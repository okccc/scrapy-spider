# Scrapy settings for example project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
SPIDER_MODULES = ['example.spiders']
NEWSPIDER_MODULE = 'example.spiders'

USER_AGENT = 'scrapy-redis (+https://github.com/rolando/scrapy-redis)'

REDIS_URL = "redis://127.0.0.1:6379"  # 指定redis地址

DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"  # 指定给request对象去重的方法
SCHEDULER = "scrapy_redis.scheduler.Scheduler"  # 指定scheduler队列
SCHEDULER_PERSIST = True  # 队列中的内容是否持久化,False表示会在关闭redis时清空redis
#SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"
#SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"
#SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderStack"

ITEM_PIPELINES = {
    'example.pipelines.ExamplePipeline': 300,
    'scrapy_redis.pipelines.RedisPipeline': 400,  # 将item放入redis的pipeline,如果不想保存大redis就注释掉
}

LOG_LEVEL = 'DEBUG'

# Introduce an artifical delay to make use of parallelism. to speed up the
# crawl.
DOWNLOAD_DELAY = 1
