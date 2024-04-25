# Arrow Scraper

## Description
This scrapy project scrapes products data from a list of manufacturers in arrow.com website, and track the change in price/stock in a google worksheet

# Pre Requisites
- Installing required libraries (use the command: `pip install -r requirements.txt`)
- Enable Google Drive & Google Spreadsheet API from https://console.developers.google.com/
- Update `credentials.json` with valid credentials.
- Make sure there is a folder called `ARROW` in Google Drive where worksheets will be created and stored.

# Usage
- Add categories to `categories.csv` file in first column.
    Links should look like this: https://www.arrow.com/en/products/search?q=Molex&filters=Manufacturer_name:Molex;&selectedType=manufacturer
    where "Molex" is the manufacturer name.

For one time usage:
- Run the command:
    `scrapy crawl arrow_spider`

# Schedule Usage
Update the file `run_schedule.py` with date and time of when you want the scraper to run. (Default: Saturday at 5:15)
To run the script everyday, add 'mon,tue,wed,thu,fri,sat,sun' to the variable ON_DAYS
To run the script once a day, add 'mon' or 'tue' or.... to the variable ON_DAYS

For scheduled usage:
- Run the command:
    `python run_schedule.py`

# Dataset
Data is stored in SQLITE file 'arrow.db', whereas price and quantity tracking are posted to google spreadsheet.