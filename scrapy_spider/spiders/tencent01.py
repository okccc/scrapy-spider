# -*- coding: utf-8 -*-
"""
Spider类：所有爬虫的基类,默认parse()函数解析,只爬取start_urls列表中的页面,需要手动翻页
__init__()：初始化爬虫名字和start_urls列表
start_requests()：调用make_requests_from_url()方法,将start_urls中的url生成request对象交给scrapy下载并返回response
parse()：解析response,返回Item(交给ItemPipeline持久化)或者Request对象(放入爬取队列交给scrapy继续下载)

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
from scrapy_spider.items import TXItem


class TXSpider(scrapy.Spider):
    """
    基于Spider类的爬虫：需要手动刷新url(更安全: 可以避免反爬虫故意篡改url的问题)
    """

    # 爬虫名称
    name = "tx01"
    # 爬取范围(可选)
    allowed_domains = ["tencent.com"]
    # 初始url,不会被allowed_domains过滤
    start_urls = ["http://hr.tencent.com/position.php?&start="]

    # 注意：parse()方法名是固定的,继承的父类未实现的方法
    def parse(self, response):
        # 创建Item对象
        item = TXItem()
        # 获取当前页职位信息列表
        positions = response.xpath("//tr[@class='even'] | //tr[@class='odd']")
        # 遍历所有职位
        for each in positions:
            # 职位名称
            name = each.xpath("./td[1]/a/text()").extract_first()
            # 详细链接
            link = "https://hr.tencent.com/" + each.xpath("./td[1]/a/@href").extract_first()
            # 职位类别
            sort = each.xpath("./td[2]/text()").extract_first()
            # 招聘人数
            num = each.xpath("./td[3]/text()").extract_first()
            # 上班地点
            site = each.xpath("./td[4]/text()").extract_first()
            # 发布时间
            publish = each.xpath("./td[5]/text()").extract_first()
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
            callback：指定传入的url交给哪个方法解析
            meta：在不同的解析方法中传递数据,默认会携带下载延迟和请求深度等信息
            dont_filter：scrapy默认对url去重,但有时候需要多次请求同一个url
            """
            yield scrapy.Request(url=next_page, callback=self.parse, meta=None, dont_filter=False)


