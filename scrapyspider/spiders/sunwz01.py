# coding=utf-8
"""
问题：scrapy爬取的数据含有\xa0字符,其实是网页源码中的"&nbsp;"字符串,表示不间断的空格符,不能直接以split(" ")分割
<strong class="tgray14">提问：投诉城管&nbsp;&nbsp;编号:186603&nbsp;&nbsp;</strong>
解决：s = "".join(s.split())
strip(): 只能去除字符串两边的空格,中间的去除不了
split(): 不带参数时表示分割所有 换行符/制表符/空格
'sep'.join(sequence): 将序列(string/tuple/list等)中的元素与分隔符sep(可以为空)拼接成一个新字符串
举例：
sep = "-"
sequence = ["a", "b", "c"]
print(sep.join(sequence))  # a-b-c

问题：用xpathhelper测试时发现//div[@class='***']/text()的results != 1,是因为网页源码中的<br>换行符(见截图)
     如果text = response.xpath("//div[@class='***']/text()").extract()[0]则只能取到文本的第一行而不是全部行的数据
解决：text = response.xpath("//div[@class='***']/text()").extract()  # 此时text是包含所有行的list
     res = "".join(text).strip()

xpath提取数据时: extract()[0] == get()
               extract() == getall()
"""

import scrapy
from scrapyspider.items import SunwzspiderItem


class SunwzSpider(scrapy.Spider):
    """
    基于Spider类的爬虫
    """

    # 爬虫名称
    name = 'sunwz01'
    # 网站域名
    allowed_domains = ['wz.sun0769.com']
    # 起始url
    url = "http://wz.sun0769.com/index.php/question/questionType?type=4&page="
    offset = 0
    start_urls = [url + str(offset)]

    # 获取页面response的所有帖子
    def parse(self, response):
        # 获取当前页所有帖子的链接列表
        links = response.xpath("//a[@class='news14']/@href").extract()
        # 迭代获取每个帖子链接
        for each in links:
            # 将链接放到请求队列并调用self.parse_item处理帖子的response
            yield scrapy.Request(each, callback=self.parse_item)
        # 爬完第一页继续往后翻
        if self.offset < 120:
            self.offset += 30
            # 向新的页面发起请求并调用self.parse处理页面的response
            yield scrapy.Request(self.url + str(self.offset), callback=self.parse)

    # 处理每个帖子response的内容
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

        # # 爬完第一页继续往后翻
        # if self.offset < 120:
        #     self.offset += 30
        # # 向新的页面发起请求并调用self.parse处理页面的response
        # yield scrapy.Request(self.url + str(self.offset), callback=self.parse)
