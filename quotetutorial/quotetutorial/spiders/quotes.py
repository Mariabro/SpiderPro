# -*- coding: utf-8 -*-
import scrapy

from quotetutorial.items import QuoteItem


class QuotesSpider(scrapy.Spider):
    name = 'quotes'   # name是用来唯一标识这个Spider的
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        # pass
        # print(response.text)
        quotes = response.css('.quote')
        for quote in quotes:
            item = QuoteItem()
            # ::text表示其中的文本，extract提取
            text = quote.css('.text::text').extract_first()   # 提取第一个结果
            author = quote.css('.author::text').extract_first()
            tags = quote.css('.tags .tag::text').extract()     # 提取所有的
            item['text'] = text
            item['author'] = author
            item['tags'] = tags
            yield item

        next = response.css('.pager .next a::attr(href)').extract_first()
        url = response.urljoin(next)
        yield scrapy.Request(url=url, callback=self.parse)  # 递归调用来实现循环下一页