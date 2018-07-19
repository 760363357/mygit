from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from diy_save.saver import Saver    # 用于操作Excel类
import time
import re


class PhaInfo(object):
    # 初始化一些信息，sleep表示两个页面之间的休眠间隔
    def __init__(self, sleep):
        self.sleep = sleep
        self.start_url = 'http://app1.sfda.gov.cn/datasearch/face3/base.jsp?tableId=34&tableName=TABLE34&title=%D2%A9%C6%B7%C9%FA%B2%FA%C6%F3%D2%B5&bcId=118103348874362715907884020353'
        self.save_object = Saver()
        # self.save_object.clear()
        self.option = webdriver.FirefoxOptions()
        self.option.add_argument("--headless")    # 把该行去掉注释表示无界面浏览
        self.drive = webdriver.Firefox(firefox_options=self.option)
        self.act = ActionChains(self.drive)
        self.wait = WebDriverWait(self.drive, 10)

    # 信息收集
    def info_handl(self, info_ele):
        info = {}
        next_id = self.save_object.get()
        info['id'] = 1 if not next_id else next_id[-1].get('id') + 1
        info['企业名称'] = info_ele[10].text
        info['编号'] = info_ele[2].text
        info['社会信用代码/组织机构代码'] = info_ele[4].text
        info['分类码'] = info_ele[6].text
        info['省份'] = info_ele[8].text
        info['法定代表人'] = info_ele[12].text
        info['企业负责人'] = info_ele[14].text
        info['质量负责人'] = info_ele[16].text
        info['注册地址'] = info_ele[18].text
        info['生产地址'] = info_ele[20].text
        info['生产范围'] = info_ele[22].text
        info['发证日期'] = info_ele[24].text
        info['有效期至'] = info_ele[26].text
        info['发证机关'] = info_ele[28].text
        info['签发人'] = info_ele[30].text
        info['日常监管机构'] = info_ele[32].text
        info['日常监管人员'] = info_ele[34].text
        info['监督举报电话'] = info_ele[36].text
        info['备注'] = info_ele[38].text
        info['相关数据库查询'] = info_ele[40].text.replace('\n', ' ')
        self.save_object.insert(info)

    # 点击详情页，通过页面元素点击或者JS点击
    def click_detail(self, num):
        try:
            a = self.drive.find_elements_by_xpath('//div[@id="content"]//p/a')
            self.act.click(a[num]).perform()
        except:
            js = f'document.getElementById("content").getElementsByTagName("a")[{num}].click();'
            self.drive.execute_script(js)
            # print(a[num].text)

            # a[num].click()

    # 程序结束时，关闭浏览器。
    def __del__(self):
        self.drive.quit()

    # 保存文件
    def save(self):
        self.save_object.save()

    # 处理一个页面的信息
    def one_page_info(self):
        try:
            a = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@id="content"]//p/a')))
            time.sleep(0.5)
        except:
            print('无法找到企业标签，请检查原因！')
        else:
            page_total = len(a)
            print([x.text for x in a])
            for num in range(page_total):
                self.click_detail(num)
                time.sleep(self.sleep)
                try:
                    info_ele = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="listmain"]/div//tr/td')))
                except:
                    print('找不到所要的信息！')
                else:
                    self.info_handl(info_ele)
                    js = 'document.getElementsByClassName("listmain")[0].getElementsByTagName("img")[0].onclick()'
                    self.drive.execute_script(js)
                    time.sleep(self.sleep)
            self.save_object.save()

    # 主要函数，执行入口
    def main(self):
        self.drive.get(self.start_url)
        num = len(self.save_object.get())
        try:
            page = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@id="content"]//tbody/tr[1]/td[1]')))[4]
            time.sleep(0.5)
            self.drive.execute_script('window.scrollTo(0,350)')
            page = int(re.findall('共(.*?)页', page.text)[0])
        except:
            print('使用默认页数')
            page = 504
        print(f'需要抓取的信息共有{page}页')
        if num:
            try:
                self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@id="content"]//img')))
            except:
                exit()
                pass
            else:
                js1 = f'document.getElementById("content").getElementsByTagName("table")[4].getElementsByTagName("input")[0].value="{(num//15)+1}";'
                js2 = 'document.getElementById("content").getElementsByTagName("table")[4].getElementsByTagName("input")[1].click();'
                self.drive.execute_script(js1)
                time.sleep(0.5)
                self.drive.execute_script(js2)
                current = (num//15) + 1
        else:
            current = 1
        for pa in range(current, page + 1):
            print(f'正在抓取第{pa}页信息...')
            self.one_page_info()
            try:
                self.wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, '//div[@id="content"]//img')))
            except:
                pass
            else:
                if pa == page:
                    break
                js = 'document.getElementById("content").getElementsByTagName("img")[2].onclick()'
                self.drive.execute_script(js)
            time.sleep(self.sleep)
            print(f'抓取第{pa}页完毕！')
        time.sleep(2)
        self.drive.quit()




if __name__ == '__main__':
    sleep = 1
    info = PhaInfo(sleep)
    info.main()

