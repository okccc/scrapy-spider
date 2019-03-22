# coding=utf-8
"""
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
xpath提取数据: extract_first() <==> get();  extract() <==> getall()
"""

import scrapy
from scrapy_spider.items import YGItem


class YGSpider(scrapy.Spider):
    # 爬虫名称
    name = 'yg01'
    # 爬取范围
    allowed_domains = ['wz.sun0769.com']
    # 初始url
    start_urls = ["http://wz.sun0769.com/index.php/question/questionType?type=4&page="]

    # 注意：parse()方法名是固定的,继承的父类未实现的方法
    def parse(self, response):
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
            # 构建新的request对象访问详情页
            yield scrapy.Request(url=item["link"], callback=self.parse_detail, meta={"item": item})
        # 判断下一页：
        next_page = response.xpath('//a[text()=">"]/@href').extract_first()
        if next_page:
            """
            scrapy.Request()构建request对象
            callback：指定传入的url交给哪个方法解析
            meta：在不同的解析方法中传递数据,默认会携带下载延迟和请求深度等信息
            dont_filter：scrapy默认对url去重,但有时候需要多次请求同一个url
            """
            yield scrapy.Request(next_page, callback=self.parse)

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
        print(type(item))
        yield item
