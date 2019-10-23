# -*- encoding: utf8-*-
import sys
import pandas as pd
import pickle
import requests
from datetime import datetime
import jieba.posseg
import jieba.analyse
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import json

from bs4 import BeautifulSoup as bs
import os
root_path = r"C:\Users\marshall\PycharmProjects\YourSE\data\\"
columns = ["id", "title", "content", "name", "ts"]

def acquire_article():
    articles = list()
    filename = "./data/articles.pkl"
    flag, articles = load_data(filename)
    if flag:
        return articles
    with open("articles.txt", "r", encoding="utf8") as fp1:
        for line in fp1:
            url = line.strip()
            web_page = requests.get(url)
            soup = bs(web_page.content)
            ts_now = int(datetime.now().timestamp())
            aid = url.split('/')[-1]
            article = [
                aid,
                 soup.title.text,
                 soup.body.text,
                "{}_{}".format(aid, ts_now),
                 ts_now
            ]
            articles.append(article)
        dump_data(filename, articles)
    return articles

def load_data(filename, data=None):
    if os.path.exists(filename):
        with open(filename, "rb") as fp:
            data = pickle.load(fp)
            return True, data
    else:
        return False, None

def dump_data(filename, data):
    with open(filename, "wb") as fp:
        pickle.dump(data, fp, pickle.HIGHEST_PROTOCOL)

def pre_processor(articles):
    filename = "./data/features.pkl"
    flag, data = load_data(filename)
    if flag:
        return data["X"], data["vectorizer"]
    data = pd.DataFrame(articles, columns=columns)

    jieba.analyse.set_stop_words("./data/stop_words.txt")
    data["t_kws"] = data["title"].apply(lambda x:
        " ".join(
            jieba.analyse.extract_tags(
        x, topK=10, withWeight=False, allowPOS=('n','v')
    )))
    data["c_kws"] = data["content"].apply(lambda x:
        " ".join(
            jieba.analyse.extract_tags(
        x, topK=100, withWeight=False, allowPOS=('n','v')
    )))
    data["kws"] = data["t_kws"] + " " + data["c_kws"]
    vectorizer = TfidfVectorizer(
        max_features=500, use_idf=True, smooth_idf=True)
    X = vectorizer.fit_transform(data["kws"].values)

    dump_data(filename, {"X": X, "vectorizer": vectorizer})
    return X, vectorizer



if __name__ == "__main__":
    articles = acquire_article()
    X, vectorizer = pre_processor(articles)
    true_k = 3
    k_means = KMeans(
        n_clusters=true_k,
        init='k-means++',
        max_iter=300,
        n_init=1,
        verbose=False
    )
    k_means.fit(X)
    terms = vectorizer.get_feature_names()
    print(terms)
    print(k_means.cluster_centers_)
    if True:  # 显示标签
        print("Top terms per cluster:")
        order_centroids = k_means.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names()
        # print(vectorizer.get_stop_words())
        for i in range(true_k):
            print("Cluster %d" % i, end='')
            for ind in order_centroids[i, :10]:
                print(' %s' % terms[ind], end='')
            print()
    result = list(k_means.predict(X))
    print('Cluster distribution:')
    print(dict([(i, result.count(i)) for i in result]))
    print(k_means.score(X))




