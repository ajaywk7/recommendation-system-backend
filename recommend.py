import sklearn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
product_descriptions = pd.read_csv(
    r"C:\projects\groceries-backend\products.csv", encoding="ISO-8859-1")
product_descriptions.shape
product_descriptions = product_descriptions.dropna()
product_descriptions.shape
product_descriptions.head()
product_descriptions1 = product_descriptions.head(500)
product_descriptions1["description"].head(10)
vectorizer = TfidfVectorizer(stop_words='english')
X1 = vectorizer.fit_transform(product_descriptions1["description"])
X1
X = X1
kmeans = KMeans(n_clusters=10, init='k-means++')
y_kmeans = kmeans.fit_predict(X)


def print_cluster(i):
    #print("Cluster %d:" % i),
    arr = []
    for ind in order_centroids[i, :10]:
        arr.append(terms[ind])
    return arr


true_k = 10

model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
model.fit(X1)
order_centroids = model.cluster_centers_.argsort()[:, ::-1]
terms = vectorizer.get_feature_names()
'''for i in range(true_k):
    print_cluster(i)'''


def show_recommendations(product):
    #print("Cluster ID:")
    Y = vectorizer.transform([product])
    prediction = model.predict(Y)
    # print(prediction)
    arr = print_cluster(prediction[0])
    return arr


#show_recommendations("Brown eggs")
