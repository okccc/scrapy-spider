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
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_spider.items import YGItem


class YGSpider(CrawlSpider):
    # 爬虫名称
    name = 'yg02'
    # 爬取范围(可选)
    allowed_domains = ['wz.sun0769.com']
    # 起始url
    start_urls = ['http://wz.sun0769.com/index.php/question/questionType?type=4&page=']

    # rules列表
    rules = (
        Rule(LinkExtractor(allow=r"type=4&page=\d+"), callback='parse_item', follow=True),
    )

    # 注意：此处不能用parse()
    def parse_item(self, response):
        # 获取当前页帖子标签列表
        tr_list = response.xpath('//td[@align="center"]//tr')
        # 遍历
        for tr in tr_list:
            # 创建Item对象
            item = YGItem()
            # 先提取列表页能提取的字段
            item["title"] = tr.xpath('.//a[2]/text()').extract_first()
            item["link"] = tr.xpath('.//a[2]/@href').extract_first()
            item["publish"] = tr.xpath('.//td[last()]/text()').extract_first()
            # CrawlSpider类中也是可以手动构建request对象的
            yield scrapy.Request(url=item["link"], callback=self.parse_detail, meta={"item": item})

    def parse_detail(self, response):
        # 接收上个方法传递的item对象
        item = response.meta["item"]
        # 继续提取详情页的字段
        item["img"] = response.xpath('//td[@class="txt16_3"]//img/@src').extract_first()
        item["img"] = "http://wz.sun0769.com" + item["img"] if item["img"] else None
        if item["img"]:
            item["content"] = response.xpath('//div[@class="contentext"]/text()').extract_first()
        else:
            item["content"] = response.xpath('//td[@class="txt16_3"]/text()').extract_first()
        yield item
