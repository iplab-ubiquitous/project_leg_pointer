# -*- coding: utf-8 -*-
from sklearn import svm, neighbors, metrics, preprocessing, cross_validation
from sklearn import datasets
from sklearn.cross_validation import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.kernel_approximation import RBFSampler
from sklearn.cluster import KMeans
import numpy as np
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA

import pandas as pd

dataset1 = pd.read_csv("test3.csv");
#print(dataset1);

'''
del(dataset1['label']);
#print(dataset1);
pred = KMeans(n_clusters=3).fit_predict(dataset1);
print(pred);


pca = PCA(n_components=2)
plot_data = pca.fit_transform(dataset1);

plt.figure();

for (i, label) in enumerate(pred):
    if label == 0:
        plt.scatter(plot_data[i, 0], plot_data[i, 1], c='red')
    elif label == 1:
        plt.scatter(plot_data[i, 0], plot_data[i, 1], c='blue')
    elif label == 2:
        plt.scatter(plot_data[i, 0], plot_data[i, 1], c='green')

plt.show();

'''


# 学習データを用意する


#特徴量の次元を圧縮
#似たような性質の特徴を同じものとして扱います
#del(dataset1['index']);
del(dataset1['err']);
del(dataset1['temparature']);
#del(dataset1['a']);
#del(dataset1['b']);
dataset1_train, dataset1_test = train_test_split(dataset1,test_size=0.2);
print("train_data = \n", dataset1_train);
print("test_data  = \n", dataset1_test);

train_label = dataset1_train['label']
train_data = dataset1_train[['acc_x','acc_y','acc_z','rad_x','rad_y','rad_z','gyr_x','gyr_y','gyr_z']];
test_label = dataset1_test['label']
test_data = dataset1_test[['acc_x','acc_y','acc_z','rad_x','rad_y','rad_z','gyr_x','gyr_y','gyr_z']];

#test_pred = clf.predict(dataset1_test[['x','y','z']]);
clf_svc = svm.LinearSVC(loss='hinge', C=2.5,class_weight='balanced', random_state=0);
result = clf_svc.fit(train_data, train_label)
pred = clf_svc.predict(test_data);
#print(test_pred);
print(classification_report(test_label, pred));
print("正答率 = ",metrics.accuracy_score(test_label, pred));

n_neighbors = 5;
clf_nk = neighbors.KNeighborsClassifier(n_neighbors, weights = 'distance');
result = clf_nk.fit(train_data, train_label)
pred_nk = clf_nk.predict(test_data);
#print(test_pred);
print(classification_report(test_label, pred_nk));
print("正答率 = ",metrics.accuracy_score(test_label, pred_nk));


#どのモデルがいいのかよくわからないから目があったやつとりあえずデフォルト設定で全員皆殺し


#LinearSVCのスコア:0.973333333333
