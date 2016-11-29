# -*- coding: utf-8 -*-
import scrapy


class FcaSpider(scrapy.Spider):
    name = "fca"
    allowed_domains = ["register.fca.org.uk"]
    start_urls = ['http://register.fca.org.uk/']

    def parse(self, response):
        pass
