# -*- coding: utf-8 -*-
import scrapy
import re
import json
from ..files.hand_file import cookies
from ..items import TencentItem


class TempData(object):
    def __init__(self):
        # 大话题： id
        self.topic = {}
        # 小话题：连接
        self.topic_link = {}


class MyspiderSpider(scrapy.Spider):
    name = 'myspider'
    allowed_domains = ['zhihu.com']
    interface_url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
    base_url = 'https://www.zhihu.com'
    start_urls = ['https://www.zhihu.com/topics']
    t = TempData()
    print('取到的cookies是：', cookies)
    srftoken = cookies['_xsrf']

    def start_requests(self):
        for i in self.start_urls:
            yield scrapy.Request(i, callback=self.parse, cookies=cookies, meta={'cookie_jar': 1})

    def parse(self, response):
        offset = 0
        title = response.xpath('//li[@class="zm-topic-cat-item"]/a/text()').extract()
        title_id = response.xpath('//ul[@class="zm-topic-cat-main clearfix"]/li/@data-id').extract()
        id_hash = re.findall('"user_hash":"(.*?)"', response.body.decode())[0]

        # print(response.body.decode())
        assert len(title) == len(title_id)
        for num in range(len(title)):
            self.t.topic[title[num]] = title_id[num]
        # print(self.t.topic)
        # print(id_hash)
        for top_key in self.t.topic:
            data = {
                'method': 'next',
                'params': json.dumps({"topic_id":int(self.t.topic[top_key]), "offset": offset, "hash_id": id_hash})
            }
            # print(id_hash)
            yield scrapy.FormRequest(url=self.interface_url,
                                     formdata=data,
                                     callback=self.par_offset,
                                     headers={'x-xsrftoken':self.srftoken},
                                     meta={'id_hash':id_hash,
                                           # 'topic': 1761,
                                           'topic':int(self.t.topic[top_key]),
                                           'offset':offset})
    def par_offset(self, response):

        item = TencentItem()
        res_json = json.loads(response.body.decode())
        msg = res_json.get('msg')
        id_hash = response.meta['id_hash']
        topic = response.meta['topic']
        mkey = ''
        for key in self.t.topic:
            if topic == int(self.t.topic[key]):
                mkey = key
                break
        # data = response.meta['data']
        # print(msg[0])
        # print(msg)
        for m in msg:
            title = re.findall('<strong>(.*?)</strong>', m)[0]
            link = re.findall('href="(.*?)"', m)[0]
            self.t.topic_link[title] = self.base_url + link + '/top-answers'
            # print(self.t.topic_link[title])
            item['topic_id'] = {mkey: self.t.topic[mkey]}
            item['topic_link'] = {title: self.t.topic_link[title]}
            yield item
        if len(msg):
            offset = response.meta['offset'] + len(msg)
            data = {
                'method': 'next',
                'params': json.dumps({"topic_id": topic, "offset": offset, "hash_id": id_hash})
            }

            yield scrapy.FormRequest(url=self.interface_url,
                                     formdata=data,
                                     callback=self.par_offset,
                                     headers={'x-xsrftoken':self.srftoken},
                                     meta={'id_hash':id_hash,
                                           'topic':topic,
                                           'offset':offset})
            print(data)

    def parse_topic(self, response):
        pass

        # print(title)
        # print(title_id)
        # print(response.body.decode())
