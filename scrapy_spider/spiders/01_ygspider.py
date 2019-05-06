# -*- coding: utf-8 -*-
"""
Spider类：所有爬虫的基类,默认parse()函数解析,只爬取start_urls列表中的页面,需要手动翻页
1.__init__()：初始化爬虫名name和start_urls列表
2.start_requests()：调用make_requests_from_url()方法,将start_urls中的url生成request对象交给scrapy下载并返回response
3.parse()：解析response,返回Item(交给ItemPipeline持久化)或Request对象(放入爬取队列交给scrapy继续下载)

CrawlSpider类: 需要自定义parse_item()函数解析,定义一些rule来提供跟进link的机制从爬取的网页中获取新的link并继续爬取
LinkExtractor(
    allow = (),                 # 满足括号中'正则表达式'的值会被提取,如果为空就全部匹配(常用)
    deny = (),                  # 与这个正则表达式不匹配的URL一定不提取,优先级高于allow
    allow_domains = (),         # 会被提取的链接的domains(常用)
    deny_domains = (),          # 一定不会被提取链接的domains
    restrict_xpaths = (),       # 如果要提取的链接太复杂re不好匹配可以改用xpath
)
Rule(
    link_extractor,             # 是一个LinkExtractor对象,定义需要提取的链接
    callback = None,            # 匹配的链接需要提取数据时才会指定callback(比如数据都在详情页,新匹配的列表页就不需要指定callback)
    follow = None,              # 是否循环跟进页面中符合allow匹配规则的链接
    process_links = None,       # 过滤从link_extractor中提取的link(有些反爬虫会故意响应错误链接)
    process_request = None      # 过滤request
)

问题：scrapy爬取的数据含有\xa0字符,其实是网页源码中的"&nbsp;"字符串,表示不间断的空格符,不能直接以split("***")分割
<strong class="tgray14">提问：投诉城管&nbsp;&nbsp;编号:186603&nbsp;&nbsp;</strong>
解决：s = "".join(s.split())
strip(): 只能去除字符串两边的空格,中间的去除不了
split(): 不带参数时表示分割所有 换行符/制表符/空格
'sep'.join(sequence): 将序列(string/tuple/list)中的元素与分隔符sep(可以为空)拼接成一个新字符串
举例：
sep = "-"
sequence = ["a", "b", "c"]
print(sep.join(sequence))  # a-b-c

问题：xpath_helper测试时发现'//div[@class="***"]/text()'的results != 1,是因为网页源码中的<br>换行符
     response.xpath('//div[@class="***"]/text()').extract_first()只能取到文本的第一行而不是全部行
方式一："".join(response.xpath('//div[@class="***"]/text()').extract()).split()
方式二："".join(response.xpath('div[@class="***"]//text()').extract_first().split())
xpath提取数据: extract_first = get  extract = getall
"""

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_spider.items import YGItem


class YGSpider01(scrapy.Spider):
    # 基于Spider类的爬虫：需要手动刷新url(更安全,有些网站翻页时url不变是通过js生成的,需要破解对应的js)
    # 爬虫名称
    name = 'yg01'
    # 爬取范围
    allowed_domains = ['wz.sun0769.com']
    # 初始url,不会被allowed_domains过滤
    start_urls = ["http://wz.sun0769.com/index.php/question/questionType?type=4&page="]

    def parse(self, response):
        """
        # 注意：parse()方法名是固定的,继承自父类未实现的方法
        在parse方法之前start_requests方法会先请求start_urls中的url返回response交给parse方法解析
        scrapy.Request()构建request对象
        callback：指定回调函数,不指定的话默认交给parse方法处理
        meta：在不同的解析方法中传递数据,默认会携带下载延迟和请求深度等信息
        dont_filter：scrapy默认对url去重,但有时候需要多次请求同一个url
        """

        # 创建Item对象
        item = YGItem()
        # 获取当前页帖子列表
        tr_list = response.xpath('//td[@align="center"]//tr')
        for tr in tr_list:
            # 先提取列表页能提取的字段
            item["title"] = tr.xpath('.//a[2]/text()').extract_first()
            item["link"] = tr.xpath('.//a[2]/@href').extract_first()
            item["publish"] = tr.xpath('.//td[last()]/text()').extract_first()
            # 构建新的request对象访问详情页
            yield scrapy.Request(url=item["link"], callback=self.parse_detail, meta={"item": item})
        # 判断下一页：
        next_page = response.xpath('//a[text()=">"]/@href').extract_first()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse, meta=None, dont_filter=False)

    @staticmethod
    def parse_detail(response):
        # 接收上个方法传递的item对象
        item = response.meta["item"]
        # 继续提取详情页的字段
        item["img"] = response.xpath('//td[@class="txt16_3"]//img/@src').extract_first()
        item["img"] = "http://wz.sun0769.com" + item["img"] if item["img"] else None
        if item["img"]:
            item["content"] = response.xpath('//div[@class="contentext"]/text()').extract_first()
        else:
            item["content"] = response.xpath('//td[@class="txt16_3"]/text()').extract_first()
        # yield可以减少内存占用,yield只能接Request/BaseItem/dict/None
        yield item


class YGSpider02(CrawlSpider):
    # 基于CrawlSpider类的爬虫：可以自动跟进response里的链接(速度更快)
    # 爬虫名称
    name = 'yg02'
    # 爬取范围(可选)
    allowed_domains = ['wz.sun0769.com']
    # 起始url
    start_urls = ['http://wz.sun0769.com/index.php/question/questionType?type=4&page=']

    # rules列表(可以包含多个Rule对象)
    rules = (
        # 获取其他页面链接,依次发送请求并持续跟进,调用指定回调函数处理
        Rule(LinkExtractor(allow=r"type=4&page=\d+"), callback='parse_item', follow=True),
    )

    # 注意：此处要自定义方法,parse方法是专门用来将提取的链接构造成request请求发送
    def parse_item(self, response):
        # 获取当前页帖子列表
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

    @staticmethod
    def parse_detail(response):
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

