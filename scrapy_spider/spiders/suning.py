# -*- coding: utf-8 -*-

import scrapy


class SuningSpider(scrapy.Spider):

    # 爬虫名称
    name = "suning"
    # 爬取范围
    allowed_domains = [""]
    # 初始url,不会被allowed_domains过滤
    start_urls = [""]

    def parse(self, response):
        pass
