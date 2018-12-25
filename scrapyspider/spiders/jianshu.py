# -*- coding: utf-8 -*-
"""
在scrapy框架中使用selenium模拟浏览器处理ajax动态加载的页面
思路：自定义下载器中间件替换scrapy流程图中的downloader下载器,包括request和response两部分
"""

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapyspider.items import JianshuspiderItem
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class JianshuSpider(CrawlSpider):
    name = 'jianshu'
    allowed_domains = ['jianshu.com']
    start_urls = ['https://jianshu.com']

    rules = (
        # 文章链接匹配规则
        Rule(LinkExtractor(allow='/p/[0-9a-z]{12}'), callback='parse_item', follow=True),
    )

    def __init__(self):
        # 设置chrome不加载图片
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        # 创建浏览器对象
        self.driver = webdriver.Chrome(executable_path="D://chromedriver/chromedriver.exe", chrome_options=chrome_options)
        super().__init__()

        # 分发器做信号映射：当signals.spider_closed信号发生时调用close_chrome()函数
        dispatcher.connect(receiver=self.spider_closed, signal=signals.spider_closed)

    # 关闭spider时的逻辑处理
    def spider_closed(self):
        # 当爬虫结束时退出chrome
        print("spider is over and quit chrome...")
        self.driver.quit()

    def parse_item(self, response):
        item = JianshuspiderItem()

        id = response.url.split("/")[-1]
        title = response.xpath('//h1[@class="title"]/text()').get()
        link = response.url
        author = response.xpath('//span[@class="name"]/a/text()').get()
        pubtime = response.xpath('//span[@class="publish-time"]/text()').get()
        content = response.xpath('//div[@class="show-content"]').get()
        readings = response.xpath('//span[@class="views-count"]/text()').get().split()[1]
        comments = response.xpath('//span[@class="comments-count"]/text()').get().split()[1]
        subjects = ",".join(response.xpath('//div[@class="include-collection"]/a/div[@class="name"]/text()').getall())

        item["id"] = id
        item["title"] = title
        item["link"] = link
        item["author"] = author
        item["pubtime"] = pubtime
        item["content"] = content
        item["readings"] = readings
        item["comments"] = comments
        item["subjects"] = subjects

        yield item
