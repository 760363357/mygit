import requests
import re
import jieba
from ..Model.predict import predict
from ..Model.train import Train
import numpy as np


class Info(object):
    requests.packages.urllib3.disable_warnings()
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'
    }

    def __init__(self, url):
        self.url = url
        self.text = self._get_text(self.url)
        print(self.text)
        self.title_compile = 'title>(.*?)</title>'
        self.origin_compile = "source: '(.*?)'"
        self.time_compile = "time: '(.*?)'"
        self.passages_counts_compile = '&lt;p&gt;'
        self.content_compile = '&lt;p&gt;(.*?)&lt'
        self.tid_thr = 0.2
        self.predict_dict = {
            '1': '汽车',
            '2': '财经',
            '3': 'IT',
            '4': '健康',
            '5': '体育',
            '6': '旅游',
            '7': '教育',
            '8': '军事',
            '9': '文化',
            '10': '娱乐',
            '11': '时尚'
        }

    def _get_text(self, url):
        res = requests.get(url, verify=False, headers=self.header)
        if res.status_code != 200:
            print('获取链接文本失败，请检查原因！')
            raise requests.HTTPError
        return res.text

    def get_title(self):
        return re.findall(self.title_compile, self.text)[0]

    def get_origin(self):
        return re.findall(self.origin_compile, self.text)[0]

    def get_time(self):
        return re.findall(self.time_compile, self.text)[0]

    def get_passages_counts(self):
        return len(re.findall(self.passages_counts_compile, self.text))

    def _get_content_text(self):
        symbol_key = ['，', '。', '！', '“', '”', '；', '？']
        text = re.findall(self.content_compile, self.text)
        text = ''.join(text)
        return re.subn('|'.join(symbol_key), '', text)[0]

    def get_count(self):
        return len(self._get_content_text())

    def get_keyword(self):
        res = list(jieba.cut(self._get_content_text()))
        res = Train.data_pre(Train.voc.vocabulary_, [' '.join(res)]).toarray()[0]
        sort_res = np.argsort(res)
        r = np.where(sort_res >= self.tid_thr)[0]
        if len(r) > 5:
            r = sort_res[-5:]
        item = Train.voc.vocabulary_.items()
        sort_word = list(sorted(item, key=lambda x: x[0]))
        return [sort_word[index][0] for index in reversed(r)]

    def get_predict(self):
        predict_num = predict([' '.join(jieba.cut(self._get_content_text()))])[0]
        return self.predict_dict[predict_num]


if __name__ == '__main__':
    i = Info('https://www.toutiao.com/a6547465138344034823/')
    # print(i.text)
    # print(i.get_title())
    # print(i.get_origin())
    # print(i.get_keyword())
    # print(i.get_predict())
