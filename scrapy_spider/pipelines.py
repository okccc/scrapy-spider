# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from scrapy_spider.items import NewHouseItem, EsfHouseItem, EsfHouseItem02, HospitalItem, DoctorItem
from twisted.enterprise import adbapi
import json


class SoufangspiderPipeline(object):
    def __init__(self):

        config = {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "root",
            "db": "test",
            "charset": "utf8",
            "cursorclass": pymysql.cursors.DictCursor  # 以dict格式返回数据
        }
        # 创建数据库连接池
        self.dbpool = adbapi.ConnectionPool("pymysql", **config)

    def process_item(self, item, spider):
        # runInteraction()函数将mysql插入变成异步执行,直接调用insert方法是同步插入
        self.dbpool.runInteraction(self.do_insert, item)

        return item

    def do_insert(self, cursor, item):
        value = []
        if item.__class__ == NewHouseItem:
            fields1 = ["id", "province", "city", "community", "url", "price", "area", "district", "address", "sale"]
            for field in fields1:
                value.append(item[field])
        # elif item.__class__.startswith("EsfHouseItem"):
        elif item.__class__ == EsfHouseItem or EsfHouseItem02:
            fields2 = ["community", "title", "province", "city", "address", "rooms", "floor", "toward", "year", "area", "price", "unit"]
            for field in fields2:
                value.append(item[field])
        else:
            pass

        try:
            sql1 = "replace into newhouse values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            sql2 = "replace into esfhouse values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            if len(value) == 10:
                cursor.execute(sql1, value)
            elif len(value) == 12:
                cursor.execute(sql2, value)
            else:
                pass
        except Exception as e:
            print(e)


class SoyoungspiderPipeline(object):
    def __init__(self):

        config = {
            "host": "10.9.157.245",
            "port": 3306,
            "user": "root",
            "password": "ldaI00Uivwp",
            "db": "test",
            "charset": "utf8"
        }
        self.conn = pymysql.connect(**config)
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        value = []
        if item.__class__ == HospitalItem:
            fields1 = ["id", "name", "aptitude", "address", "skilled", "insert_time"]
            for field in fields1:
                value.append(item[field])
            # print(value)
        elif item.__class__ == DoctorItem:
            fields2 = ["id", "name", "hospital_id", "hospital_name", "title", "skilled", "insert_time"]
            for field in fields2:
                value.append(item[field])
            # print(value)
        else:
            pass

        try:
            sql1 = "replace into hospital values(%s,%s,%s,%s,%s,%s)"
            sql2 = "replace into doctor values(%s,%s,%s,%s,%s,%s,%s)"
            if len(value) == 6:
                self.cur.execute(sql1, value)
            elif len(value) == 7:
                self.cur.execute(sql2, value)
            else:
                pass
            self.conn.commit()
        except Exception as e:
            print(e)

        return item

    def close(self):
        self.cur.close()
        self.conn.close()


class JianshuspiderPipeline(object):
    def __init__(self):
        config = {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "root",
            "db": "test",
            "charset": "utf8"
        }
        self.conn = pymysql.connect(**config)
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        value = []
        fields = ["id", "title", "link", "author", "pubtime", "content", "readings", "comments", "subjects"]
        for field in fields:
            value.append(item[field])
        print(value)

        try:
            sql = "replace into articles values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            self.cur.execute(sql, value)
            self.conn.commit()
        except Exception as e:
            print(e)

        return item

    def close(self):
        self.cur.close()
        self.conn.close()


class JianshuTwistedspiderPipline(object):
    def __init__(self):
        config = {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "root",
            "db": "test",
            "charset": "utf8",
            "cursorclass": pymysql.cursors.DictCursor  # 以dict格式返回数据
        }

        # 创建数据库连接池
        self.dbpool = adbapi.ConnectionPool('pymysql', **config)

    def process_item(self, item, spider):
        # runInteraction()函数将mysql插入变成异步执行,直接调用insert方法是同步插入
        self.dbpool.runInteraction(self.do_insert, item)

        return item

    def do_insert(self, cursor, item):
        # cursor对象是cursorclass类传过来的
        value = []
        fields = ["id", "title", "link", "author", "pubtime", "content", "readings", "comments", "subjects"]
        for field in fields:
            value.append(item[field])
        try:
            sql = "replace into articles values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql, value)
        except Exception as e:
            print(e)


class SunwzspiderPipeline(object):
    def __init__(self):
        self.file = open("C://Users/Public/post.json", "w", encoding="utf-8")

    def process_item(self, item, spider):
        self.file.write(json.dumps(dict(item), ensure_ascii=False) + "\n")
        return item

    def close(self):
        self.file.close()


class TencentspiderPipeline(object):
    def __init__(self):
        self.file = open("./position.csv", "w", encoding="utf-8")

    # 初始化和关闭文件方法只会执行一次,写数据方法会反复调用,有数据过来就处理
    def process_item(self, item, spider):
        self.file.write(json.dumps(dict(item), ensure_ascii=False) + "\n")
        return item

    def close(self):
        self.file.close()


class ItcastPipeline(object):
    """
    管道文件：保存爬虫程序抓取的数据
    """

    # __init__()方法是可选的,用于初始化
    def __init__(self):
        self.filename = open("./teacher.json", "w", encoding="utf-8")

    # process_item()方法必须写,用来处理item数据
    def process_item(self, item, spider):
        # 注意：要先将item对象转换成dict --> TypeError: Object of type 'MyspiderItem' is not JSON serializable
        self.filename.write(json.dumps(dict(item), ensure_ascii=False) + "\n")
        # 为了在不同的pipeline中传递item需要将其return,不然后序pipeline接收的item是None
        return item

    # close_spider()方法是可选的,结束时调用
    def close_spider(self, spider):
        self.filename.close()
