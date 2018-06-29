from tencent.files.saver import Saver
import xlrd
import xlwt
import requests
from tencent.files.hand_file import cookies
import re
p1 = {
    'path_dir': r'C:\Users\PYTHON\Desktop\service\tencent',
    'filename': 'topic_info1.xls',
}
p2 = {
    'path_dir': r'C:\Users\PYTHON\Desktop\service\tencent',
    'filename': 'topic_info2.xls',
    'field': ['id', 'topic', 'follow_num', 'question_num', 'question', 'quest_link']
}
head = {
    'User-Agent': 'MRO'
}
res = requests.get('https://www.zhihu.com/api/v4/questions/21485858/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&amp;limit=10&amp;offset=0&amp;sort_by=default', headers=head,
                   # proxies={'https': '47.96.125.99:3008'}
                   )
print(res.text)
ans = res.json()['data']
print(res.url)
l = re.findall('limit=(\d*)', res.url)[0]
print(l)
content = []
for a in ans:
    text = re.subn('<.*?>', '', a['content'])[0]
    app_gree = a['voteup_count']
    print('回答的赞数：', app_gree)
    # print('回答的内容：', text)
    content.append((text, app_gree))


def filer():
    ta = xlrd.open_workbook('que_info0.xls')
    ta2 = xlrd.open_workbook('topics_过滤.xls')
    sh = ta.sheet_by_name('topic')
    sh2 = ta2.sheet_by_name('topic')
    wr = xlwt.Workbook(encoding='utf-8')
    wh = wr.add_sheet('topic')
    num = sh.nrows
    total = []
    print(num)
    res = []

    for i in range(num):
        result = sh.row_values(i)
        if not result[1]:
            result[1] = 'Unknow'
        # res.append(result[4])
        total.append(result)


    # for i in range(1, sh2.nrows):
    #     result = sh2.row_values(i)
    #     # res.append(result[4])
    #     total.append(result[1:])
    # res = set(res)
    # print(len(res))
    # count = 1
    # temp_data = []
    # temp = []
    # for i in total:
    #     if not i[1]:
    #         print(i)
    #         print(count)
    #     if i[4] not in temp:
    #         temp.append(i[4])
    #         i.insert(0, str(count))
    #         temp_data.append(i)
    #         count += 1
    #
    # temp_data.insert(0, ['id', 'topic', 'follow_num', 'question_num', 'question', 'quest_link'])

    # l = set(res[current:])
    # x = l - cur
    # r = []
    # print(len(x))
    # for q in x:
    #     for i in total[current:]:
    #         if i[3] == q:
    #             r.append(i[4])
    #             break
    #
    # print(len(r))

    # ex = []
    # t = []
    # temp = [['id', 'topic', 'follow_num', 'question_num', 'question', 'quest_link']]
    # for x in total[1:]:
    #     if (x[4], x[5]) in t:
    #         pass
    #     else:
    #         ex.append(x[1:])
    #         t.append((x[4], x[5]))
    #
    # print(len(ex))
    # print(ex[:2])
    # s = enumerate(ex)
    # for x, y in s:
    #     z = [x]
    #     z.extend(y)
    #     temp.extend([z])
    # print(temp[:2])
    # print(len(temp))
    #
    # # question = []
    # # t = []
    # # for x in temp:
    # #     t.append((x[4], x[5]))
    # #     if not question:
    # #         question.append(x)
    # #     for i in question:
    # #         if x[4] == i[4]:
    # #             pass
    # #         else:
    # #             question.append(x)
    # #             break
    # # print(len(question))
    # # print(len(set(t)))
    #
    #
    #
    #
    #
    for n in range(len(total)):
        for m in range(len(total[n])):
            wh.write(n, m, total[n][m])
    wr.save('que_info1.xls')
    # with open('1.txt', 'w') as fi:
    #     fi.write('\n'.join(r))

    # print(temp)




# if __name__ == '__main__':
#     import os
#     res = os.listdir('./')
#
#     with open('./data/ten/1.txt', 'w') as fi:
#         fi.write('2')

    # print(res.text)