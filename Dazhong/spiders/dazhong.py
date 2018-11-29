# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from lxml import etree
from urllib.parse import urljoin
from ..items import DazhongItem
import time


class DazhongSpider(scrapy.Spider):
    name = 'dazhong'
    allowed_domains = ['m.dianping.com']
    url = 'https://m.dianping.com/awp/h5/hotel-dp/list/list.html?cityid=143&from=m_nav_3_jiudian'
    jsExecute = "var q=document.documentElement.scrollTop=%d"

    def start_requests(self):
        index = 0
        while True:
            value = index * 500
            execute = self.jsExecute % value
            index += 1
            if index == 30:
                break
            time.sleep(1)
            yield Request(url=self.url, callback=self.parse_response, meta={'js': execute}, dont_filter=True)

    def parse_response(self, response):
        if response.status == 200:
            doc = etree.HTML(response.body)
            items = doc.xpath('//div[@id="main"]//div[@class="list"]//div[@class="cell"]')
            for item in items:
                url_detail = urljoin(response.url, item.xpath('./a/@href')[0])
                time.sleep(1)
                yield Request(url=url_detail, callback=self.parse, meta={'js_detail': '123456'})

    def parse(self, response):
        if response.status == 200:
            doc = etree.HTML(response.body)
            item = DazhongItem()
            item['hotel_name'] = ''.join(doc.xpath('//div[@id="main"]/div[2]/div[1]/div[1]/span/text()'))
            roomsNum = doc.xpath('//div[@id="main"]/section[1]/div/div[3]/div[2]/span[2]/text()')
            if roomsNum:
                item['hotel_total_rooms'] = int(roomsNum[0])
            print(item)
            yield item
