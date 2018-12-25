# -*- coding: utf-8 -*-
"""
需求：抓取房天下网站各个城市的新房和二手房房价信息
思路：
1、先获取所有城市链接
http://www.fang.com/SoufunFamily.htm
2、再获取每个城市新房/二手房链接
上海：http://sh.fang.com/
     http://sh.newhouse.fang.com/house/s/
     http://sh.esf.fang.com/
无锡：http://wuxi.fang.com/
     http://wuxi.newhouse.fang.com/house/s/
     http://wuxi.esf.fang.com/
北京：http://bj.fang.com/
     http://newhouse.fang.com/house/s/
     http://esf.fang.com/

在linux部署工程：
pip freeze > requirements.txt
在virtualenv安装环境：pip install requirements.txt

问题：xpath()获取不到数据,返回的是空[]
原因：Scrapy爬虫看到的页面结构与我们自己在浏览器看到的可能并不一样(比如某个页面元素的id或者class不一样,甚至元素名字也不一样)
解决：使用scrapy shell测试 --> 通过view(response)命令来看看scrapy爬虫所看到的页面具体长啥样(可以在弹出的浏览器中检查元素)
"""

import scrapy
import re
from scrapyspider.items import NewHouseItem, EsfHouseItem, EsfHouseItem02
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapyspider.utils.common import get_md5
from scrapyspider.items import MyItemLoader


