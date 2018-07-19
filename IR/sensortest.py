#Serial Communication with Arduino
import serial
#statistics libraries
import pandas as pd
import numpy as np
#scikit-learn
from sklearn import svm, neighbors, metrics, preprocessing, cross_validation
from sklearn.metrics import classification_report, accuracy_score
from sklearn.cross_validation import cross_val_score
from sklearn.model_selection import train_test_split

#others
from time import sleep

ser = serial.Serial('/dev/cu.usbmodem17', 115200, timeout=None)
data = pd.DataFrame(index=[], columns=['IR_left', 'IR_right', 
                                       'Pres_follow', 'Pres_back', 
                                       'direction'])
test_data = pd.DataFrame(index=[], columns=[['IR_left', 'IR_right',
                                        'Pres_follow', 'Pres_back'
                                       ]])

class sensor_read:
    def __init__(self):
        for i in range(100):
            ser.readline()

    def read_ser(self, label):
        line = ser.readline()
        line = line.strip().decode('utf-8').split(",")
        line.append(label)
        return line
    def my_sleep(self, interval):
        for i in range(1000*interval):
            ser.readline()
    def read_test_ser(self):
        line = ser.readline()
        line = line.strip().decode('utf-8').split(",")
        series = pd.Series(line, index=test_data.columns)
        new_data = test_data.append(series, ignore_index=True)
        return new_data



print("キャリブレーションを行います")
rd = sensor_read()

print("座席にしっかりと座ってください")
rd.my_sleep(10)

for i in range(200):
    line = rd.read_ser("neutral")
    series = pd.Series(line, index=data.columns)
    print(series)
    data = data.append(series, ignore_index=True)

print("足を左に傾けてください")
rd.my_sleep(5)

for i in range(200):
    line = rd.read_ser("left")
    series = pd.Series(line, index=data.columns)
    print(series)
    data = data.append(series, ignore_index=True)

print("足を右に傾けてください")
rd.my_sleep(2)

for i in range(200):
    line = rd.read_ser("right")
    series = pd.Series(line, index=data.columns)
    print(series)
    data = data.append(series, ignore_index=True)

'''
#split data to train and test
data_train, data_test = train_test_split(data, test_size=0.2)
print("train_data = \n", data_train)
print("test_data  = \n", data_test)

train_label = data_train['direction']
train_data = data_train[['IR_left', 'IR_right',
                         'Pres_follow', 'Pres_back']]

test_label = data_test['direction']
test_data = data_test[['IR_left', 'IR_right',
                         'Pres_follow', 'Pres_back']]
'''

clf_svc = svm.LinearSVC(loss='hinge', C=2.5,
                        class_weight='balanced', random_state=0)
                        
clf_nk = neighbors.KNeighborsClassifier(5, weights='distance')
label = data['direction']
sensor_data = data[['IR_left', 'IR_right',
                         'Pres_follow', 'Pres_back']]


scores = cross_val_score(clf_svc, sensor_data, label, cv=10)
print('SVC Cross-Validation scores: {}'.format(scores))
print('Average score of SVC: {}'.format(np.mean(scores)))
scores = cross_val_score(clf_nk, sensor_data, label, cv=10)
print('k-NN Cross-Validation scores: {}'.format(scores))
print('Average score of k-NN: {}'.format(np.mean(scores)))

clf_svc1 = svm.LinearSVC(loss='hinge', C=2.5,
                         class_weight='balanced', random_state=0)
clf_svc1.fit(sensor_data, label)
print("キャリブレーション終了")
rd.my_sleep(1)
while True:
    new_data = rd.read_test_ser()
    print(clf_svc1.predict(new_data))
    rd.my_sleep(1)




