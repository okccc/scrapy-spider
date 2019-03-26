# -*- coding: utf-8 -*-
"""
scrapy模拟登录
1.直接携带cookie
2.先post登录页再get其它页
"""

import scrapy
import re


class ZHSpider01(scrapy.Spider):
    name = "zh01"
    allowed_domains = ["zhihu.com"]
    start_urls = ["https://www.zhihu.com/people/chen-qian-19-92/collections"]

    # 重写start_requests方法,自定义start_urls的请求
    def start_requests(self):
        # cookies过期时间比较久并且不需要经常访问的话可以直接携带cookie信息(不推荐)
        cookies = '_zap=4ed3bd6e-794d-4b4c-87cc-adb49c2780cf; _xsrf=cfJrgTchoVBvs9HHkGbKXn7thB7ilEow; d_c0="APAidaHjDA-PTjyLJncKLaFbA4DYavVgsEI=|1551343016"; tst=r; q_c1=c075f31f159941648223977608536cc6|1551343227000|1551343227000; __gads=ID=cee2c710f9595244:T=1553484065:S=ALNI_MYh-eOSzmu14n2gxXAF8pwapxyyAw; l_n_c=1; o_act=login; ref_source=other_; r_cap_id="ZGMyMWI3NjE4NzRlNGM2M2FkMDdiNzdhODFhYTY1NjY=|1553493705|c4120250f3585cadbe5d667821bec1eb5766b6e2"; cap_id="MTMzYzhlMmNhZDc3NGEzY2E2NDQ3ZTBjNzdjN2Y2OWY=|1553493705|27a8b014bb82b0acb5aab06ba5bb3e372317e6ef"; l_cap_id="MDY1ZWM5Yzk5MTk5NDljNzkzOWVmNzhkOTY1ZTJkNWY=|1553493705|cb44b3952524fb6980f59e52b96c544c938cae15"; n_c=1; capsion_ticket="2|1:0|10:1553493727|14:capsion_ticket|44:NTFlZmUyNzBiOTc3NGNmOGE0YmI4MzA4ZmRjMjdiOGY=|351691bb772cbfe4eecb3e4b5eff743cc886a090cf098a91d81c1fe36460edf8"; z_c0="2|1:0|10:1553493743|4:z_c0|92:Mi4xNDdBbUFBQUFBQUFBOENKMW9lTU1EeVlBQUFCZ0FsVk43cnlGWFFBbDZfR2haeDN5ZkxmTndQWXhhZXZIUGthbUR3|37524b1c41bad9a3e334485b766e00abf2e7affa6e8202c3ea4ff10c1c642188"; tgw_l7_route=7bacb9af7224ed68945ce419f4dea76d'
        cookies = {i.split("=")[0]: i.split("=")[1] for i in cookies.split("; ")}
        # 构造包含cookies参数的Request对象
        yield scrapy.Request(url=self.start_urls[0], cookies=cookies)

    def parse(self, response):
        # res = re.findall("追风少年", response.text)
        # print(res)
        print(response.url)
        res = response.xpath('//div[@class="List-item"]//a/text()').extract()
        print(res)


class ZHSpider02(scrapy.Spider):
    name = "zh02"
    allowed_domains = ["github.com"]
    start_urls = ["https://github.com/login"]

    def parse(self, response):
        # scrapy.Request只能发送get请求,scrapy.FormRequest可以发送POST请求(推荐)
        yield scrapy.FormRequest.from_response(
            response,  # 自动从response中寻找form表单
            formdata={"login": "okccc", "password": "******"},
            callback=self.parse_after,
        )

    def parse_after(self, response):
        print(re.findall("redis", response.text))
