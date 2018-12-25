# -*- coding: utf-8 -*-
"""
AttributeError: 'str' object has no attribute 'iter'
原因：restrict_xpaths (str or list) – is a XPath (or list of XPath’s) which defines regions inside the response where links should be extracted from.
翻译：restrict_xpaths (str或lis) - 是一个XPath(或XPath的列表),它定义了应该从中提取链接的响应内的 区域(黑体加粗)
解释：restrict_xpaths应指向元素-->直接链接或包含链接的容器,而不是属性
"""

import scrapy
from scrapyspider.items import HospitalItem, DoctorItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import time


class SoyoungSpider(CrawlSpider):
    name = 'soyoung'
    allowed_domains = ['y.soyoung.com']

    start_urls = [
        'http://y.soyoung.com/hospital',
        'http://y.soyoung.com/doctor',
    ]

    # def start_requests(self):
    #     yield scrapy.Request("http://y.soyoung.com/hospital", callback=self.parse_hospital),
    #     # yield scrapy.Request("http://y.soyoung.com/doctor", callback=self.parse_doctor),

    rules = (
        Rule(LinkExtractor(allow='/hospital/index/page/\d+'), callback='parse_hospital', follow=True),
        Rule(LinkExtractor(allow='/doctor/index/page/\d+'), callback='parse_doctor', follow=True),
        # Rule(LinkExtractor(restrict_xpaths='//li[contains(@onclick, "window.open")]/a[@class="pic"]'), callback='parse_doctor'),
    )

    def parse_hospital(self, response):
        item = HospitalItem()
        hospitals = response.xpath('//li[@onclick]')
        for each in hospitals:
            id = each.xpath('./a/@href').extract()[0][1:]
            name = each.xpath('./a/@title').extract()[0]
            aptitude = each.xpath('.//p[1]/text()').extract()[0]
            address_list = each.xpath('.//p[2]/text()').extract()
            if len(address_list) == 0:
                address = ""
            else:
                address = "".join(address_list[0].split())
            skilled_list = each.xpath('.//p[3]/a/text()').extract()
            if len(skilled_list) == 0:
                skilled = ""
            else:
                skilled = ",".join("".join(skilled_list).split())

            item['id'] = id
            item['name'] = name
            item['aptitude'] = aptitude
            item['address'] = address
            item['skilled'] = skilled
            item['insert_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            yield item

    def parse_doctor(self, response):
        item = DoctorItem()
        doctors = response.xpath('//li[@onclick]')
        for each in doctors:
            id = each.xpath('./a/@href').extract()[0][1:]
            name = each.xpath('./a/@title').extract()[0]
            hospital_id = each.xpath('.//p[1]/a/@href').extract()[0][1:]
            hospital_names = each.xpath('.//p[1]/a/@title').extract()
            if len(hospital_names) == 0:
                hospital_name = ""
            else:
                hospital_name = hospital_names[0]
            titles = each.xpath('.//p[2]/text()').extract()
            if len(titles) == 0:
                title = ""
            else:
                title = titles[0]
            skilleds = each.xpath('.//p[3]/a/text()').extract()
            if len(skilleds) == 0:
                skilled = ""
            else:
                skilled = skilleds[0]
            insert_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            item['id'] = id
            item['name'] = name
            item['hospital_id'] = hospital_id
            item['hospital_name'] = hospital_name
            item['title'] = title
            item['skilled'] = skilled
            item['insert_time'] = insert_time

            yield item



