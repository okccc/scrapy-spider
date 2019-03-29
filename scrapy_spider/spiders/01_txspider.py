# -*- coding: utf-8 -*-
"""
Spider类：所有爬虫的基类,默认parse()函数解析,只爬取start_urls列表中的页面,需要手动翻页
1.__init__()：初始化爬虫名name和start_urls列表
2.start_requests()：调用make_requests_from_url()方法,将start_urls中的url生成request对象交给scrapy下载并返回response
3.parse()：解析response,返回Item(交给ItemPipeline持久化)或者Request对象(放入爬取队列交给scrapy继续下载)

CrawlSpider类: 需要自定义parse_item()函数解析,定义一些rule来提供跟进link的机制从爬取的网页中获取新的link并继续爬取
LinkExtractor(
    allow = (),                 # 满足括号中'正则表达式'的值会被提取,如果为空就全部匹配(常用)
    deny = (),                  # 与这个正则表达式不匹配的URL一定不提取,优先级高于allow
    allow_domains = (),         # 会被提取的链接的domains(常用)
    deny_domains = (),          # 一定不会被提取链接的domains
    restrict_xpaths = (),       # 使用xpath表达式,和allow共同作用过滤链接
)
Rule(
    link_extractor,             # 是一个LinkExtractor对象,定义需要提取的链接
    callback = None,            # 匹配的链接需要提取数据时才会指定callback(比如数据都在详情页,新匹配的列表页就不需要指定callback)
    follow = None,              # 是否循环跟进页面中符合allow匹配规则的链接
    process_links = None,       # 过滤从link_extractor中提取的link(有些反爬虫会故意响应错误链接)
    process_request = None      # 过滤request
)
"""

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_spider.items import TXItem


class TXSpider01(scrapy.Spider):
    """
    基于Spider类的爬虫：需要手动刷新url(更安全,有些网站翻页时url不变是通过js生成的,需要破解对应的js)
    """

    # 爬虫名称
    name = "tx01"
    # 爬取范围(可选)
    allowed_domains = ["tencent.com"]
    # 初始url,不会被allowed_domains过滤
    start_urls = ["http://hr.tencent.com/position.php?&start="]

    # 注意：parse()方法名是固定的,继承的父类未实现的方法
    def parse(self, response):
        """
        在parse方法之前start_requests方法会先请求start_urls返回response交给parse解析
        """

        # 获取当前页职位信息列表
        tr_list = response.xpath("//tr[@class='even'] | //tr[@class='odd']")
        # 遍历所有职位
        for tr in tr_list:
            # 创建Item对象
            item = TXItem()
            # 职位名称
            name = tr.xpath("./td[1]/a/text()").extract_first()
            # 详细链接
            link = "https://hr.tencent.com/" + tr.xpath("./td[1]/a/@href").extract_first()
            # 职位类别
            sort = tr.xpath("./td[2]/text()").extract_first()
            # 招聘人数
            num = tr.xpath("./td[3]/text()").extract_first()
            # 上班地点
            site = tr.xpath("./td[4]/text()").extract_first()
            # 发布时间
            publish = tr.xpath("./td[5]/text()").extract_first()
            item['name'] = name
            item['link'] = link
            item['sort'] = sort
            item['num'] = num
            item['site'] = site
            item['publish'] = publish
            # yield可以减少内存占用,yield只能接Request/BaseItem/dict/None
            yield item
        # 判断下一页
        next_page = "http://hr.tencent.com/" + response.xpath('//a[@id="next"]/@href').extract_first()
        if next_page != "javascript:;":
            """
            scrapy.Request()构建request对象
            callback：指定回调函数,不指定的话默认交给parse方法处理
            meta：在不同的解析方法中传递数据,默认会携带下载延迟和请求深度等信息
            dont_filter：scrapy默认对url去重,但有时候需要多次请求同一个url
            """
            yield scrapy.Request(url=next_page, callback=self.parse, meta=None, dont_filter=False)


class TXSpider02(CrawlSpider):
    """
    基于CrawlSpider类的爬虫：可以自动跟进response里的链接(速度更快)
    """

    # 爬虫名称
    name = 'tx02'
    # 域名约束(指定爬虫范围)
    allowed_domains = ['hr.tencent.com']
    # 起始url
    start_urls = ['https://hr.tencent.com/position.php?&start=']

    # rules列表(可以包含多个Rule对象)
    rules = [
        # 获取其他页面链接,依次发送请求并持续跟进,调用指定回调函数处理
        Rule(LinkExtractor(allow=r"position.php\?\&start=\d+"), callback='parse_item', follow=True)
    ]

    # 注意：此处要自定义方法,parse方法是专门用来将提取的链接构造成request请求发送
    def parse_item(self, response):
        # 获取当前页职位信息列表
        tr_list = response.xpath("//tr[@class='odd'] | //tr[@class='even']")
        # 遍历所有职位
        for tr in tr_list:
            # 创建Item对象
            item = TXItem()
            # 职位名称
            name = tr.xpath("./td[1]/a/text()").extract_first()
            # 详细链接
            link = "https://hr.tencent.com/" + tr.xpath("./td[1]/a/@href").extract_first()
            # 职位类别
            sort = tr.xpath("./td[2]/text()").extract_first()
            # 招聘人数
            num = tr.xpath("./td[3]/text()").extract_first()
            # 上班地点
            site = tr.xpath("./td[4]/text()").extract_first()
            # 发布时间
            publish = tr.xpath("./td[5]/text()").extract_first()
            item['name'] = name
            item['link'] = link
            item['sort'] = sort
            item['num'] = num
            item['site'] = site
            item['publish'] = publish
            # yield可以减少内存占用,yield只能接Request/BaseItem/dict/None
            yield item


