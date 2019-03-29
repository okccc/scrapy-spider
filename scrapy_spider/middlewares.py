# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


class ScrapyspiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScrapyspiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


from fake_useragent import UserAgent
from scrapy_spider.utils.crud import random
from scrapy.http import HtmlResponse


class RandomUserAgent(object):
    # 下载中间件处理请求
    def process_request(self, request, spider):
        ua = UserAgent()
        request.headers.setdefault('User-Agent', ua.random)


class CheckUserAgent(object):
    # 下载中间件处理响应
    def process_response(self, request, response, spider):
        # print(dir(request))
        # print(dir(response))
        print(request.headers["User-Agent"])
        # 注意：process_response()必须有返回值,返回request表示经过引擎交给调度器,返回response表示经过引擎交给爬虫(scrapy架构图)
        # AssertionError: Middleware CheckUserAgent.process_response must return Response or Request, got <class 'NoneType'>
        return response


class RandomProxy(object):
    def process_request(self, request, spider):
        proxy_ip = random()
        print(proxy_ip)
        request.meta['proxy'] = proxy_ip


class SeleniumMiddleware(object):
    """
    scrapy集成selenium
    """

    # def __init__(self):
    #     # 设置chrome不加载图片
    #     chrome_options = webdriver.ChromeOptions()
    #     prefs = {"profile.managed_default_content_settings.images": 2}
    #     chrome_options.add_experimental_option("prefs", prefs)
    #     # 创建浏览器对象
    #     self.driver = webdriver.Chrome(executable_path="D://chromedriver/chromedriver.exe", chrome_options=chrome_options)

    def process_request(self, request, spider):
        """
        改进：DownloaderMiddlewares只能处理request和response,却无法在scrapy程序结束后关闭chrome
             既然不是每个spider都需要chrome,那么可以将chrome放到需要的spider程序由spider关闭,这样多个spider还能启动多个chrome并发运行
        """

        if spider.name == "jianshu":
            # 打开页面
            spider.driver.get(request.url)

            # 获取展开更多标签
            try:
                while True:
                    # 标签可能需要点击多次
                    tag = spider.driver.find_element_by_class_name("show-more")
                    tag.click()
                    if not tag:
                        break
            except:
                pass

            # 将获取到的源码封装成response对象并直接返回给spider处理,而不再将request发送到downloader下载
            return HtmlResponse(url=request.url, body=spider.driver.page_source, request=request, encoding="utf-8")