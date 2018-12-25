# -*- coding: utf-8 -*-
"""
CrawlSpider(class scrapy.spiders.CrawlSpider)
Spider类:
    只爬取start_urls列表中的网页
CrawlSpider类:
    定义了一些规则(rule)来提供跟进link的机制,从爬取的网页中获取link并继续爬取

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
    callback = None,            # 从link_extractor中每获取到新的链接时,指定回调函数处理response响应的数据
    cb_kwargs = None,
    follow = None,              # 是否依据规则跟进链接,不写callback默认True,写callback默认False
    process_links = None,       # 调用函数处理从link_extractor中获取到的链接(有些反爬虫会故意响应错误链接)
    process_request = None      # 指定调用的函数,用于过滤提取到的每个request
)
"""

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapyspider.items import SunwzspiderItem


class SunwzSpider(CrawlSpider):
    """
    基于CrawlSpider类的爬虫
    """

    # 爬虫名称
    name = 'sunwz02'
    # 网站域名
    allowed_domains = ['wz.sun0769.com']
    # 起始url
    start_urls = ['http://wz.sun0769.com/index.php/question/questionType?type=4&page=']

    # rules列表
    rules = (
        # 页面匹配规则: 有些网站的反爬虫措施会对响应的url做手脚,此时需调用process_links方法处理后返回正确格式的url
        Rule(LinkExtractor(allow="type=4&page=\d+"), process_links="deal_links"),
        # 页面里帖子链接匹配规则: 调用callback抓取帖子链接里的数据
        Rule(LinkExtractor(allow="question/\d+/\d+.shtml"), callback="parse_item"),
    )

    # 处理链接
    def deal_links(self, links):
        for each in links:
            # 调整url格式
            each.url = each.url.replace("?", "&").replace("Type&", "Type?")
        return links

    # 处理帖子数据
    def parse_item(self, response):
        # 创建Item对象
        item = SunwzspiderItem()

        text1 = response.xpath("//div[@class='pagecenter p3']//strong[@class='tgray14']/text()").extract()[0]
        # 编号
        id = text1.split()[-1].split(":")[1]
        # 标题
        title = text1.split()[0].split("：")[1]
        # 链接
        link = response.url
        # 状态
        status = response.xpath("//div[@class='cleft']/span/text()").extract()[0]
        text2 = response.xpath("//div[@class='content text14_2']//p/text()").extract()[0]
        # 网友
        netizen = text2.split()[0].split("：")[1]
        # 时间
        time = text2.split("：")[-1].strip()
        # 内容(带图片)
        content = response.xpath("//div[@class='contentext']/text()").extract()
        if len(content) == 0:
            # 不带图片
            content = response.xpath("//div[@class='c1 text14_2']/text()").extract()
        else:
            content = content

        item["id"] = id
        item["title"] = title
        item["link"] = link
        item["status"] = status
        item["netizen"] = netizen
        item["time"] = time
        item["content"] = "".join("".join(content).strip().split())

        # 将数据交给pipeline处理
        yield item