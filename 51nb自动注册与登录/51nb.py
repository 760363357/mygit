import requests
from config import HEADER
import re
import chardet
import time
import random
import os
import json
from chaojiying_Python.chaojiying import Chaojiying_Client
import sys

class NbReg(object):
    def __init__(self, user, password, key):
        requests.packages.urllib3.disable_warnings()
        self.sess = requests.session()
        self.sess.headers.update(HEADER)
        # self.sess.headers
        self.sess.verify = False
        self.id = ''
        self.formhash = ''
        self.arg = ''
        self.usr = user
        self.password = password
        self.key = key
        self.user_field = ''
        self.password_field = ''
        self.password2_field = ''
        self.email_field = ''


    def reg_id_form(self, url):
        res = self.sess.get(url)
        self.id = re.findall('id="seccode_(.*?)"', res.text)[0]
        self.formhash = re.findall('name="formhash" value="(.*?)"', res.text)[0]
        self.arg = re.findall('name="agreebbrule" value="(.*?)"', res.text)[0]
        self.user_field = re.findall('<label for="(.*?)">用户名', res.text)[0]
        self.password_field = re.findall('<label for="(.*?)">密码', res.text)[-1]
        self.password2_field = re.findall('<label for="(.*?)">确认密码', res.text)[0]
        self.email_field = re.findall('<label for="(.*?)">Email', res.text)[0]
        # print(self.password_field)
        # print(self.arg)
        # print(self.formhash)
        assert self.id
        return res.content.decode(chardet.detect(res.content)['encoding'])

    def get_user(self, url, username):
        data = {
            'mod': 'ajax',
            'inajax': 'yes',
            'infloat': 'register',
            'handlekey': 'register',
            'ajaxmenu': '1',
            'action': 'checkusername',
            'username': username
        }
        res = self.sess.get(url, params=data)
        r = re.findall(r'TA\[(.*?)\]', res.text)[0]
        assert r == 'succeed'

    def get_psw(self, url, password):
        pass

    def get_email(self, url, email):
        data = {
            'mod': 'ajax',
            'inajax': 'yes',
            'infloat': 'register',
            'handlekey': 'register',
            'ajaxmenu': '1',
            'action': 'checkemail',
            'email': email
        }
        res = self.sess.get(url, params=data)
        r = re.findall(r'TA\[(.*?)\]', res.text)[0]
        assert r == 'succeed'

    def get_cap(self, img_url, img_filename):
        data = {
            'mod': 'seccode',
            'action': 'update',
            'idhash': self.id,
            '': random.random(),
            'modid': 'undefind'
        }
        res = self.sess.get(img_url, params=data)
        next_data = re.findall('src="(.*?)"', res.text)[-1].split("?")[-1]
        img_c = self.sess.get(img_url + '?' + next_data)
        # print(img_c.content)
        with open(img_filename, 'wb') as fi:
            fi.write(img_c.content)

    def vaild_cap(self, url, filename):
        captch, pic, cap = self.into_cap(filename)
        data = {
            'mod': 'seccode',
            'action': 'check',
            'inajax': '1',
            'modid': 'member::register',
            'idhash': self.id,
            'secverify': captch
        }
        res = self.sess.get(url, params=data)
        r = re.findall(r'TA\[(.*?)\]', res.text)[0]
        print(r)
        if r == 'succeed':
            return captch
        else:
            print('该验证码错误，正在重试！')
            cap.ReportError(pic)
            self.get_cap(url, filename)
            return self.vaild_cap(url, filename)

    def into_cap(self, filename):
        cap = Chaojiying_Client(self.usr, self.password, self.key)
        im = open(filename, 'rb').read()
        res = cap.PostPic(im, 1902)
        print(res)
        return res['pic_str'], res['pic_id'],  cap

    def submit(self, url, data):
        data1 = {
            'mod': 'register',
            'inajax': '1'
        }
        data2 = {
            'regsubmit': 'yes',
            'formhash': self.formhash,
            'referer': 'https://forum.51nb.com/forum.php',
            'activationauth': '',
            self.user_field: data['username'],
            self.password_field: data['password'],
            self.password2_field: data['password'],
            self.email_field: data['email'],
            'seccodehash': self.id,
            'seccodemodid': 'member::register',
            'seccodeverify': data['captch'],
            'agreebbrule': self.arg
        }
        print(data2)
        res = self.sess.post(url, params=data1, data=data2)
        if res.status_code == 200:
            if 'succeedmessage' in res.text:
                print('注册成功！正在跳转页面获取cookies！')
            else:
                print(res.text)
                print('注册失败，请检查原因！')
                sys.exit()

    def get_cookies(self):
        res = self.sess.get('https://forum.51nb.com/forum.php')
        # print(res.text)
        print('获取coolies成功！下面是cookie值：')
        cookies = requests.utils.dict_from_cookiejar(self.sess.cookies)
        print(cookies)
        return cookies

    def save(self, data, cookies):
        filename = 'cookies.json'
        res = os.listdir('./')
        if filename in res:
            fi = open(filename, 'r+')
            f = list(fi.read())
        else:
            fi = open(filename, 'w')
            f = []
        f.append([data, cookies])
        json.dump(f, fi)
        fi.close()

    def start_reg(self, data):
        submit = 'https://forum.51nb.com/member.php'
        use_url = 'https://forum.51nb.com/forum.php'
        reg = 'https://forum.51nb.com/member.php?mod=register'
        img = 'https://forum.51nb.com/misc.php'
        self.reg_id_form(reg)
        time.sleep(1)
        self.get_user(use_url, data['username'])
        time.sleep(1)
        self.get_email(use_url, data['email'])
        time.sleep(0.5)
        self.get_cap(img, data['captch_file'])
        data['captch'] = self.vaild_cap(img, data['captch_file'])
        self.submit(submit, data)
        time.sleep(5)
        cookies = self.get_cookies()
        self.save(cookies, data)


