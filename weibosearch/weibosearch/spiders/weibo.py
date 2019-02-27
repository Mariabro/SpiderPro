# -*- coding: utf-8 -*-
import re

from scrapy import Spider, FormRequest, Request

from weibosearch.items import WeiboItem
import tushare as ts

class WeiboSpider(Spider):
    name = 'weibo'
    allowed_domains = ['weibo.cn']
    search_url = 'http://weibo.cn/search/mblog'
    max_page = 100  # 最多发送100次请求

    def start_requests(self):
        result = ts.get_hs300s()
        keywords = result['code'].tolist()
        for keyword in keywords:
        # keyword = '000001'  # 搜索关键字,中国平安的股票代号
            url = '{url}?keyword={keyword}'.format(url=self.search_url, keyword=keyword)    # 构造新的url
            for page in range(self.max_page+1):
                data = {
                    'mp': str(self.max_page),
                    'page': str(page)
                }
                yield FormRequest(url, callback=self.parse_index, formdata=data, meta={'keyword': keyword})   # FormRequest是一个Scrapy中的类

    def parse_index(self, response):
        weibos = response.xpath('//div[@class="c" and contains(@id, "M_")]')
        print(weibos)  # weibos返回的是一个一个Selector

        for weibo in weibos:
            # 如果是转发的会含有cmt
            is_forward = bool(weibo.xpath('.//span[@class="cmt"]').extract_first())
            print(is_forward)
            if is_forward:
                # contains括号里的.表示当前的文本
                detail_url = weibo.xpath('.//a[contains(.,"原文评论[")]//@href').extract_first()
            else:
                detail_url = weibo.xpath('.//a[contains(.,"评论[")]//@href').extract_first()
            print(detail_url)
            yield Request(detail_url, callback=self.parse_detail, meta={'keyword': response.meta['keyword']})

    def parse_detail(self, response):
        id = re.search('comment\/(.*?)\?', response.url).group(1)
        url = response.url
        content = ''.join(response.xpath('//div[@id="M_"]//span[@class="ctt"]//text()').extract())
        print(id, url, content)
        comment_count = response.xpath('//span[@class="pms"]//text()').re_first('评论\[(.*?)\]')
        forward_count = response.xpath('//a[contains(.,"转发[")]//text()').re_first('转发\[(.*?)\]')
        like_count = response.xpath('//a[contains(.,"赞[")]').re_first('赞\[(.*?)\]')
        print(comment_count, forward_count, like_count)
        posted_at = response.xpath('//div[@id="M_"]//span[@class="ct"]//text()').extract_first(default=None)
        user = response.xpath('//div[@id="M_"]/div[1]/a/text()').extract_first(default=None)
        print(posted_at, user)
        keyword = response.meta['keyword']
        weibo_item = WeiboItem()
        for field in weibo_item:
            try:
                weibo_item[field] = eval(field)
            except NameError:
                self.logger.debug('Field is Not Defined: ' + field)
        yield weibo_item