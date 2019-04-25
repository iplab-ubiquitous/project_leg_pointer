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

W_SIZE = 10

dataset1 = pd.read_csv("test4.csv")


#以下学習
#del(data['err'])
#del(data['temparature'])


move = dataset1['move']
data = dataset1[['Left_ACC_X0', 'Left_ACC_Y0', 'Left_ACC_Z0',
                         'Left_GYR_X0', 'Left_GYR_Y0', 'Left_GYR_Z0',
                         'Right_ACC_X0', 'Right_ACC_Y0', 'Right_ACC_Z0',
                         'Right_GYR_X0', 'Right_GYR_Y0', 'Right_GYR_Z0',
                         'Left_ACC_X1', 'Left_ACC_Y1', 'Left_ACC_Z1',
                         'Left_GYR_X1', 'Left_GYR_Y1', 'Left_GYR_Z1',
                         'Right_ACC_X1', 'Right_ACC_Y1', 'Right_ACC_Z1',
                         'Right_GYR_X1', 'Right_GYR_Y1', 'Right_GYR_Z1',
                         'Left_ACC_X2', 'Left_ACC_Y2', 'Left_ACC_Z2',
                         'Left_GYR_X2', 'Left_GYR_Y2', 'Left_GYR_Z2',
                         'Right_ACC_X2', 'Right_ACC_Y2', 'Right_ACC_Z2',
                         'Right_GYR_X2', 'Right_GYR_Y2', 'Right_GYR_Z2',
                         'Left_ACC_X3', 'Left_ACC_Y3', 'Left_ACC_Z3',
                         'Left_GYR_X3', 'Left_GYR_Y3', 'Left_GYR_Z3',
                         'Right_ACC_X3', 'Right_ACC_Y3', 'Right_ACC_Z3',
                         'Right_GYR_X3', 'Right_GYR_Y3', 'Right_GYR_Z3',
                         'Left_ACC_X4', 'Left_ACC_Y4', 'Left_ACC_Z4',
                         'Left_GYR_X4', 'Left_GYR_Y4', 'Left_GYR_Z4',
                         'Right_ACC_X4', 'Right_ACC_Y4', 'Right_ACC_Z4',
                         'Right_GYR_X4', 'Right_GYR_Y4', 'Right_GYR_Z4',
                         'Left_ACC_X5', 'Left_ACC_Y5', 'Left_ACC_Z5',
                         'Left_GYR_X5', 'Left_GYR_Y5', 'Left_GYR_Z5',
                         'Right_ACC_X5', 'Right_ACC_Y5', 'Right_ACC_Z5',
                         'Right_GYR_X5', 'Right_GYR_Y5', 'Right_GYR_Z5',
                         'Left_ACC_X6', 'Left_ACC_Y6', 'Left_ACC_Z6',
                         'Left_GYR_X6', 'Left_GYR_Y6', 'Left_GYR_Z6',
                         'Right_ACC_X6', 'Right_ACC_Y6', 'Right_ACC_Z6',
                         'Right_GYR_X6', 'Right_GYR_Y6', 'Right_GYR_Z6',
                         'Left_ACC_X7', 'Left_ACC_Y7', 'Left_ACC_Z7',
                         'Left_GYR_X7', 'Left_GYR_Y7', 'Left_GYR_Z7',
                         'Right_ACC_X7', 'Right_ACC_Y7', 'Right_ACC_Z7',
                         'Right_GYR_X7', 'Right_GYR_Y7', 'Right_GYR_Z7',
                         'Left_ACC_X8', 'Left_ACC_Y8', 'Left_ACC_Z8',
                         'Left_GYR_X8', 'Left_GYR_Y8', 'Left_GYR_Z8',
                         'Right_ACC_X8', 'Right_ACC_Y8', 'Right_ACC_Z8',
                         'Right_GYR_X8', 'Right_GYR_Y8', 'Right_GYR_Z8',
                         'Left_ACC_X9', 'Left_ACC_Y9', 'Left_ACC_Z9',
                         'Left_GYR_X9', 'Left_GYR_Y9', 'Left_GYR_Z9',
                         'Right_ACC_X9', 'Right_ACC_Y9', 'Right_ACC_Z9',
                         'Right_GYR_X9', 'Right_GYR_Y9', 'Right_GYR_Z9']]

#test_pred = clf.predict(data_test[['x','y','z']]);
clf_svc = svm.LinearSVC(loss='hinge', C=2.5,
                        class_weight='balanced', random_state=0)

scores = cross_val_score(clf_svc, data, move, cv=10)
print('Cross-Validation scores: {}'.format(scores))
print('Average score: {}'.format(np.mean(scores)))


n_neighbors = 5
clf_knn = neighbors.KNeighborsClassifier(n_neighbors, weights='distance')
scores = cross_val_score(clf_knn, data, move, cv=10)
print('Cross-Validation scores: {}'.format(scores))
print('Average score: {}'.format(np.mean(scores)))

