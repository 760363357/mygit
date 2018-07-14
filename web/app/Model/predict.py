from .train import Train
from sklearn.externals import joblib


def predict(x, mode='MB'):
    X = Train.data_pre(Train.voc.vocabulary_, x)
    if mode == 'MB':
        clf = joblib.load('app/Model/model/MultinomialNB.m')
    else:
        clf = joblib.load('app/Model/model/BernoulliNB.m')
    res = clf.predict(X)
    return res

if __name__ == '__main__':
    with open('./data/test_contents.txt', 'r', encoding='utf-8') as f:
        content = f.read().split('\n')
    print(predict([content[0]]))
