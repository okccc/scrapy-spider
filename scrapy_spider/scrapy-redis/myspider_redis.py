from scrapy_redis.spiders import RedisSpider


class MySpider(RedisSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""
    name = 'myspider_redis'
    allowed_domains = ['...']

    # RedisSpider类不写start_urls而是从redis_key取,不然每台机器都会重复抓取初始url
    # redis_key是一个空列表,程序开始时spider会处于等待状态,需要先lpush初始url到redis_key中
    redis_key = 'myspider:start_urls'  # 名字可以随便写

    # def __init__(self, *args, **kwargs):
    #     # Dynamically define the allowed domains list.
    #     domain = kwargs.pop('domain', '')
    #     self.allowed_domains = filter(None, domain.split(','))
    #     super(MySpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        return {
            'name': response.css('title::text').extract_first(),
            'url': response.url,
        }
