# -*- coding: utf-8 -*-

import scrapy
from scrapy_spider.items import SNItem
from copy import deepcopy
import re


class SNSpider(scrapy.Spider):

    # 爬虫名称
    name = "sn"
    # 爬取范围
    allowed_domains = ["suning.com"]
    # 初始url,不会被allowed_domains过滤
    start_urls = ["https://book.suning.com/"]

    def parse(self, response):
        # 创建Item对象
        item = SNItem()
        # 1.获取大分类列表
        div_list = response.xpath('//div[@class="menu-item"]')
        # 遍历大分类
        for div in div_list:
            # 大分类名称
            item["b_category"] = div.xpath('.//h3/a/text()').extract_first()
            # 2.获取小分类列表
            a_list = div.xpath('.//dd/a')
            # 遍历小分类
            for a in a_list:
                # 小分类名称
                item["s_category"] = a.xpath('./text()').extract_first()
                # 小分类链接
                href = a.xpath('./@href').extract_first()
                if href:
                    # 3.将小分类url构造成新的Request对象
                    yield scrapy.Request(
                        url=href,
                        callback=self.parse_book_list,
                        # 由于scrapy是异步的,在不同Request之间传递meta时要注意item作用范围,直接赋值会覆盖前面结果,此处要用深拷贝
                        meta={"item": deepcopy(href)}
                    )

    def parse_book_list(self, response):
        # 接收传递的meta信息
        item = response.meta["item"]
        # 获取当前页图书列表
        li_list = response.xpath('//div[@id="filter-results"]//ul/li')
        # 遍历图书
        for li in li_list:
            # 图书链接
            item["link"] = "https:" + li.xpath('.//div[@class="img-block"]/a/@href').extract_first()
            # 图书名称
            item["name"] = li.xpath('.//p[@class="sell-point"]/a/text()').extract_first()
            yield scrapy.Request(
                url=item["link"],
                callback=self.parse_book_detail,
                meta={"item": deepcopy(item)}
            )
        # 判断下一页(翻页时地址栏url居然没变说明翻页功能是通过js生成的)
        s_category_id = re.search("\d{6}", item["href"]).group()
        current_page = re.findall('param.currentPage = (.*?);', response.text)[0]
        page_num = re.findall('param.pageNumbers = (.*?);', response.text)[0]
        if current_page < page_num:
            next_page = "https://list.suning.com/emall/showProductList.do?ci={}&pg=03&cp={}".format(s_category_id, current_page.replace('"',''))
            print(next_page)
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_book_list,
                meta={"item": item}
            )

    def parse_book_detail(self, response):
        # 接收传递的meta信息
        item = response.meta["item"]
        item["author"] = response.xpath('//ul[@class="bk-publish clearfix"]/li[1]/text()').extract_first()
        item["press"] = response.xpath('//ul[@class="bk-publish clearfix"]/li[2]/text()').extract_first()
        item["publish"] = response.xpath('//ul[@class="bk-publish clearfix"]/li[3]/span[last()]/text()').extract_first()
        item["price"] = response.xpath('//span[@class="mainprice"]/i/text()').extract()
        yield item
