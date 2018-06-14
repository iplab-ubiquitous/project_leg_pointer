#データ取得関係
import serial
import pandas as pd

#学習関係
from sklearn import svm, neighbors, metrics, preprocessing, cross_validation
from sklearn import datasets
from sklearn.cross_validation import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.kernel_approximation import RBFSampler
from sklearn.cluster import KMeans


ser = serial.Serial('/dev/cu.usbmodem1411',115200,timeout=None)   # シリアル通信 to Arduino
#line = ser.readline()
data = pd.DataFrame(index=[], columns=['Left_ACC_X', 'Left_ACC_Y', 'Left_ACC_Z', 
                                       'Left_GYR_X', 'Left_GYR_Y', 'Left_GYR_Z', 
                                       'Right_ACC_X', 'Right_ACC_Y', 'Right_ACC_Z',
                                       'Right_GYR_X', 'Right_GYR_Y', 'Right_GYR_Z', 
                                       'move'])
#print(line.strip().decode('utf-8').split(","))
#10000データで学習を行う
for i in range(100):
    line = ser.readline()
    line = line.strip().decode('utf-8').split(",")
    line.append("right_flick")
    #print(line)
    series = pd.Series(line, index=data.columns)
    data = data.append(series, ignore_index=True)
    print(series)
#ser.close()
#print(data)


data.to_csv("test4.csv", sep=",")
#以下学習
del(data['err'])
del(data['temparature'])
data_train, data_test = train_test_split(data, test_size=0.2)
print("train_data = \n", data_train)
print("test_data  = \n", data_test)

train_label = data_train['label']
train_data = data_train[['acc_x', 'acc_y', 'acc_z', 'rad_x', 'rad_y', 'rad_z', 'gyr_x', 'gyr_y', 'gyr_z']]
test_label = data_test['label']
test_data = data_test[['acc_x', 'acc_y', 'acc_z', 'rad_x', 'rad_y', 'rad_z', 'gyr_x', 'gyr_y', 'gyr_z']]

#test_pred = clf.predict(data_test[['x','y','z']]);
clf_svc = svm.LinearSVC(loss='hinge', C=2.5,
                        class_weight='balanced', random_state=0)
result = clf_svc.fit(train_data, train_label)
pred = clf_svc.predict(test_data)
#print(test_pred);
print(classification_report(test_label, pred))
print("正答率 = ", metrics.accuracy_score(test_label, pred))

n_neighbors = 5
clf_nk = neighbors.KNeighborsClassifier(n_neighbors, weights='distance')
result = clf_nk.fit(train_data, train_label)
pred_nk = clf_nk.predict(test_data)
#print(test_pred);
print(classification_report(test_label, pred_nk))
print("正答率 = ", metrics.accuracy_score(test_label, pred_nk))
