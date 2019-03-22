# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_spider.items import TXItem


class TXSpider(CrawlSpider):
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
        # 获取页面链接,依次发送请求并持续跟进,调用指定回调函数处理
        Rule(LinkExtractor(allow=r"position.php\?\&start=\d+"), callback='parse_item', follow=True)
    ]

    def parse_item(self, response):
        # 创建Item对象
        item = TXItem()
        # 获取当前页职位信息列表
        positions = response.xpath("//tr[@class='odd'] | //tr[@class='even']")
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
