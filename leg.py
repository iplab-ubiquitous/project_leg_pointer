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


ser = serial.Serial('/dev/cu.usbmodem1421',9600,timeout=None)   # シリアル通信 to Arduino
#line = ser.readline()
data = pd.DataFrame(index=[], columns=['err', 'temparature', 'acc_x', 'acc_y', 'acc_z', 'arg_x', 'arg_y', 'arg_z', 'gyr_x', 'gyr_y', 'gyr_z', 'label'])
#print(line.strip().decode('utf-8').split(","))
#10000データで学習を行う
for i in range(10000):
    line = ser.readline()
    series = pd.Series(line.strip().decode('utf-8').split(","), index=data.columns)
    data = data.append(series,ignore_index=True)
 
ser.close()
print(data)
