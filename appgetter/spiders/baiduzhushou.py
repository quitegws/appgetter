#encoding=utf-8

import scrapy
import os
import datetime
import time
import csv
import requests
import logging
from lxml import html

class BaiduZhushouSpider(scrapy.Spider):
    name = 'bdzscrawler'
    allowed_domains = ['shouji.baidu.com']
    start_urls = ['http://shouji.baidu.com/software/501/']

    def parse(self, response):
        pass
        kind = response.xpath('//*[@id="doc"]/div[2]/div/div/ul/li/a')
        for x in kind:
            kind_name = x.xpath('text()').extract()[0]
            kind_link = x.xpath('@href').extract()[0]
            yield scrapy.Request('http://shouji.baidu.com' + kind_link, self.parse_kind, meta={'kind': kind_name})

    def parse_kind(self, response):
        kind = response.meta['kind']
        sub_kind = response.xpath('//*[@id="doc"]/div[3]/div[1]/ul/li[position()>1]/a')
        for x in sub_kind:
            sub_kind_name = x.xpath('text()').extract()[0]
            sub_kind_link = x.xpath('@href').extract()[0]
            yield scrapy.Request('http://shouji.baidu.com' + sub_kind_link, self.parse_sub_kind, meta={
                'kind':kind, 'sub_kind':sub_kind_name
            })

    def parse_sub_kind(self, response):
        cur_url = response.url
        # if str(cur_url).endswith('/'):
        #     cur_url = str(cur_url)[:-1]
        kind = response.meta['kind']
        sub_kind = response.meta['sub_kind']
        page_lists_links = []

        next_page_links = response.xpath('//*[@id="doc"]/div[3]/div[2]/ul/li/a/@href').extract()
        for next_page_link in next_page_links:
            if next_page_link not in page_lists_links:
                page_lists_links.append(next_page_link)

        curdir = 'shoujibaidu/' + kind + '/' + sub_kind + '/'
        os.makedirs(curdir, 0o777, True)
        time = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")
        f = open(curdir + time + '.csv', 'w')
        # writer = csv.writer(f)

        for u in page_lists_links:
            url = cur_url + u
            res = html.parse(url)

            apps = res.xpath('//*[@id="doc"]/div[3]/div[1]/div/ul/li/a/div[1]/p[1]')

            for app in apps:
                try:
                    app_names = app.xpath('text()')
                    if app_names:
                        app_name = app.xpath('text()')[0]
                except Exception as e:
                    logging(e)
                    app_name = 'null'
                f.write(app_name + '\n')
                # writer.writerow([app_name])

        f.close()