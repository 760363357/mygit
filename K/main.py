import pandas as pd
import numpy as np
# from sklearn.cluster import KMeans, DBSCAN
import matplotlib.pyplot as plt
import random
import decimal


# 计算follow_num和question_num相关系数
def relevance(parse_cols):
    rel = parse_cols.corr().values[0, 1]
    print('关注数与问题数的相关系数为：', rel)
    if -0.7 < rel < 0.7:
        print('由于相关系数比较小，可以认为关注数与问题数无任何关系。')
    else:
        print('由于相关系数比较大，可以认为关注数与问题数存在相关关系')


# 画出关注数与问题数的分布图
def draw(X_train, filename):
    # model = KMeans(n_clusters=3).fit(X_train)
    # print(model.labels_)
    #
    # print(model.cluster_centers_)
    # print(model.inertia_)
    fig = plt.figure(figsize=(10, 5))

    ax = fig.add_subplot(1, 1, 1)
    # plt.scatter(X_train, np.ones((1, len(X_train)), dtype=np.int64))
    ax.scatter(X_train[:, 0], X_train[:, 1])
    ax.set_xlabel("follow_num")
    ax.set_ylabel("question_num")
    ax.set_title("Distribution diagram")
    ax.legend(framealpha=0.5)
    # plt.show()
    plt.savefig(filename)
    # print(model.predict([[50000]]))


# 画出话题的所占比例
def pie_chart(parse_col, filename, show_num=None, mode=None):
    if not show_num:
        show_num = 20
    data = {}
    color_unit = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

    total_num = np.sum(parse_col[:, 1])
    for rank in sorted(parse_col, key=lambda x: x[1], reverse=True)[:show_num]:
        topic = rank[0]
        num = rank[1]
        color = '#' + ''.join(random.choices(color_unit, k=6))
        data[topic] = (r'%.2f' % ((num/total_num) * 100), color)
    values = [decimal.Decimal(x[0]) for x in data.values()]
    topic_num = sum(values)
    data['其他'] = (decimal.Decimal('100') - decimal.Decimal(topic_num), '#ffff10')
    # print(topic_num)
    # print(values)

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    #
    # # 设置绘图对象的大小
    fig = plt.figure(figsize=(10, 10))

    cities = data.keys()
    values = [float(x[0]) for x in data.values()]
    colors = [x[1] for x in data.values()]
    #
    ax1 = fig.add_subplot(111)
    if mode:
        ax1.set_title('根据问题数得出话题所占比例饼图')
    else:
        ax1.set_title('根据关注人数得出话题所占比例饼图')
    #
    labels = ['{}:{}'.format(city, str(value) + '%') for city, value in zip(cities, values)]
    #
    # # 设置饼图的凸出显示
    explode = [0 for x in range(show_num + 1)]
    #
    # # 画饼状图， 并且指定标签和对应的颜色
    # # 指定阴影效果

    ax1.pie(values, labels=labels, colors=colors, explode=explode, shadow=True)

    #
    plt.savefig(filename)
    # plt.show()
    # print(total_num)
    # print()


if __name__ == '__main__':
    xls = pd.DataFrame(pd.read_excel('./que_info.xls', parse_cols=(1, 2, 3)))
    xls = xls.drop_duplicates(subset='topic')
    # relevance(xls[['follow_num', 'question_num']])
    # draw(xls[['follow_num', 'question_num']].values, 'x-y.png')
    pie_chart(xls[['topic', 'question_num']].values, 'pie1.jpg', show_num=5, mode=1)

