from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.externals import joblib


class Train(object):
    train_texts = open(r'app/Model/data/train_contents.txt', 'r', encoding='utf-8').read().split('\n')
    test_texts = open(r'app/Model/data/test_contents.txt', 'r', encoding='utf-8').read().split('\n')
    all_texts = train_texts + test_texts
    voc = CountVectorizer()
    voc.fit_transform(all_texts)

    def __init__(self):
        self.train_labels = open(r'app/Model/data/train_labels.txt', 'r', encoding='utf-8').read().split('\n')
        self.test_labels = open(r'app/Model/data/test_labels.txt', 'r', encoding='utf-8').read().split('\n')
        self.all_labels = self.train_labels + self.test_labels
        self.train_data = self.data_pre(self.voc.vocabulary_, self.train_texts)
        self.test_data = self.data_pre(self.voc.vocabulary_, self.test_texts)
        self.all_data = self.data_pre(self.voc.vocabulary_, self.all_texts)

    @staticmethod
    def data_pre(voc, data):

        train_counts = CountVectorizer(vocabulary=voc).fit_transform(data)
        test_data = TfidfTransformer().fit_transform(train_counts)
        return test_data
        # return train_counts, test_counts

    def fit(self, x, y, model='MB'):
        if model == 'MB':
            self.clf = MultinomialNB(alpha=0.1)
        else:
            self.clf = BernoulliNB(alpha=0.1)
        self.clf.fit(x, y)

    def predict(self, x):
        count = 0
        res = self.clf.predict(x)
        for num in range(len(res)):
            if res[num] == self.test_labels[num]:
                count += 1
        if isinstance(self.clf, MultinomialNB):
            name = 'MultinomialNB'

        else:
            name = 'BernoulliNB'
        print('{}模型正确率：{:.2f}%'.format(name, count / len(res) * 100))
        joblib.dump(self.clf, f'./model/{name}.m')

    def __call__(self, *args, **kwargs):
        self.fit(self.all_data, self.train_labels + self.test_labels, model='MB')
        self.predict(self.test_data)


if __name__ == '__main__':
    t = Train()
    t()