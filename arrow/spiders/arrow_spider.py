import scrapy
from string import ascii_lowercase
import math

class ArrowSpiderSpider(scrapy.Spider):
    # Syntax: scrapy crawl arrow_spider
    name = 'arrow_spider'

    custom_settings = {
        'DB_NAME': 'arrow',
        'CATEGORIES': ['SiTime', 'Semtech', 'Silicon Labs', 'NXP Semiconductors', 'Microchip Technology', 'STMicroelectronics', 'Onsemi', 'Skyworks Solutions', 'Amphenol RF','Lattice Semiconductor', 'Altera Intel Programmable', 'Allegro MicroSystems', 'MaxLinear Inc', 'Diodes Incorporated', 'Alpha and Omega Semiconductor','Amphenol', 'Molex', 'KEMET Corporation', 'TDK', 'Texas Instruments', 'Vishay', 'Micron Technology'],
        # 'CRAWLERA_ENABLED': False,
        # 'DOWNLOADER_MIDDLEWARES': ''
    }


    headers = {
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'en-US,en;q=0.9',
    }

    cookies = {
        "arrowcurrency": "isocode=USD&culture=en-US",
    }
    
    def start_requests(self):
        categories = open('arrow_categories.csv', 'r').read().split('\n')
        for category_url in categories:
            manufacturer = category_url.split('q=')[-1].split('&')[0]
            if manufacturer:
                url = f"https://www.arrow.com/productsearch/searchresultsajax?q={manufacturer}&filters=Manufacturer_name:{manufacturer};&selectedType=manufacturer&promoGroupLevel=main"
                yield scrapy.Request(url, headers=self.headers, cookies=self.cookies, callback=self.pre_parse,  meta={'uri': url})

    def pre_parse(self, response):
        print('PRE_PARSE: ', response.url)
        number_of_products = response.json()['data']['resultsMetadata']['totalResultCount']
        if number_of_products <= 10000:
            for i in range(math.ceil(number_of_products/100)+1):
                url = response.meta['uri'] + f'&page={i}&perPage=100'
                yield scrapy.Request(url, headers=self.headers, cookies=self.cookies, callback=self.parse)

        elif number_of_products <= 20000:
            for direction in ['asc', 'desc']:
                for i in range(101):
                    url = response.meta['uri'] + f'&sortBy=fullPart&sortDirection={direction}&page={i}&perPage=100'
                    yield scrapy.Request(url, headers=self.headers, cookies=self.cookies,  callback=self.parse, meta={'uri': url})
                    
        elif 'facetContainer' in response.json()['data'] and len(response.json()['data']['facetContainer']['categoryFacets']) > 1:
            for category in response.json()['data']['facetContainer']['categoryFacets']:
                url = 'https://www.arrow.com/productsearch/searchresultsajax' + category['url']
                yield scrapy.Request(url, headers=self.headers, cookies=self.cookies,  callback=self.pre_parse, meta={'uri': url})

        elif number_of_products <= 30000:
            for sortType in ['fullPart', 'calculatedQuantity', 'calculatedPrice']:
                for direction in ['asc', 'desc']:
                    for i in range(101):
                            url = response.meta['uri'] + f'&sortBy={sortType}&sortDirection={direction}&page={i}&perPage=100'
                            yield scrapy.Request(url, headers=self.headers, cookies=self.cookies,  callback=self.parse, meta={'uri': url}, dont_filter=True)
        elif 'Molex&cat=Connectors' in response.url:
            for url in ['Connector+Headers+and+PCB+Receptacles', 'Connector+Discrete+Wire+Housing', 'Connector+Terminals', 'Connector+FFC-FPC', 'Connector+Terminal+Blocks', 'Connector+Contact', 'Connector+Power', 'Connector+Backplane', 'Connector+Accessories', 'Connector+Accessories', 'Connector+Telephone+and+Telecom', 'Connector+D-Subminiature', 'Connector+RF', 'Shrink+Boot+Adapters', 'Connector+Circular', 'Connector+Rectangular', 'Connector+Socket', 'Connector+Fiber+Optics', 'Connector+USB', 'Connector+Memory+Card', 'Connector+Card+Edge', 'Connector+Audio+and+Video', 'Connector+Other', 'Connector+Interface', 'Connector+Jumpers+and+Shunts', 'Connector+Photovoltaic']:
                url = 'https://www.arrow.com/en/productsearch/searchresultsajax?q=Molex&filters=Manufacturer_name:Molex&prodLine=' + url
                yield scrapy.Request(url, headers=self.headers, cookies=self.cookies,  callback=self.pre_parse, meta={'uri': url})
        
        elif 'prodLine=Connector+Circular' in response.url:
            if 'char' not in response.meta:
                for c in ascii_lowercase+'123456789':
                    for d in ascii_lowercase+'123456789':
                        url = f'https://www.arrow.com/en/productsearch/searchresultsajax?q={c+d}&filters=Amphenol:&prodLine=Connector+Circular'
                        yield scrapy.Request(url, headers=self.headers, cookies=self.cookies,  callback=self.pre_parse, meta={'uri': url, 'char': c+d})
            else:
                for c in ascii_lowercase+'123456789':
                    url = f'https://www.arrow.com/en/productsearch/searchresultsajax?q={response.meta["char"]+c}&filters=Amphenol:&prodLine=Connector+Circular'
                    yield scrapy.Request(url, headers=self.headers, cookies=self.cookies,  callback=self.pre_parse, meta={'uri': url, 'char': response.meta["char"]+c})
        elif 'capacitor' in response.url.lower():
            for direction in ['asc', 'desc']:
                for sortBy in ['fullPart', 'calculatedPrice', 'calculatedQuantity', 'Capacitance%20Value', 'Tolerance', 'Voltage', 'Dielectric']:
                    for i in range(101):
                        url = response.meta['uri'] + f'&sortBy={sortBy}&sortDirection={direction}&page={i}&perPage=100'
                        yield scrapy.Request(url, headers=self.headers, cookies=self.cookies,  callback=self.parse, meta={'uri': url})

        elif 'resistor' in response.url.lower():
            for direction in ['asc', 'desc']:
                for sortBy in ['fullPart', 'calculatedPrice', 'calculatedQuantity', 'Resistance%20Value%20-%20(Ohm)', 'Tolerance', 'Current%20Sensing', 'Power%20Rating%20-%20(W)', 'Technology', 'Operating%20Temperature%20-%20(°C)']:
                    for i in range(101):
                        url = response.meta['uri'] + f'&sortBy={sortBy}&sortDirection={direction}&page={i}&perPage=100'
                        yield scrapy.Request(url, headers=self.headers, cookies=self.cookies,  callback=self.parse, meta={'uri': url})

        
        else:
            print('Ending', response.url)
        
    def parse(self, response):
        if 'results' not in response.json()['data']:
            return
        products = response.json()['data']['results']
        for product in products:
            data = {
                'Part URL': 'https://www.arrow.com' + product['partUrl'],
                'Part no.': product['partNumber'],
                'Price': '',
                'Stock': '',
                'Manufacturer': product['manufacturer'],
                'Product Category': product['category']
            }

            if product['groupedBuyingOptions']['regionalBuyingOptions']:
                if product['groupedBuyingOptions']['regionalBuyingOptions'][0]['buyingOptions']:
                    data['Stock'] = product['groupedBuyingOptions']['regionalBuyingOptions'][0]['buyingOptions'][0]['quantity']

                    if product['groupedBuyingOptions']['regionalBuyingOptions'][0]['buyingOptions'][0]['priceBands']:
                        data['Price'] = product['groupedBuyingOptions']['regionalBuyingOptions'][0]['buyingOptions'][0]['priceBands'][0]['price']
            yield(data)