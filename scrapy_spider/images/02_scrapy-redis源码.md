#### 为什么要用scrapy-redis?  
- scrapy基于set()做request去重,request对象存放于各个程序的调度器(内存),所以只能单机爬并且程序重启会重复抓取已经抓过的url
- scrapy-redis基于redis做request去重,request对象存放于redis,可以联机爬并且程序重启不会重复抓取已经抓过的url(断点续爬),从而实现分布式增量爬虫

### settings.py变化部分
```python
REDIS_URL = "redis://127.0.0.1:6379"  # redis地址
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"  # 指定指纹去重组件,取代scrapy默认去重方法
SCHEDULER = "scrapy_redis.scheduler.Scheduler"  # 指定调度器,取代scrapy默认调度器
SCHEDULER_PERSIST = True  # 调度器持久化,爬虫结束时是否清空redis中的request队列和去重指纹set
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"  # 指定队列请求方式,按照优先级
#SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"
#SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderStack"
ITEM_PIPELINES = {
    'example.pipelines.ExamplePipeline': 300,
    'scrapy_redis.pipelines.RedisPipeline': 400,  # 该pipeline将item存入redis,如果不想保存到redis就注释掉
}
```

### RedisPipeline类
```python
def process_item(self, item, spider):
    return deferToThread(self._process_item, item, spider)

def _process_item(self, item, spider):
    key = self.item_key(item, spider)
    data = self.serialize(item)
    self.server.rpush(key, data)  # rpush说明是list列表
    return item
    
def item_key(self, item, spider):
    """Returns redis key based on given spider."""
    return self.key % {'spider': spider.name}
```

### RFPDupeFilter类
- 判断指纹是否已存在于redis的set集合
```python
def request_seen(self, request):
    """Returns True if request was already seen."""
    fp = self.request_fingerprint(request)
    # This returns the number of values added, zero if already exists.
    added = self.server.sadd(self.key, fp)
    return added == 0
```
- 使用hashlib.sha1加密request对象存入redis做指纹去重
```python
def request_fingerprint(request, include_headers=None):
    """
    Return the request fingerprint.

    The request fingerprint is a hash that uniquely identifies the resource the
    request points to. For example, take the following two urls:

    http://www.example.com/query?id=111&cat=222
    http://www.example.com/query?cat=222&id=111

    Even though those are two different URLs both point to the same resource
    and are equivalent (ie. they should return the same response).

    Another example are cookies used to store session ids. Suppose the
    following page is only accesible to authenticated users(通过身份验证的用户):

    http://www.example.com/members/offers.html

    Lot of sites use a cookie to store the session id, which adds a random
    component to the HTTP Request and thus should be ignored when calculating
    the fingerprint.

    For this reason, request headers are ignored by default when calculating
    the fingeprint. If you want to include specific headers use the
    include_headers argument, which is a list of Request headers to include.

    """
    
    # 计算指纹时默认忽略请求头,因为headers的cookie中含有随机值sessionid,在sha1计算时会引起偏差
    if include_headers not in cache:
        fp = hashlib.sha1()  
        fp.update(to_bytes(request.method))  # 请求方法
        fp.update(to_bytes(canonicalize_url(request.url)))  # 请求url
        fp.update(request.body or b'')  # 请求体
    return fp.hexdigest()
```

### Scheduler类
- 调度器是否持久化
```python
def close(self, reason):
    if not self.persist:
        self.flush()

def flush(self):
    self.df.clear()  # 清空去重指纹
    self.queue.clear()  # 清空请求队列
```
- 当指纹不存在或者dont_filter=True时request对象才会入队列
```python
def enqueue_request(self, request):
    if not request.dont_filter and self.df.request_seen(request):
        # 默认dont_filter=False(True) and request指纹已存在(True) --> 不入队列
        # 默认dont_filter=False(True) and request指纹不存在(False) --> 入队列
        # 由于start_urls是程序入口,dont_filter=True(False) --> 入队列
        self.df.log(request, self.spider)
        return False
    self.queue.push(request)  # 入队列
    return True
```
