# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import sqlite3
import json
import gspread
import datetime
from apiclient import discovery # pip install --upgrade google-api-python-client
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import json
import time

class SQLITE_Pipeline(object):
    CONNECTION = ''
    google = gspread.service_account(filename = 'credentials.json')
    indexes = []
    WORKSHEET = ''
    current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    sheets = []
    completed = []
    previously = []
    
    def create_table(self, spider_name):
        cursor = self.CONNECTION.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {spider_name}
            (
                part_url TEXT,
                part_no PRIMARY KEY,
                price FLOAT,
                stock INT,
                manufacturer TEXT,
                category TEXT
            );
        ''')
    
    def create_worksheet(self, spider_name):
        creds = json.loads(open('credentials.json').read())
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        drive_service = discovery.build('drive', 'v3', credentials=credentials)
        file_metadata = {
            'name': self.WORKSHEET,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': ['1_PAhxNPZ1bZ0mYfuu0GcaEM7ThaYjeRy'],
        }
        drive_service.files().create(body=file_metadata).execute()

        gc = self.google.open(self.WORKSHEET)
        for sheet in self.indexes:
            worksheet = gc.add_worksheet(title=sheet, rows="60000", cols="7")
            while True:
                try:
                    worksheet.append_rows([['Date', 'Product Name', 'Product Link', 'Current Price', 'Price Change', 'Current Stock #', 'Stock Change']], table_range='A1')
                    break
                except Exception as err:
                    print(err)
                    time.sleep(1)
            self.sheets.append([sheet, gc.worksheet(sheet), []])
        gc.del_worksheet(gc.worksheet('Sheet1'))

        try:
            prev_data = list(self.CONNECTION.cursor().execute(f'SELECT * FROM {spider_name}'))
        except:
            prev_data = []

        self.previously = {}
        for data in prev_data:
            try:
                self.previously[data[4]].append(data)
            except:
                self.previously[data[4]] = [data]

    def process_item(self, item, spider):
        if not self.CONNECTION:
            DB_FILE_NAME = spider.settings.get("DB_NAME")
            self.indexes = spider.settings.get("CATEGORIES")
            self.WORKSHEET = spider.name + '_' + datetime.datetime.now().strftime('%Y%m%d')
            self.CONNECTION = sqlite3.connect(DB_FILE_NAME+'.db')
            self.create_table(spider.name)
            self.create_worksheet(spider.name)

        if item['Part no.'] not in self.completed:
            self.completed.append(item['Part no.'])
            self.store_db(item, spider.name)
            return item

    def store_db(self, item, spider_name):
        cursor = self.CONNECTION.cursor()

        for cell in item:
            if isinstance(item[cell], str):
                item[cell] = item[cell].replace("'", "''")

        try:
            if isinstance(item['Price'], str):
                item['Price'] = item['Price'].replace(',', '')
            item['Price'] = float(item['Price']) if item['Price'] else 0
            cursor.execute(f"""INSERT INTO {spider_name} VALUES (
                '{item['Part URL']}',
                '{item['Part no.']}',
                {item["Price"] if item["Price"] else 0},
                {item["Stock"] if item["Stock"] else 0},
                '{item["Manufacturer"]}',
                '{item["Product Category"]}'
                )
            """)
            print('OKEY!')
        except Exception as err:
            try:
                old_record = [(a, b, c, d, e, f) for a, b, c, d, e, f in self.previously[item['Manufacturer']] if b  == item['Part no.']]
                stock_change = price_change = 0
                if not item['Price']:
                    item['Price'] = 0
                if not item['Stock']:
                    item['Stock'] = 0
                if old_record:
                    self.previously[item['Manufacturer']].remove(old_record[0])
                    if item['Price'] and old_record[0][2]:
                        try:
                            price_change = float(item['Price']) - float(old_record[0][2])
                        except:
                            price_change = float(item['Price'].replace(',', '')) - float(old_record[0][2].replace(',', ''))
                    if item['Stock'] and old_record[0][3]:
                        stock_change = int(item['Stock']) - int(old_record[0][3])

                if price_change or stock_change:
                    if item['Manufacturer'] in self.indexes:
                        sheet_index = self.indexes.index(item['Manufacturer'])
                        ITEM = [self.current_time, item['Part no.'], item['Part URL'], item['Price'], price_change, item['Stock'], stock_change]
                        self.sheets[sheet_index][2].append(ITEM)
                        if len(self.sheets[sheet_index][2]) >= 10:
                            sheet = self.sheets[sheet_index][1]
                            for i in range(5):
                                try:
                                    sheet.append_rows(self.sheets[sheet_index][2], table_range='A2')
                                    self.sheets[sheet_index][2] = []
                                    break
                                except Exception:
                                    time.sleep(5)
                                    pass
                    
                    if isinstance(item['Price'], str):
                        item['Price'] = item['Price'].replace(',', '')
                    item['Price'] = float(item['Price'])
                    cursor.execute(f"""UPDATE {spider_name}
                                    SET price = {item["Price"]}, stock = {item["Stock"]}
                                    WHERE part_no = '{item["Part no."]}';
                                    """)
            except Exception as err:
                print(err)
        self.CONNECTION.commit()

    def close_spider(self, spider):
        for sheet in self.sheets:
            data = sheet[2]
            if len(data):
                gc_sheet = sheet[1]
                try:
                    gc_sheet.append_rows(data, table_range='A2')
                except Exception as err:
                    print(err)
                    pass