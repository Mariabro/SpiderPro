# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.exceptions import DropItem


class TextPipeline(object):
    def __init__(self):
        self.limit = 50

    # pipelines要实现process_item方法，要么返回item，要么返回DropItem
    def process_item(self, item, spider):
        if item['text']:
            if len(item['text']) > self.limit:
                # [0:self.limit]切片处理
                item['text'] = item['text'][0:self.limit].rstrip() + '...'
            return item
        else:
            return DropItem('Missing Text')

# 保存到数据库
class MongoPipeline(object):

    def __init__(self, mongo_url, mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    # 爬虫启动时进行
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]

    # item插入到MongoDB
    def process_item(self,item,spider):
        name = item.__class__.__name__
        self.db[name].insert(dict(item))
        return item

    # 关闭mongo连接
    def close_spider(self,spider):
        self.client.close()