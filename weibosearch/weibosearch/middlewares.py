# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import json
import logging

import requests

from requests.exceptions import ConnectionError
from scrapy.exceptions import IgnoreRequest


class CookiesMiddleware():

    # Scrapy中很少用到print，一般使用logger
    def __init__(self, cookies_pool_url):
        self.logger = logging.getLogger(__name__)
        self.cookies_pool_url = cookies_pool_url
    # 定义一个私有方法
    def _get_random_cookies(self):
        try:
            response = requests.get(self.cookies_pool_url)
            if response.status_code == 200:
                return json.loads(response.text)
        except ConnectionError:
            return None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            cookies_pool_url = crawler.settings.get('COOKIES_POOL_URL')
        )

    def process_request(self, request, spider):
        cookies = self._get_random_cookies()
        if cookies:
            request.cookies = cookies
            self.logger.debug('Using Cookies' + json.dumps(cookies))    # 利用json.dumps把cookies转换成字符串
        else:
            self.logger.debug('No Valid Cookies')

    # 因为微博反爬机制比较强，所以需要在中间件写一些东西
    # 实现了process_response表示对response做处理
    def process_response(self, request, response, spider):
        # 如果状态码在300以上，说明cookie已经失效
        if response.status in [300,301,302,303]:
            try:
                redirect_url = response.headers['location']
                if 'passport' in redirect_url:  # cookie失效
                    self.logger.warning('Need Login, Updating Cookies')
                elif 'weibo.cn/security' in redirect_url:   # 封号
                    self.logger.warning('Account is locked!')
                # 如果cookie失效，重新取出一个cookie进行替换
                request.cookies = self._get_random_cookies()
                return request
            except:
                raise IgnoreRequest
        elif response.status in [414]:
            return request
        else:
            return response
