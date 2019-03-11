# -*- coding: utf-8 -*-
import scrapy


class DemoSpider(scrapy.Spider):
    name = 'demo'
    #allowed_domains = ['scrapydemo.test']
    start_urls = ['http://scrapydemo.test/']

    def parse(self, response):
        pass