# class NbLog(NbReg):
#     def __init__(self):
#         super().__init__()
#
#     def post_data(self, data):
#         pass


if __name__ == '__main__':
    li = list(range(1, 9))
    username = random.random()*10**10
    password = random.random()*10**7
    email = random.random()*10**10
    data = {
        'username': str(int(username)),
        'password': str(int(password)),
        'email': str(int(email)) + '@qq.com',
        'captch_file': 'cap.png',
        'capth': ''
    }
    print('注册信息为:', data)
    r = NbReg('ppy835766', 'zjl171313ZJL', '896687')
    # r.reg_id_form('https://forum.51nb.com/member.php?mod=register')
    r.start_reg(data)
    # co = {'Uf3r_2132_auth': '8162rOXOqvHjticmKohLQG92%2Fx01d9uJU4VBzb8ZjVEqjhwkK%2F%2BBmJ7SPee0cbrot276V7jwKaDDbmxyRHB40adAJ3WM', 'Uf3r_2132_connect_is_bind': '0', 'Uf3r_2132_creditbase': '0D0D0D0D0D0D0D0D0', 'Uf3r_2132_creditnotice': '0D0D2D0D0D0D0D0D0D1898490', 'Uf3r_2132_creditrule': '%E6%AF%8F%E5%A4%A9%E7%99%BB%E5%BD%95', 'Uf3r_2132_lastact': '1528903819%09forum.php%09', 'Uf3r_2132_lastvisit': '1528900154', 'Uf3r_2132_nofavfid': '1', 'Uf3r_2132_saltkey': 'ahe9T1eP', 'Uf3r_2132_seccode': '1206.ec67214889a456b473', 'Uf3r_2132_sid': 'nloq51', 'Uf3r_2132_ulastactivity': '30e3IRPP2XC%2FwUDOGsmUj26yD4m1aZzjfbrN1gggVWlkoLMf3t7Z'}
    # c = NbReg(1, 2, 3)
    # r.save(co, data)