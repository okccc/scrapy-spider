# -*- coding: utf-8 -*-
"""
CrawlSpider(class scrapy.spiders.CrawlSpider)
Spider类:
    默认parse()函数解析：只爬取start_urls列表中的网页,爬取新的页面需要手动更新url
CrawlSpider类:
    自定义parse_xxx()函数解析：定义了一些规则(rule)来提供跟进(link)的机制并指定回调函数parse_xxx,从爬取的网页中获取link并继续爬取

LinkExtractors类:
    用于提取链接,该类的extract_links()方法接收一个Response对象,返回一个scrapy.link.Link对象
    该类需要实例化一次,并且extract_links()方法会根据不同的response调用多次提取链接
class scrapy.linkextractors.LinkExtractor(
    allow = (),                 # 满足括号中'正则表达式'的值会被提取,如果为空则全部匹配(常用)
    deny = (),                  # 与这个正则表达式不匹配的URL一定不提取
    allow_domains = (),         # 会被提取的链接的domains(常用)
    deny_domains = (),          # 一定不会被提取链接的domains
    deny_extensions = None,
    restrict_xpaths = (),       # 使用xpath表达式,和allow共同作用过滤链接
    tags = ('a','area'),
    attrs = ('href'),
    canonicalize = True,
    unique = True,
    process_value = None
)

rules:
    包含一个或多个Rule对象,每个Rule对爬取网站的动作定义了特定操作
class scrapy.spiders.Rule(
    link_extractor,             # 是一个LinkExtractor对象,定义需要提取的链接
    callback = None,            # 从link_extractor中每获取到新的链接时,指定回调函数
    cb_kwargs = None,
    follow = None,              # 是否依据规则跟进链接,不写callback默认True,写callback默认False
    process_links = None,       # 调用函数处理从link_extractor中获取到的链接(有些反爬虫会故意响应错误链接)
    process_request = None      # 指定调用的函数,用于过滤提取到的每个request
)
"""

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapyspider.items import TencentspiderItem


class TencentSpider(CrawlSpider):
    """
    基于CrawlSpider类的爬虫：可以自动跟进response里的链接(速度更快)
    """

    # 爬虫名称
    name = 'tencent02'
    # 域名约束(指定爬虫范围)
    allowed_domains = ['hr.tencent.com']
    # 起始url
    start_urls = ['https://hr.tencent.com/position.php?&start=']

    # 每一页链接的匹配规则
    # pageLink = LinkExtractor(allow="position.php\?\&start=\d+")
    # print(type(pageLink))  # <class 'scrapy.linkextractors.lxmlhtml.LxmlLinkExtractor'>

    # rules列表(可以包含多个Rule)
    rules = [
        # 获取页面链接,依次发送请求并持续跟进,调用指定回调函数处理
        Rule(LinkExtractor(allow="position.php\?\&start=\d+"), callback='parse_item', follow=True)
    ]

    def parse_item(self, response):
        # print(response.url)  # https://hr.tencent.com/position.php?&start=0

        # 创建Item对象
        item = TencentspiderItem()

        # 获取当前页职位信息列表
        positions = response.xpath("//tr[@class='odd'] | //tr[@class='even']")
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
