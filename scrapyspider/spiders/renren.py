# -*- coding: utf-8 -*-
"""
模拟登陆人人网：需要重写start_requests()方法发送post请求,scrapy发送post请求需要使用scrapy.FormRequest()方法
"""

import scrapy


class RenrenSpider(scrapy.Spider):
    name = 'renren'
    allowed_domains = ['www.renren.com']

    def start_requests(self):
        # 登录页面
        url = "http://www.renren.com/PLogin.do"
        # 发送post请求
        yield scrapy.FormRequest(
            url,
            formdata={"email": "123456789@qq.com", "password": "hehexixihaha"},
            callback=self.parse
        )

    def parse(self, response):
        with open("my.html", "w", encoding="utf8") as f:
            f.write(response.text)
