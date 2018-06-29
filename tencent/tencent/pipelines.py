# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from .files.saver import Saver
from scrapy.exceptions import DropItem
import os

class TencentPipeline(object):
    def open_spider(self, spider):
        if spider.name != 'myspider':
            return None
        self.s = Saver()
        self.count = 0

    def process_item(self, item, spider):
        if spider.name != 'myspider':
            return item
        di = dict(item)
        di_1 = list(di['topic_id'].items())[0]
        print(di_1)
        di_2 = list(di['topic_link'].items())[0]
        d = {'id': self.count+1, 'topics': di_1[0],
             'topics_id': di_1[1],
             'topic': di_2[0],
             'link': di_2[1]}
        self.s.insert(d)
        if self.count % 50 == 0:
            self.s.save()

        self.count += 1
        return item

    def close_spider(self, spider):
        if spider.name != 'myspider':
            return None
        self.s.save()

class TopicPipeline(object):
    def open_spider(self, spider):
        if spider.name != 'question':
            return None
        self.file_num = 1
        self.s = Saver(info={
            'filename': 'topic_info' + str(self.file_num) + '.xls',
            'field': ['id', 'topic', 'follow_num', 'question_num', 'question', 'quest_link']
        })
        self.count = len(self.s.get()) + 1

    def process_item(self, item, spider):
        if spider.name != 'question':
            return item
        di = dict(item)
        print(di.keys())
        if 'topic_essence10' not in list(di.keys()):
            return item
        print('111111111111111')
        if len(self.s.get()) > 60000:
            self.file_num += 1
            self.s = Saver(info={
                'filename': 'topic_info' + str(self.file_num) + '.xls',
                'field': ['id', 'topic', 'follow_num', 'question_num', 'question', 'quest_link']
            })
            self.count = len(self.s.get()) + 1
        for ti in di['topic_essence10']:
            d = {'id': self.count,
                 'topic': di['topic'],
                 'follow_num': di['topic_follow_num'],
                 'question_num': di['topic_que_num'],
                 'question': ti[0],
                 'quest_link': ti[1]
                 }
            self.s.insert(d)
            # if self.count % 20 == 0:
            #     self.s.save()
            self.count += 1
        self.s.save()
        raise DropItem('已处理item', item)

    def close_spider(self, spider):
        if spider.name != 'question':
            return None
        self.s.save()

class AnswerPipeline(object):
    title = []
    dic = {}
    def open_spider(self, spider):
        if spider.name != 'deatil':
            return None
        self.count = 0
        self.se = Saver(info={
            'filename': 'detail_info' + str(self.count) + '.xls',
            'field': ['id', 'topic', 'mode', 'title', 'total_answer_num', 'follow_num', 'scan_num', 'answer_content']
        })
        self.count = len(self.se.get()) + 1
        self.current = os.listdir(r'D:\deatil/')

    def process_item(self, item, spider):
        if spider.name != 'deatil':
            return item
        di = dict(item)
        print(di.keys())
        if 'answer_content' not in list(di.keys()):
            return item
        print('**********************************************')
        dic = item['topics']
        ti = item['topic']
        if dic not in self.current:
            os.mkdir(r'D:\deatil/' + dic)
            self.current.append(dic)
            os.mkdir(r'D:\deatil/' + dic + '/' + ti)
        else:
            res = os.listdir(r'D:\deatil/' + dic)
            if ti not in res:
                os.mkdir(r'D:\deatil/' + dic + '/' + ti)
        if len(self.se.get()) > 60000:
            nu = 1
            self.se = Saver(info={
            'filename': 'detail_info' + str(nu) + '.xls',
            'field': ['id', 'topic', 'mode', 'title', 'total_answer_num', 'follow_num', 'scan_num', 'answer_content']
        })
            nu += 1
        if di['title'] not in self.title:
            self.dic[di['title']] = str(self.count)
            with open(r'D:\deatil/' + dic + '/' + ti + '/' + di['title'] + '.txt', 'w', encoding='utf-8') as fi:
                fi.write(','.join([str((content, num)) for content, num in di['answer_content']]) + ',')
            d = {
                'id': self.count,
                'topic': di['topic'],
                'mode': di['mode'],
                'title': di['title'],
                'total_answer_num': di['total_answer_num'],
                'follow_num': di['follow_num'],
                'scan_num': di['scan_num'],
                'answer_content': di['title'] + '.txt'
            }
            self.title.append(di['title'])
            self.se.insert(d)
            self.count += 1
            self.se.save()
        else:

            with open(r'D:\deatil/' + dic + '/' + ti + '/' + di['title'] + '.txt', 'a+', encoding='utf-8') as fi:
                fi.write(','.join([str((content, num)) for content, num in di['answer_content']]) + ',')

            # res = self.se.get({'title': di['title']})[0]
            # print('更新数据：', res)
            # res['answer_content'] = list(res['answer_content'])
            # res['answer_content'] = str(res['answer_content'].extend(di['answer_content']))
            # self.se.update(res, {'title': di['title']})

        raise DropItem('已处理该item: ', item)

    def close_spider(self, spider):
        if spider.name != 'deatil':
            return None
        self.se.save()
