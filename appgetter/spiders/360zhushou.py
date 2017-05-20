# -*- coding: utf-8 -*-

import os
import scrapy
import datetime
import time
from lxml import html
from appgetter.items import AppItem, AppTypeItem

class MultiSpiders(scrapy.Spider):
    global base_url
    global start_urls_
    name = '360zhushou'
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
                yield scrapy.Request(item['url'], self.parse_item, meta={'type_name': type_name, 'kind': kind})

    def parse_item(self,response):
        item = AppItem()
        type_name = response.meta['type_name']
        kind = response.meta['kind']
        if kind == 'application':
            order_dic={'newest' : '最新', 'weekdownload' : '综合', 'download' : '总榜', 'poll' : '好评'}
        else:
            order_dic = {'newest': '最新', 'weekpure': '综合', 'download': '总榜', 'poll': '好评'}
        cur_url = response.url
        for order in order_dic.keys():
            sep = os.sep
            linesep = os.linesep
            curdir = "360zhushou" + sep + kind + sep + type_name + sep + order_dic[order] + sep
            os.makedirs(curdir, 0o777, True)
            cur_time = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")
            f = open(curdir + cur_time + '.csv', 'w')
            for i in range(1, 51):
                time.sleep(0.1)
                url = cur_url + 'order/' + order + '/?page=' + str(i)
                res = html.parse(url)
                apps = res.xpath('//*[@id="iconList"]/li/h3/a/text()')
                f.write("####page=" + str(i) + "\n")
                for app in apps:
                    app = app.replace(",", " ")
                    f.write(app + linesep)
            f.close()


    # def parse_order(self, response):
    #     type_name = response.meta['type_name']
    #     kind = response.meta['kind']
    #     order_lists = response.xpath('/html/body/div[3]/div[2]/div/div[1]/div[2]/a')
    #     for order_list in order_lists:
    #         order_name = order_list.xpath('text()').extract()[0]
    #         order_url = order_list.xpath('@href').extract()[0]
    #         yield scrapy.Request(base_url + order_url, self.parse_type,
    #                              meta={'type_name': type_name, 'order_name': order_name, 'kind': kind})