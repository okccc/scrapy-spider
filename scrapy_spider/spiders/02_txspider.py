# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy_spider.items import TXItem


class TXSpider01(scrapy.Spider):
    """
    该网站是html动态加载,F12-->Network-->Headers抓请求接口
    """

    # 爬虫名称
    name = "tx"
    # 爬取范围(可选)
    allowed_domains = ["tencent.com"]
    # url列表
    start_urls = ["https://careers.tencent.com/tencentcareer/api/post/Query?pageIndex={}&pageSize=10".format(i) for i in range(1, 343)]

    # 注意：parse()方法名是固定的,继承的父类未实现的方法
    def parse(self, response):
        # 创建Item对象
        item = TXItem()
        # 解析json数据
        dict_data = json.loads(response.text)
        positions = dict_data["Data"]["Posts"]
        for position in positions:
            item["title"] = position["RecruitPostName"]
            item["link"] = position["PostURL"]
            item["category"] = position["CategoryName"]
            item["location"] = position["LocationName"]
            item["responsibility"] = position["Responsibility"]
            item["update_time"] = position["LastUpdateTime"]
            yield item



