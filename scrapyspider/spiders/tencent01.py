# -*- coding: utf-8 -*-
"""
Spider类:
    class scrapy.Spider是最基本的类,所有编写的爬虫必须继承这个类,其定义了如何爬取某个(或某些)网站
    包括爬取动作(例如:是否跟进链接)以及如何从网页的内容中提取结构化数据(item字段)

主要函数及调用顺序：
__init__():
    初始化爬虫名字和start_urls列表
start_requests():
    调用make_requests_from_url()方法,生成Requests对象交给Scrapy下载并返回response
parse():
    解析response,并返回Item或Requests(需指定回调函数);Item传给Item pipline持久化
    Requests交由Scrapy下载,并由指定的回调函数处理(默认parse()),一直循环直到处理完所有的数据为止;

主要属性和方法
name:
    定义spider名字,比如爬取mywebsite.com,该spider通常会被命名为mywebsite,具有唯一性
allowed_domains:
    包含了spider允许爬取的域名(domain)的列表,可选
start_urls:
    初始URL元组/列表,当没有指定特定URL时,spider将从该列表中开始爬取
start_requests(self):
    当spider启动爬取并且未指定start_urls时才会调用该方法,生成request对象调用scrapy解析并返回response
parse(self, response):
    默认的Request对象回调函数,用来处理网页返回的response信息,生成Item或者新的Request对象

parse()方法工作机制：
1、方法结尾是yield而不是return,parse()方法将会被当做一个生成器使用;scrapy会逐一获取parse方法中生成的结果并判断类型
  如果是request就加入爬取队列,是item类型就使用pipeline处理,其他类型则返回错误信息
2、scrapy取到新的request并不会立马发送,而是先将其放入队列,然后接着从生成器里获取,直到取尽第一部分的request
  然后再获取第二部分的item,取到item了,就会放到对应的pipeline处理
3、parse()方法作为回调函数(callback)赋值给了Request,指定parse()方法来处理这些请求scrapy.Request(url, callback=self.parse)
4、Request对象经过调度,执行生成 scrapy.http.response()的响应对象,并送回给parse()方法,直到调度器中没有Request(递归)
  取尽之后,parse()工作结束,引擎再根据队列和pipelines中的内容去执行相应的操作
5、程序在取得各个页面的items前,会先处理完之前所有的request队列里的请求,然后再提取items
"""

import scrapy
from scrapyspider.items import TencentspiderItem


class TencentSpider(scrapy.Spider):
    """
    基于Spider类的爬虫：需要手动刷新url(更安全: 可以避免反爬虫故意篡改url的问题)
    """

    # 爬虫名称
    name = "tencent01"
    # 域名
    allowed_domains = ["tencent.com"]
    # 起始url
    url = "http://hr.tencent.com/position.php?&start="
    offset = 0
    start_urls = [url + str(offset)]

    def parse(self, response):
        # 创建Item对象
        item = TencentspiderItem()

        # 获取当前页职位信息列表
        positions = response.xpath("//tr[@class='even'] | //tr[@class='odd']")
        # 遍历所有职位
        for each in positions:
            # 职位名称
            name = each.xpath("./td[1]/a/text()").extract()[0]
            # 详细链接
            detailLink = each.xpath("./td[1]/a/@href").extract()[0]
            # 职位类别
            sort_list = each.xpath("./td[2]/text()").extract()
            if len(sort_list) == 0:
                sort = ""
            else:
                sort = sort_list[0]
            # 招聘人数
            num = each.xpath("./td[3]/text()").extract()[0]
            # 上班地点
            site = each.xpath("./td[4]/text()").extract()[0]
            # 发布时间
            publishTime = each.xpath("./td[5]/text()").extract()[0]

            item['name'] = name
            item['detailLink'] = detailLink
            item['sort'] = sort
            item['num'] = num
            item['site'] = site
            item['publishTime'] = publishTime

            # 将数据交给pipeline处理
            yield item

        # 爬完第一页继续往后翻
        if self.offset < 100:
            self.offset += 10
            # 向新的页面发起请求并调用self.parse处理response
            yield scrapy.Request(self.url + str(self.offset), callback=self.parse)


