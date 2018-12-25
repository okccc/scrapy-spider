# -*- coding: utf-8 -*-
"""
ItemLoader: 替代杂乱的extract()/get(),简化代码便于维护提高复用率,并且可以使用processors对字段值做进一步的函数处理
数据提取方法：
add_xpath(): 通过xpath表达式提取
add_css(): 通过css表达式提取
add_value(): 给杂务字段设置值

常用processors：
MapCompose(float)：将字符串转化为数字
MapCompose(str.strip, str.title, str.upper)：去除空格,单词首字母大写,转换大小写
MapCompose(lambda i: i.replace(',', ''), float)：将字符串转化为数字,逗号替换为空格
MapCompose(lambda i: urlparse.urljoin(response.url, i))：合并url
MapCompose(remove_tags, udf): 去除html标签,再调用自定义函数进一步处理
Identity(): 返回原值
Join()：合并多个结果
TakeFirst(): 返回第一个非空/None值
总结：MapCompose()适合input_processor,其它的适合output_processor

数据流向(debug)：add_xpath(会调用input_processor处理,数据暂存在ItemLoader中) --> load_item(会调用output_processor处理) --> item
"""

import scrapy
# 导入scrapy加载器
from scrapy.loader import ItemLoader
# 导入scrapy内置处理器
from scrapy.loader.processors import MapCompose, TakeFirst, Join, Identity
# 导入去除html标签的函数
from w3lib.html import remove_tags


# 自定义ItemLoader类
class MyItemLoader(ItemLoader):
    # add_xpath()获取Field填充数据后设置默认input_processor给字符串去空格
    default_input_processor = MapCompose(lambda s: s.strip())
    # load_item()传值给Item后设置默认output_processor输出列表的第一个非空/None值
    default_output_processor = TakeFirst()


def deal_tab(value):
    # 处理字符串中间的空格(strip只能去除字符串两边的空格)
    return "".join(value.split())


def deal_district(value):
    return value.split()[0]


class NewHouseItem(scrapy.Item):
    # 构建Item模型(类似ORM对象关系映射)：用来定义结构化数据字段,保存爬取到的数据,类似python的dict
    id = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()
    community = scrapy.Field(
        # input_processor=MapCompose(str.strip)
    )
    url = scrapy.Field()
    price = scrapy.Field(
        # input_processor=MapCompose(remove_tags, deal_tab)
    )
    area = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal_tab)
    )
    district = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal_district)
    )
    address = scrapy.Field()
    sale = scrapy.Field()


def deal_rooms(value):
    tmp = "".join(value.split()).split("|")
    if len(tmp) >= 1:
        return tmp[0]

def deal__floor(value):
    tmp = "".join(value.split()).split("|")
    if len(tmp) >= 2:
        return tmp[1]

def deal_toward(value):
    tmp = "".join(value.split()).split("|")
    if len(tmp) >= 3:
        return tmp[2]

def deal_year(value):
    tmp = "".join(value.split()).split("|")
    if len(tmp) >= 4:
        return tmp[3]


class EsfHouseItem(scrapy.Item):
    province = scrapy.Field()
    city = scrapy.Field()
    community = scrapy.Field()
    title = scrapy.Field()
    address = scrapy.Field()
    rooms = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal_rooms)
    )
    floor = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal__floor)
    )
    toward = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal_toward)
    )
    year = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal_year)
    )
    area = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal_tab)
    )
    price = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal_tab)
    )
    unit = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal_tab)
    )


def deal_rooms02(value):
    tmp = "".join(value.split()).split("|")
    if len(tmp) >= 1:
        return tmp[0]

def deal_area(value):
    tmp = "".join(value.split()).split("|")
    if len(tmp) >= 2:
        return tmp[1]

def deal_floor02(value):
    tmp = "".join(value.split()).split("|")
    if len(tmp) >= 3:
        return tmp[2]

def deal_toward02(value):
    tmp = "".join(value.split()).split("|")
    if len(tmp) >= 4:
        return tmp[3]

def deal_year02(value):
    tmp = "".join(value.split()).split("|")
    if len(tmp) >= 5:
        return tmp[4]


class EsfHouseItem02(scrapy.Item):
    province = scrapy.Field()
    city = scrapy.Field()
    community = scrapy.Field()
    title = scrapy.Field()
    address = scrapy.Field()
    rooms = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal_rooms02)
    )
    floor = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal_floor02)
    )
    toward = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal_toward02)
    )
    year = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal_year02)
    )
    area = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal_area)
    )
    price = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal_tab)
    )
    unit = scrapy.Field(
        input_processor=MapCompose(remove_tags, deal_tab)
    )


class HospitalItem(scrapy.Item):
    # 医院编号
    id = scrapy.Field()
    # 医院名称
    name = scrapy.Field()
    # 医院资质
    aptitude = scrapy.Field()
    # 医院地址
    address = scrapy.Field()
    # 医院擅长项目
    skilled = scrapy.Field()
    # 写入时间
    insert_time = scrapy.Field()


class DoctorItem(scrapy.Item):
    # 医生编号
    id = scrapy.Field()
    # 医生名字
    name = scrapy.Field()
    # 医生所在医院编号
    hospital_id = scrapy.Field()
    # 医生所在医院名称
    hospital_name = scrapy.Field()
    # 医生职称职务
    title = scrapy.Field()
    # 医生擅长项目
    skilled = scrapy.Field()
    # 写入时间
    insert_time = scrapy.Field()


class JianshuspiderItem(scrapy.Item):
    id = scrapy.Field()  # 编号
    title = scrapy.Field()  # 标题
    link = scrapy.Field()  # 链接
    author = scrapy.Field()  # 作者
    pubtime = scrapy.Field()  # 出版时间
    content = scrapy.Field()  # 内容
    readings = scrapy.Field()  # 阅读数
    comments = scrapy.Field()  # 评论数
    subjects = scrapy.Field()  # 专题(该字段需要使用selenium模拟浏览器点击标签)


class SunwzspiderItem(scrapy.Item):
    """
    需求：抓取http://wz.sun0769.com/index.php/question/questionType?type=4网站每个帖子信息
    """

    # 编号
    id = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 链接
    link = scrapy.Field()
    # 状态
    status = scrapy.Field()
    # 网友
    netizen = scrapy.Field()
    # 时间
    time = scrapy.Field()
    # 内容
    content = scrapy.Field()


class TencentspiderItem(scrapy.Item):
    """
    需求：抓取http://hr.tencent.com/position.php?&start=0#a职位数据
    """

    # define the fields for your item here like:

    # 职位名称
    name = scrapy.Field()
    # 详细链接
    detailLink = scrapy.Field()
    # 职位类别
    sort = scrapy.Field()
    # 招聘人数
    num = scrapy.Field()
    # 上班地点
    site = scrapy.Field()
    # 发布时间
    publishTime = scrapy.Field()


