# -*- coding: utf-8 -*-
import scrapy


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    # custom_settings = {
    #     'DEFAULT_REQUEST_HEADERS' : {
    #         'User-Agent': None,
    #         'Accept-Language': 'en',
    #     }
    # }

    def __init__(self, mongo_url, mongo_db, *args, **kwargs):
        super(ZhihuSpider, self).__init__(*args, **kwargs)
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def parse(self, response):
        pass
