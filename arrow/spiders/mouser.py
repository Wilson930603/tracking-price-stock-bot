import scrapy

class MouserpiderSpider(scrapy.Spider):
    # Syntax: scrapy crawl mouser
    name = 'mouser'
    custom_settings = {
        'DB_NAME': 'mouser',
        'CATEGORIES': ['amphenol', 'broadcom', 'cirrus-logic', 'diodes-inc', 'dialog-semiconductor', 'finisar', 'infineon', 'intersil', 'keysight', 'kemet-electronics', 'marvell-semiconductor', 'maxim-integrated', 'microchip', 'molex', 'monolithicpowersystems', 'murata', 'nordic-semiconductor', 'nxp-semiconductors', 'onsemi', 'power-integrations', 'renesas', 'sandisk', 'semtech', 'seoulsemiconductor', 'sitime', 'stmicroelectronics', 'texas-instruments', 'toshiba-semiconductors', 'vishay'],
    }
    headers = {
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'en-US,en;q=0.9',
        'Cookie': 'preferences=NCM=1&pl=en-GB&pc_eu=USDe;',
    }

    def start_requests(self):
        manufacturers = open('mouser_categories.csv', 'r').read().split('\n')
        for manufacturer in manufacturers:
            url = 'https://eu.mouser.com/c/?q=' + manufacturer
            yield scrapy.Request(url, headers=self.headers, meta={'m': manufacturer}, callback=self.parse_categories)

    def parse_categories(self, response):
        if 'An unexpected error has occurred.' in response.text:
            yield scrapy.Request(response.url, headers=self.headers, meta=response.meta, callback=self.parse_categories)

        try:
            size = int(response.xpath('//span[@class="searchResultsCount total-results-value"]/text()').get().replace('(', '').replace(')', ''))
            if size <= 1250:
                yield scrapy.Request(response.url, headers=self.headers, meta={'m': response.meta['m'], 'subcat': ''}, callback=self.parse_products, dont_filter=True)
                return
        except:
            pass

        for sub_category in response.xpath('//div[@class="div-cat-title"]'):
            url = 'https://eu.mouser.com' + sub_category.xpath('.//a/@href').get()
            name = sub_category.xpath('.//a/text()').get().strip()
            yield scrapy.Request(url, headers=self.headers, meta={'m': response.meta['m'], 'subcat': name}, callback=self.parse_attributes)

    def parse_attributes(self, response):
        if 'An unexpected error has occurred.' in response.text:
            yield scrapy.Request(response.url, headers=self.headers, meta=response.meta, callback=self.parse_attributes)

        if 'ProductDetail' in response.url:
            yield scrapy.Request(response.url, headers=self.headers, meta={'m': response.meta['m'], 'subcat': response.meta['subcat']}, callback=self.parse_products, dont_filter=True)
            return
        try:
            size = int(response.xpath('//span[@id="lblreccount"]/text()').get().replace('.', '')) if response.xpath('//span[@id="lblreccount"]/text()') else int(response.xpath('//span[@class="record-count-lbl"]/text()').get())
            if size <= 1250:
                yield scrapy.Request(response.url, headers=self.headers, meta={'m': response.meta['m'], 'subcat': response.meta['subcat']}, callback=self.parse_products, dont_filter=True)
                return
        except:
            pass

        for attribute in response.xpath('//td[@class="attr-grp"]'):
            name = attribute.xpath('.//input/@value')[2].get()
            values = attribute.xpath('.//select/option/text()').getall()
            for value in values:
                url = response.url + f'&{name}={value}'
                yield scrapy.Request(url, headers=self.headers, meta={'m': response.meta['m'], 'subcat': response.meta['subcat']}, callback=self.parse_products)
    
    def parse_products(self, response):
        if 'An unexpected error has occurred.' in response.text:
            yield scrapy.Request(response.url, headers=self.headers, meta=response.meta, callback=self.parse_products)

        for product in response.xpath('//tr[@data-partnumber]'):
            data = {
                'Part URL': 'https://eu.mouser.com' + product.xpath('.//a/@href').get(),
                'Part no.': product.xpath('.//@data-partnumber').get(),
                'Price': '',
                'Stock': '',
                'Manufacturer': response.meta['m'],
                'Product Category': response.meta['subcat']
            }
            try:
                data['Stock'] = int(product.xpath('.//span[@class="available-amount"]/text()').get().replace('.', ''))
            except:
                data['Stock'] = 0
            
            try:
                data['Price'] = float(product.xpath('.//span[contains(@id, "lblPrice_")]/text()').get().split(' ')[0].replace(',', '.'))
            except:
                data['Price'] = ''

            yield(data)        
        if response.xpath('//a[@id="lnkPager_lnkNext"]'):
            url = response.xpath('//a[@id="lnkPager_lnkNext"]/@href').get()
            yield scrapy.Request(url, headers=self.headers, meta=response.meta, callback=self.parse_products)