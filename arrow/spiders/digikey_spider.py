from scrapy import Request, Spider, Item
import re
from random import randint
import csv
from scrapy import Field

class DigikeyItem(Item):
    PartURL = Field()
    PartNo = Field()
    Price = Field()
    Stock = Field()
    Manufacturer = Field()
    ProductCategory = Field()    
    pass

class digikey(Spider):
    name = 'digikey' #name of your spider. scrapy crawl spider_name
    base_url  = 'https://www.digikey.com'
    user_agents = [
        'Mozilla/5.0 (X11; CrOS x86_64 10066.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:70.0) Gecko/20100101 Firefox/70.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:70.0) Gecko/20100101 Firefox/70.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.100.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/604.1 Edg/100.0.100.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19042',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19042',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36 OPR/65.0.3467.48',
        'Mozilla/5.0 (X11; CrOS x86_64 10066.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }

    custom_settings = {
        'DB_NAME': 'digikey',
        'CATEGORIES': ['Amphenol LTW', 'Amphenol Wilcoxon Sensing Technologies', 'Amphenol Anytek', 'Amphenol Times Microwave Systems', 'Amphenol ICC (FCI)', 'Amphenol Spectra-Strip', 'Amphenol Socapex', 'Amphenol Aerospace Operations', 'Amphenol ICC (Commercial Products)', 'Amphenol NEXUS Technologies', 'Amphenol PCD', 'Amphenol Audio', 'Amphenol Sine Systems Corp', 'Amphenol RF', 'Amphenol Interconnect India', 'Amphenol Industrial Operations', 'Amphenol Tuchel Industrial', 'Amphenol Air LB', 'Amphenol Alden Products Company'],
    }

    def __init__(self):
        super(digikey, self).__init__()
        self.start = 0

    def rotate_headers(self):
        self.headers['User-Agent'] = self.user_agents[randint(0,len(self.user_agents)-1)]

    def start_requests(self):
        for link in csv.reader(open('digikey_prods.csv', 'r')):
            if link[0] == 'links':
                continue
            self.rotate_headers()
            yield Request(link[0],callback=self.product_information,headers=self.headers)

    def product_information(self,response):
        na = ''
        try:
            Manufacturer = response.xpath('//td[div[contains(text(),"Manufacturer")]]/following-sibling::td')[0].xpath('.//text()').get()
        except:
            Manufacturer = na
        try:
            PartNo = response.xpath('//td[div[contains(text(),"Digi-Key Part Number")]]/following-sibling::td')[0].xpath('.//text()').get()
        except:
            PartNo = na
        try:
            Price = response.xpath('//span[contains(@data-testid,"pricing-group")]/table/tbody/tr//text()')[1].get().strip('$')
        except:
            Price = na
        try:
            category = ' '.join(response.xpath('//td[div[contains(text(),"Category")]]/following-sibling::td')[0].xpath('.//text()').extract())
        except:
            category = na
        try:
            stock = re.findall(r'\d+',response.xpath('//script[contains(text(),"browser")]/text()').get().split('messages')[-1].split('In Stock')[0])[0]
        except:
            stock = na

        data = {
            'Part URL': response.url,
            'Part no.': PartNo,
            'Price': Price,
            'Stock': stock,
            'Manufacturer': Manufacturer,
            'Product Category': category
        }

        yield data