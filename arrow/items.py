# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class ArrowItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class DigikeyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    PartURL = Field()
    PartNo = Field()
    Price = Field()
    Stock = Field()
    Manufacturer = Field()
    ProductCategory = Field()    
    pass
