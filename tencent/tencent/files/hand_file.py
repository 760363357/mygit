from .saver import Saver
import random
# js = {}
# s = 'd_c0="ADBlgM5Htg2PTp0qFkzt5K09UOIoNdN08C4=|1528350936"; q_c1=583cd44958244181a7d61291443fb412|1528350936000|1528350936000; _zap=d4cb7680-0167-40b8-93bb-c2979fac92e0; l_cap_id="Mjg0NmIxNDY3NjM0NGE0MDgxYTRlMGRiNjNkYzZmMjA=|1528987559|c6573f3ae987b380bfb0fa0f828d69792d3b9d02"; r_cap_id="ZWJkNjc0YWVlNDFmNGU4ZGJhMTUwZGQzMTRmNjQ4NTg=|1528987559|af85731ed8395b383cdf8c1921ad1aa530e9e518"; cap_id="ZTJhMDgxMDdlYzZiNDI4ZjlmYzJhZTA5ZjljOTllZjg=|1528987559|d2335322f080a3df509f53ec28e04a77a5beddb8"; _xsrf=d1b81b2f-30d1-4957-a28d-070df219755a; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1; capsion_ticket="2|1:0|10:1529069386|14:capsion_ticket|44:NDgzMTJlYjkzMDY3NGZkMWJiZDM0MzgzYjBjMmNkNjI=|c7af7b8d91dee390cf1ef2b0982d2954dfe0d4a29136d141ef4824931c9ed603"; z_c0="2|1:0|10:1529069387|4:z_c0|92:Mi4xOGtKQUJnQUFBQUFBTUdXQXprZTJEU1lBQUFCZ0FsVk5TdzBSWEFCQ0lxMWxCOGxuZi1VZ0Y2SGkwY3pGdXN0TVRR|837c8583508bc9d8494aaf08aabfab99a81746919ed6bd13bba1a76fba3783a6"; __utma=51854390.1190383294.1528969206.1528987399.1529069392.4; __utmb=51854390.0.10.1529069392; __utmc=51854390; __utmz=51854390.1529069392.4.4.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmv=51854390.100--|2=registration_date=20171019=1^3=entry_date=20171019=1'
# sl = s.strip().split(';')
# for s in sl:
#     res = s.split('=', maxsplit=1)
#
#     js[res[0]] = res[1]
#
# js = [js]


class Cookies(object):
    __fi = Saver(mode='json')

    @classmethod
    def get_cookies(cls):
        res = cls.__fi.get()
        # print(res)
        return random.choice(res)
#
cookies = Cookies.get_cookies()
# print(cookies)
# head = {
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'
# }
# print(cookies)
# ses = requests.session()
# ses.headers.update(head)
# ses.cookies = requests.utils.cookiejar_from_dict(cookies)
# ses.verify = False
# res = ses.get('https://www.zhihu.com/people/edit')
# print(res.text)
# print(res.url)
# print(requests.utils.dict_from_cookiejar(res.cookies))