class scrapyspider(scrapy.Spider):
    # 爬虫名称
    name = 'soufang'
    # 域名范围
    allowed_domains = ['fang.com']
    # 起始页面
    start_urls = ['http://www.fang.com/SoufunFamily.htm']

    # scrapy默认只处理200<=response.status<300的url;现在想统计404页面数量,将404添加到http状态码请求列表
    handle_httpstatus_list = [404]  # 见源码-->scrapy.spidermiddlewares.httperror

    def __init__(self):
        super().__init__()
        self.failed_urls = []

        # 分发器做信号映射：当signals.spider_closed信号发生时调用stats.set_value()函数
        dispatcher.connect(receiver=self.spider_closed, signal=signals.spider_closed)

    # 关闭spider时的逻辑处理
    def spider_closed(self):
        # 给统计数据stats设置key/value
        self.crawler.stats.set_value("failed_urls_detail", ",".join(self.failed_urls))

    # 解析页面
    def parse(self, response):
        if response.status == 404:
            # 将404页面添加到错误url列表
            self.failed_urls.append(response.url)
            # 统计数据stats +1
            self.crawler.stats.inc_value("failed_urls_num")  # failed_urls这一参数会在爬虫结束时的数据统计中出现

        province = None
        # 获取表格所有行
        trs = response.xpath('//div[@class="outCont"]//tr')
        # 遍历所有行
        for tr in trs:
            # 获取省份名称(去空格)
            province_text = re.sub("\s", "", tr.xpath('./td[2]//text()').extract()[0])
            # 判断省份值是否为空字符串：不是""就赋值,是""就不赋值(此时province还是之前的值),如此循环直到有新的值覆盖 -->参考：basic-->类型和变量-->test()
            if province_text:
                province = province_text
            # 海外城市数据不需要
            if province == "其它":
                continue
            # 获取所有城市行
            citys = tr.xpath('./td[3]//a')
            for each in citys:
                # 城市名称
                city = each.xpath('./text()').extract()[0]
                # 该城市链接
                link = each.xpath('./@href').extract()[0]
                pinyin = link.split("//")[1].split(".")[0]
                # 北京比较特殊
                if pinyin == "bj":
                    new_link = "http://newhouse.fang.com/house/s/"
                    esf_link = "http://esf.fang.com/"
                else:
                    # 该城市新房链接
                    new_link = "http://" + pinyin + ".newhouse.fang.com/house/s/"
                    # 该城市二手房链接
                    esf_link = "http://" + pinyin + ".esf.fang.com/"
                print(esf_link)
                # 发送新的请求链接(meta参数用于在不同请求之间传递数据,dict类型)
                yield scrapy.Request(url=new_link, callback=self.parse_new, meta={"info": (province, city)})
                # yield scrapy.Request(url=esf_link, callback=self.parse_esf, meta={"info": (province, city)})
                break
            break

    # 解析新房数据
    def parse_new(self, response):
        # 接收request请求传递过来meta参数信息
        province, city = response.meta.get("info")
        # 获取当前页面小区列表
        communitys = response.xpath('//div[@class="nlc_details"]')
        # 遍历所有小区
        for each in communitys:
            # 过滤已售完房源
            if each.xpath('.//div[contains(@class, "fangyuan")]/span/text()').get() == "售完":
                continue
            # 使用ItemLoader填充item数据(根据具体情况接收selector/response)
            loader = MyItemLoader(item=NewHouseItem(), selector=each)
            loader.add_value('id', get_md5())
            loader.add_value('province', province)
            loader.add_value('city', city)
            loader.add_xpath('community', './/div[@class="nlcd_name"]/a/text()')
            loader.add_xpath('url', './/div[@class="nlcd_name"]/a/@href')
            loader.add_xpath('price', './/div[@class="nhouse_price"]')
            loader.add_xpath('area', './/div[contains(@class, "house_type")]')
            loader.add_xpath('district', './/div[@class="address"]/a')
            loader.add_xpath('address', './/div[@class="address"]/a/@title')
            loader.add_xpath('sale', './/div[contains(@class, "fangyuan")]/span/text()')
            item = loader.load_item()
            yield item

        # 获取当前页码和尾页页码
        current_page = response.xpath('//div[@class="page"]//a[@class="active"]/text()').get()
        last_page = response.xpath('//div[@class="page"]//a[last()]/text()').get()
        # 判断是否到尾页
        if last_page == "尾页":
            # 获取新页面链接
            if current_page == "1":
                next_page = response.url + "b92"
            else:
                next_page = "/".join(response.url.split("/")[:-2]) + "/" + response.url.split("/")[-2][0:2] + str(
                    int(response.url.split("/")[-2][2:]) + 1)
            # 继续发送新的请求
            yield scrapy.Request(url=next_page, callback=self.parse_new, meta={"info": (province, city)})

    # 解析二手房首页数据
    def parse_esf(self, response):
        # 接收request请求传递过来的meta参数信息
        province, city = response.meta.get("info")
        # 获取当前页面房源列表
        houses = response.xpath('//div[@class="houseList"]/dl')
        # 遍历所有房源
        for each in houses:
            # 使用ItemLoader填充item数据(根据具体情况接收response/selector)
            loader = MyItemLoader(item=EsfHouseItem(), selector=each)
            loader.add_value('province', province)
            loader.add_value('city', city)
            loader.add_xpath('community', './/p[@class="mt10"]/a/span/text()')
            loader.add_xpath('title', './/p[@class="title"]/a/text()')
            loader.add_xpath('address', './/p[@class="mt10"]/span/text()')
            loader.add_xpath('rooms', './/p[@class="mt12"]')
            loader.add_xpath('floor', './/p[@class="mt12"]')
            loader.add_xpath('toward', './/p[@class="mt12"]')
            loader.add_xpath('year', './/p[@class="mt12"]')
            loader.add_xpath('area', './/div[contains(@class, "area")]')
            loader.add_xpath('price', './/p[@class="mt5 alignR"]')
            loader.add_xpath('unit', './/p[contains(@class, "danjia")]')
            item = loader.load_item()
            yield item

        # 判断是否有下一页
        next_url = response.xpath('//a[@id="PageControl1_hlk_next"]/@href').get()
        # 继续发送新的请求
        if next_url:
            # 这个网站做的很刁钻：二手房首页和其他页的页面展示还不一样,需调用新的函数解析
            yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_esf02, meta={"info": (province, city)})

    # 解析二手房非首页数据
    def parse_esf02(self, response):
        # 接收request请求传递过来的meta参数信息
        province, city = response.meta.get("info")
        # 获取当前页面房源列表
        houses = response.xpath('//div[contains(@class, "shop_list")]/dl')
        for each in houses:
            # 使用ItemLoader填充item数据(根据具体情况接收response/selector)
            loader = MyItemLoader(item=EsfHouseItem02(), selector=each)
            loader.add_value('province', province)
            loader.add_value('city', city)
            loader.add_xpath('community', './/p[@class="add_shop"]/a/@title')
            loader.add_xpath('title', './/span[@class="tit_shop"]/text()')
            loader.add_xpath('address', './/p[@class="add_shop"]/span/text()')
            loader.add_xpath('rooms', './/p[@class="tel_shop"]')
            loader.add_xpath('area', './/p[@class="tel_shop"]')
            loader.add_xpath('floor', './/p[@class="tel_shop"]')
            loader.add_xpath('toward', './/p[@class="tel_shop"]')
            loader.add_xpath('year', './/p[@class="tel_shop"]')
            loader.add_xpath('price', './/dd[@class="price_right"]/span[1]')
            loader.add_xpath('unit', './/dd[@class="price_right"]/span[2]')
            item = loader.load_item()
            yield item

        # 判断是否有下一页
        next_url = response.xpath('//div[@class="page_al"]/p[3]/a/@href').get()
        # 继续发送新的请求
        if next_url:
            yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_esf02, meta={"info": (province, city)})
