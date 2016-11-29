# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CompanyInfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    name = scrapy.Field()
    address = scrapy.Field()
    postcode = scrapy.Field()
    phone = scrapy.Field()
    email = scrapy.Field()
    website = scrapy.Field()
    houseNumber = scrapy.Field()
    effectiveDate = scrapy.Field()
    status = scrapy.Field()