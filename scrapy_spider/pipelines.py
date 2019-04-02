# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from scrapy_spider.items import XFItem, ESFItem, ESFItem02, HospitalItem, DoctorItem
from twisted.enterprise import adbapi
import json
import re


class TXPipeline(object):
    def __init__(self):
        self.file = open("./position.csv", "w", encoding="utf-8")

    def process_item(self, item, spider):
        """
        process_item()方法必须写,用来处理item数据
        注意：要先将item对象转换成dict --> TypeError: Object of type 'MyspiderItem' is not JSON serializable
        写入文件和数据库区别：
        程序报错文件是没有数据的,因为没有等到file.close()执行
        程序报错数据库也会有数据,因为insert之后的commit操作不需要等到con.close(),所以抓多少就能存多少
        """
        self.file.write(json.dumps(dict(item), ensure_ascii=False, indent=2))
        print(item)
        # 处理完的item要return,因为有些item可能还要经过后续pipeline处理
        return item

    def close_spider(self, spider):
        # This method is called when the spider is closed.
        self.file.close()


class YGPipeline(object):
    def process_item(self, item, spider):
        # content字段的值要处理下
        item["content"] = self.process_content(item["content"])
        with open("./sun.json", "a", encoding="utf8") as f:
            f.write(json.dumps(dict(item), ensure_ascii=False, indent=2) + "\n")
        print(item)
        return item

    @staticmethod
    def process_content(content):
        # 处理content中的乱码字符和空字符串
        if content:
            content = "".join("".join([re.sub("\xa0", "", i) for i in content]).split())
        return content


class SNPipeline(object):
    def process_item(self, item, spider):
        item["name"] = item["name"].rstrip()
        item["author"] = "".join(item["author"].split()) if item["author"] else None
        item["press"] = "".join(item["press"].split()) if item["press"] else None
        print(item)
        return item


class SYPipeline(object):
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
        value = [item[i] for i in list(dict(item).keys())]
        try:
            sql1 = "replace into hospital values(%s,%s,%s,%s,%s,%s)"
            sql2 = "replace into doctor values(%s,%s,%s,%s,%s,%s,%s)"
            if item.__class__ == HospitalItem:
                self.cur.execute(sql1, value)
            elif item.__class__ == DoctorItem:
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


class JSPipeline(object):
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


class JSTwistedPipeline(object):
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


class SFPipeline(object):
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
        if item.__class__ == XFItem:
            fields1 = ["id", "province", "city", "community", "url", "price", "area", "district", "address", "sale"]
            for field in fields1:
                value.append(item[field])
        # elif item.__class__.startswith("EsfHouseItem"):
        elif item.__class__ == ESFItem or ESFItem02:
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






