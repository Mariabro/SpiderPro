# -*- coding: utf-8 -*-
import json

import re

from scrapy import Spider, Request
from zhihuuser.items import UserItem

class ZhihuSpider(Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    start_user = 'excited-vczh'

    # 用{}表示一个变量
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'

    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follows_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        # 两个接口：
        # 用户的详细信息
        # url = 'https://www.zhihu.com/api/v4/members/liao-wu-hen-54?include=allow_message%2Cis_followed%2Cis_following%2Cis_org%2Cis_blocking%2Cemployments%2Canswer_count%2Cfollower_count%2Carticles_count%2Cgender%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'
        # 关注列表
        # url = 'https://www.zhihu.com/api/v4/members/excited-vczh/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=60&limit=20'
        yield Request(self.user_url.format(user=self.start_user, include=self.user_query), self.parse_user)  # 构造一个动态的url
        yield Request(self.follows_url.format(user=self.start_user, include=self.follows_query, offset=0, limit=20), callback=self.parse_follows)

    def parse_user(self, response):
        result = json.loads(response.text)
        item = UserItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield field
        # 进行循环往复
        # yield Request(self.follows_url.format(user=result.get('url_token'), include=self.follows_query, limit=20, offset=0), callback=self.parse_follows)

    def parse_follows(self, response):
        results = json.loads(response.text)
        print('---------------------------------------------------------')
        if 'data' in results:
            for result in results['data']:
                print('***************')
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query), self.parse_user)
        # 判断一下是否在keys以及判断是否是最后一页，如果是最后一页的话，就不需要再分页了
        if 'paging' in results and results.get('paging').get('is_end') == False:
            print('不是最后一页-------------------------')
            next_page = results.get('paging').get('next')
            print('+++++++++++++++++++++++++++++++++')
            # print('---------------'+next_page+'---------------')
            yield Request(url=next_page, callback=self.parse_follows)