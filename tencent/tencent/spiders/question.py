# -*- coding: utf-8 -*-
import scrapy
from ..files.saver import Saver
from ..items import StatItem
from ..items import AnserwItem
import json
import re



class GetUrl(object):
    @classmethod
    def get_all(cls):
        s = Saver()
        return s.get()

    @classmethod
    def erro_url(cls):
        with open(r'C:\Users\PYTHON\Desktop\service\tencent/1.txt', 'r') as fi:
            f = fi.read().split('\n')[:-1]
        for url in range(len(f)):
            if 'top-answers' not in f[url]:
                f[url] += '/top-answers'
        return f

class QuestionSpider(scrapy.Spider):
    name = 'question'
    allowed_domains = ['zhihu.com']
    question_url = 'https://www.zhihu.com/question/'   # + 问题id
    link_info = [(a['topic'], a['link']) for a in GetUrl.get_all()]
    # link_info = GetUrl.erro_url()
    # print(len(link_info))
    # print(link_info)
    # start_urls = [link[1] for link in link_info[:1]]
    # start_urls = ['http://httpbin.org/ip']
    # print(start_urls)
    # print(len(start_urls))

    def start_requests(self):
        self.num = 1
        for url in self.link_info:
            yield scrapy.Request(url[1], dont_filter=False, meta={'cookiejar': str(self.num),
                                                                      'topic': url[0]})
        # for url in self.link_info:
        #     yield scrapy.Request(url, dont_filter=False, meta={'cookiejar': str(self.num)})
            self.num += 1

    def parse(self, response):
        '''
        通过小话题url来获取关注人数，问题数item以及发出获得10个问题请求
        :param response:
        :return:
        '''
        # print(response.meta['topic'])
        # topic = response.xpath('//h1/text()').extract_first()
        try:
            que_url = re.findall('next&quot;:&quot;(.*?)&quot;', response.body.decode())[0].replace('limit=5', 'limit=10').replace('offset=5', 'offset=0')
            print(que_url)
        except:
            with open(r'C:\Users\PYTHON\Desktop\service\tencent/' + 'erro_url.txt', 'a+') as fi:
                fi.write(response.url + '\n')
            print('erro_url:', response.url)
            return None
        try:
            que_url = que_url.replace('http://', 'https://')
        except:
            pass
        # print(que_url)
        num = response.selector.re('class="NumberBoard-itemValue" title="(.*?)"')
        people_num = num[0]
        question_num = num[1]
        print('话题关注人数：', people_num)
        print('问题数：', question_num)
        yield scrapy.Request(que_url, callback=self.que_parse, meta={'people_num': people_num,
                                                                     'question_num': question_num,
                                                                     'topic': topic, # response.meta['topic'],
                                                                     'cookiejar': response.meta['cookiejar']},
                             dont_filter=False
                             )
        # print(response.body.decode())

    def que_parse(self, response):
        '''
        发出具体问题的请求或者文章请求。
        :param response:
        :return:
        '''
        topic_item = StatItem()
        title_list = []
        data = json.loads(response.body.decode())['data']
        print('获得的问题数：', len(data))
        for d in data:
            que = d['target'].get('question', 'erro')
            if que == 'erro':
                title = d['target'].get('title', '这个既不是问题也不是文章')
                title_url = d['target'].get('url', '这个既不是问题也不是文章')
                if title == '这个既不是问题也不是文章' or title_url == '这个既不是问题也不是文章':
                    print('获取问题url错误')
                    raise TypeError
            else:
                title = que['title']
                title_url = que['url']
            if 'question' in title_url:
                que_id = title_url.split('/')[-1]
                # print(que_id)
                assert que_id
                title_url = self.question_url+que_id
                # yield scrapy.Request(self.question_url+que_id, callback=self.parse_id,
                #                      meta={'modes': 'question',
                #                            'topic': response.meta['topic'],
                #                            'title': title}, dont_filter=False)
            else:
                try:
                    title_url = title_url.replace('http://', 'https://')
                except:
                    pass
                # yield scrapy.Request(title_url, callback=self.parse_id,
                #                      meta={'modes': 'article',
                #                            'topic': response.meta['topic'],
                #                            'title': title}, dont_filter=False)
            title_list.append((title, title_url))
            print('标题：', title)
            print('标题url：', title_url)
        # print(response.meta['topic'])
        topic_item['topic'] = response.meta['topic']
        topic_item['topic_follow_num'] = response.meta['people_num']
        topic_item['topic_que_num'] = response.meta['question_num']
        topic_item['topic_essence10'] = title_list
        yield topic_item
        # print(response.body.decode())

    def parse_id(self, response):
        '''
        如果是文章，则获取赞数以及文章内容。如果是问题则获取问题的关注数和浏览数并发出获取回答的请求
        :param response:
        :return:
        '''

        mode = response.meta['modes']
        topic = response.meta['topic']
        if mode == 'article':
            title = response.meta['title']
            item = AnserwItem()
            app_gree = response.selector.re('Button Button--plain">(.*?) 人')[0].replace(',', '')
            res = re.subn('<.*?>', '', response.body.decode())[0]
            item['topic'] = topic
            item['title'] = title
            item['follow_num'] = '-1'
            item['scan_num'] = '-1'
            item['total_answer_num'] = '-1'
            item['answer_content'] = [(res, app_gree)]
            item['mode'] = 'article'
            print('文章的关注数：', app_gree)
            print('文章内容: ', res)
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
            anwser_num = response.selector.re('List-headerText"><span>(.*?)<!')[0].replace(',', '')
            num = response.selector.re('NumberBoard-itemValue" title="(.*?)"')
            follow_num = num[0]
            scan_num = num[1]
            print('问题关注数：', follow_num)
            print('问题浏览数：', scan_num)
            yield scrapy.Request(anwser_url, callback=self.anwser_parse,
                                 meta={'anwser_num': int(anwser_num),
                                       'current_num': 0,
                                       'follow_num': follow_num,
                                       'scan_num': scan_num,
                                       'topic': response.meta['topic'],
                                       'title': response.meta['title']
                                       }, dont_filter=False)

    def anwser_parse(self, response):
        item = AnserwItem()
        num = response.meta['anwser_num']
        current = response.meta['current_num']
        scan_num = response.meta['scan_num']
        follow_num = response.meta['follow_num']
        topic = response.meta['topic']
        title = response.meta['title']
        if current + 10 < num:
            res = response.url.replace('offset=%s' % current, 'offset=%s' % (current+10))
            current += 10

            yield scrapy.Request(res, callback=self.anwser_parse,
                                 meta={'anwser_num': num,
                                       'current_num': current,
                                       'follow_num': follow_num,
                                       'scan_num': scan_num,
                                       'topic': topic,
                                       'title': title
                                       }, dont_filter=False)
            print(res)

        ans = json.loads(response.body.decode())['data']
        content = []
        for a in ans:
            text = re.subn('<.*?>', '', a['content'])[0]
            app_gree = a['voteup_count']
            print('回答的赞数：', app_gree)
            print('回答的内容：', text)
            content.append((text, app_gree))
        item['topic'] = topic
        item['title'] = title
        item['follow_num'] = follow_num
        item['scan_num'] = scan_num
        item['total_answer_num'] = num
        item['answer_content'] = content
        item['mode'] = 'question'
        yield item