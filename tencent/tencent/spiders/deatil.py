# -*- coding: utf-8 -*-
import scrapy
import re
from ..files.saver import Saver
import json
from ..items import AnserwItem
from ..files.hand_file import cookies

class GetUrl(object):
    @classmethod
    def get_all(cls):
        s = Saver(info={
            'filename': 'que_info1.xls',
            'field': ['id', 'topic', 'follow_num', 'question_num', 'question', 'quest_link']
        })
        return s.get()

    @classmethod
    def get_topic(cls):
        s = Saver(info={
            'filename': 'topics1.xls',
            'field': ['id', 'topics', 'topics_id', 'topic', 'link']
        })
        return s.get()

class DeatilSpider(scrapy.Spider):
    name = 'deatil'
    allowed_domains = ['zhihu.com']
    start_urls = [[x['topic'], x['quest_link']] for x in GetUrl.get_all()]
    topics = {x['topic']: x['topics'] for x in GetUrl.get_topic()}
    # cookies = {
    #     'd_c0': "ADBlgM5Htg2PTp0qFkzt5K09UOIoNdN08C4=|1528350936"
    # }


    def start_requests(self):
        count = 1
        for url in self.start_urls:
            if 'question' in url[1]:
                mode = 'question'
            else:
                mode = 'article'
            yield scrapy.Request(url[1],cookies=cookies, callback=self.parse_id, headers={'referer':'https://www.zhihu.com/topic/' + url[1].split('/')[-1] + '/top-answers'}, meta={
                'topic': url[0],
                'cookiejar': 1,
                'id': url[1].split('/')[-1],
                'mode': mode,
                'topics': self.topics.get(url[0], 'unknow')
            }, )
            count += 1

    def parse(self, response):
        pass

    def parse_id(self, response):
        '''
        如果是文章，则获取赞数以及文章内容。如果是问题则获取问题的关注数和浏览数并发出获取回答的请求
        :param response:
        :return:
        '''

        mode = response.meta['mode']
        topic = response.meta['topic']
        if mode == 'article':
            item = AnserwItem()
            try:
                app_gree = re.findall('Button Button--plain">(.*?) 人', response.body.decode())[0].replace(',', '')
            except:
                with open('./erro_url', 'a+') as fi:
                    fi.write(response.url)
                print('erro_url', response.url)
                app_gree = 0
            res = re.subn('<.*?>', '', response.body.decode())[0]
            item['topic'] = topic
            item['title'] = response.meta['id']
            item['follow_num'] = '-1'
            item['scan_num'] = '-1'
            item['total_answer_num'] = '-1'
            item['answer_content'] = [(res, app_gree)]
            item['mode'] = 'article'
            item['topics'] = response.meta['topics']
            print('文章的关注数：', app_gree)
            # print('文章内容: ', res)
            yield item
        else:
            try:
                anwser_url = re.findall('previous&quot;:&quot;(.*?)&quot;,&quot;next', response.body.decode())[0].replace('limit=5', 'limit=10')
            except:
                with open(r'C:\Users\PYTHON\Desktop\service\tencent/' + 'erro_url.txt', 'a+') as fi:
                    fi.write(response.url + '\n')
                print('erro_url:', response.url)
                return None
            try:
                anwser_url = anwser_url.replace('http://', 'https://')
            except:
                pass
            try:
                anwser_num = re.findall('List-headerText"><span>(.*?)<!', response.body.decode())[0].replace(',', '')
                num = re.findall('NumberBoard-itemValue" title="(.*?)"', response.body.decode())
                follow_num = num[0]
                scan_num = num[1]
                print('问题关注数：', follow_num)
                print('问题浏览数：', scan_num)
            except:
                with open('./erro_url', 'a+') as fi:
                    fi.write(response.url)
                return None
            yield scrapy.Request(anwser_url, callback=self.anwser_parse,cookies=cookies,
                                 meta={'anwser_num': int(anwser_num),
                                       'current_num': 0,
                                       'follow_num': follow_num,
                                       'scan_num': scan_num,
                                       'topic': response.meta['topic'],
                                       'id': response.meta['id'],
                                       'topics': response.meta['topics'],
                                       'cookiejar': response.meta['cookiejar']
                                       })

    def anwser_parse(self, response):
        item = AnserwItem()
        num = response.meta['anwser_num']
        current = response.meta['current_num']
        scan_num = response.meta['scan_num']
        follow_num = response.meta['follow_num']
        topic = response.meta['topic']
        title = response.meta['id']
        l = re.findall('limit=(\d*)', response.url)[0]
        if current + int(l) < num:
            res = response.url.replace('offset=%    s' % current, 'offset=%s' % (current+int(l)))
            current += int(l)

            yield scrapy.Request(res, callback=self.anwser_parse,cookies=cookies,
                                 meta={'anwser_num': num,
                                       'current_num': current,
                                       'follow_num': follow_num,
                                       'scan_num': scan_num,
                                       'topic': topic,
                                       'id': response.meta['id'],
                                       'topics': response.meta['topics'],
                                       'cookiejar': response.meta['cookiejar']
                                       })
            print(res)

        ans = json.loads(response.body.decode())['data']
        content = []
        for a in ans:
            text = re.subn('<.*?>', '', a['content'])[0]
            app_gree = a['voteup_count']
            print('回答的赞数：', app_gree)
            # print('回答的内容：', text)
            content.append((text, app_gree))
        item['topic'] = topic
        item['title'] = title
        item['follow_num'] = follow_num
        item['scan_num'] = scan_num
        item['total_answer_num'] = num
        item['answer_content'] = content
        item['mode'] = 'question'
        item['topics'] = response.meta['topics']
        yield item