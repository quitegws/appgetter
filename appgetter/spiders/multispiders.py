# -*- coding: utf-8 -*-

import os
import scrapy
import datetime
import time
from appgetter.items import AppItem, AppTypeItem
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.selector import Selector

class MultiSpiders(scrapy.Spider):
    global base_url
    global start_urls_
    name = 'zhushou360'
    allowed_domains = ["zhushou.360.cn"]
    base_url = 'http://zhushou.360.cn'
    start_urls_ = {'game': 'http://zhushou.360.cn/list/index/cid/2',
                   'application': 'http://zhushou.360.cn/list/index/cid/1'}

    def start_requests(self):

        for kind in start_urls_:
            yield scrapy.Request(start_urls_[kind], self.parse, meta={'kind': kind})

    def parse(self, response):
        item = AppTypeItem()
        sel=response.xpath('/html/body/div[3]/div[2]/div/ul/li[1]/a')
        kind = response.meta['kind']
        for selector in sel:
            type_url = selector.xpath('@href').extract()[0]
            type_name = selector.xpath('text()').extract()[0]
            item['name'] = type_name
            item['url'] = base_url+type_url
            if item['url'] not in start_urls_.values():
                yield scrapy.Request(item['url'], self.parse_order, meta={'type_name': type_name, 'kind': kind})

    def parse_order(self, response):
        type_name = response.meta['type_name']
        kind = response.meta['kind']
        order_lists = response.xpath('/html/body/div[3]/div[2]/div/div[1]/div[2]/a')
        for order_list in order_lists:
            order_name = order_list.xpath('text()').extract()[0]
            order_url = order_list.xpath('@href').extract()[0]
            yield scrapy.Request(base_url + order_url, self.parse_type,
                                 meta={'type_name': type_name, 'order_name': order_name, 'kind': kind})

    def parse_type(self,response):
        cur_url = response.url
        item = AppItem()
        type_name = response.meta['type_name']
        order_name = response.meta['order_name']
        kind = response.meta['kind']
        apps = response.xpath('//*[@id="iconList"]/li')

        curdir = "360zhushou/" + kind + '/' + type_name + '/' + order_name + '/'
        os.makedirs(curdir, 0o777, True)
        time = datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S")
        f = open(curdir + time + '.csv', 'w')

        for i  in range(1,50):
            pass

        for app in apps:
            app_name = app.xpath('h3/a/text()').extract()[0]
            item['name'] = app_name
            f.write(app_name + "\n")
            print(kind, type_name, order_name, time, '-------->', app_name)
            # yield scrapy.Request(item['url'], self.parse_type, meta={'type_name': type_name})
        f.close()