#PyQt
import sys
import math
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QGridLayout, QSizePolicy, QLineEdit,
                             QLineEdit, QDialog, QLabel)
from PyQt5.QtGui import QPainter, QFont, QColor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint
#PySerial
import serial
import numpy as np
import random
import time
import statistics
import csv

window_size_x = 1440   
window_size_y = 900
#window_size = QtGui.qApp.desktop().width()
num_of_sensor = 10
wait_flame = 100
alpha = 0.7
pointer_size = 20
gestures = 0
output_path = 'testLogger.csv'


class sensor_read:
    def __init__(self):
        self.ser = serial.Serial('/dev/cu.usbmodem143301', 460800)
        for i in range(10):
            self.ser.readline()

    def read_test_ser(self):
        lst = float(0)
        while self.ser.in_waiting > 1 or lst == float(0):
            lst = self.ser.readline().strip().decode("utf-8").split(',')
        return lst


class main_window(QWidget):

    #膝位置計算用変数リセット
    def value_init(self):
        self.sensor_val = np.zeros(num_of_sensor, dtype=np.float)
        self.sensor_flt = np.zeros((wait_flame,num_of_sensor), dtype=np.float)
        self.n_sensor_val = np.zeros(num_of_sensor, dtype=np.float)
        self.weight = ([1.00] * num_of_sensor)

    #指数平均平滑フィルタ変数のリセット(本当は必要ないかもしれない)
    def ema_reset(self):

        self.old_ema = np.zeros(num_of_sensor, dtype=np.float)
        self.new_ema = np.zeros(num_of_sensor, dtype=np.float)
        self.new_x = 0
        self.old_x = window_size_x / 2
        self.new_y = 0
        self.old_y = window_size_y / 2


    def __init__(self, parent=None):
        super().__init__(parent)
        self.ema_reset()
        self.value_init()
        self.resize(window_size_x, window_size_y)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.value_upd)
        self.timer.start(5)  # 200fps以下

        self.val = [0] *10

        self.do_teacher_data_collection = False
        self.gesture_number = 0
        self.current_frame_number = 0

        self.gesture_dataset = np.empty([0, 11], float)
        
        for i in range(num_of_sensor):
            self.val[i] = QLineEdit(self)
            self.val[i].move(window_size_x / 12 * (i+1), 100)
            self.val[i].resize(100, 20)


        #実験データ収集用
        self.logger = np.empty([0,10], float)
        #操作時間計測

        # self.classifier = self.classify_knee()

    def keyPressEvent(self, keyevent):
        if keyevent.key() == Qt.Key_Return:
            print("key event")
            if self.gesture_number < gestures:
                self.gesture_number += 1
            self.do_teacher_data_collection = True

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        painter.setPen(Qt.black)
        painter.setBrush(Qt.red)

        for i in range(num_of_sensor):
            painter.drawRect(window_size_x / 12 * (i+1), window_size_y -
                             (self.sensor_val[i])*10-100, 40,  (self.sensor_val[i])*10)
            self.val[i].setText(str(round(self.sensor_val[i], 2)))

    def classify_knee(self):
        from sklearn import svm, neighbors, metrics, preprocessing
        from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
        from sklearn.metrics import classification_report, accuracy_score
        import pandas as pd

        tuned_parameters = [
            {'C': [1, 10, 100, 1000], 'kernel': ['linear']}, 
            {'C': [1, 10, 100, 1000], 'kernel': ['rbf'], 'gamma': [0.001, 0.0001]}, 
            {'C': [1, 10, 100, 1000], 'kernel': ['poly'], 'degree': [2, 3, 4], 'gamma': [0.001, 0.0001]}, 
            {'C': [1, 10, 100, 1000], 'kernel': ['sigmoid'], 'gamma': [0.001, 0.0001]}
            ]

        dataset1 = pd.read_csv("testLogger_one.csv", header=None)
        dataset1['Label'] = 1
        dataset2 = pd.read_csv("testLogger_two.csv", header=None)
        dataset2['Label'] = 2

        dataset = pd.concat([dataset1, dataset2])



        data_train, data_test = train_test_split(dataset, test_size=0.2)

        train_label = data_train['Label']
        train_data = data_train.iloc[:,0:10]

        # print(train_data, train_label)

        test_label = data_test['Label']
        test_data = data_test.iloc[:, 0:10]

        classifier = GridSearchCV(svm.SVC(),            # 使用したいモデル
                                  tuned_parameters,  # 最適化したいパラメータ
                                  cv=5,  # 交差検証の回数
                                  scoring='recall'  # 評価関数の指定
                                  )
        classifier.fit(train_data, train_label)
        print(classifier.best_estimator_)
        print(classification_report(test_label, classifier.predict(test_data)))

        return classifier

    def value_upd(self):
        
        #print(self.left_limit, self.right_limit,self.upper_limit, self.lower_limit)
        tmp = rd.read_test_ser()
        self.sensor_val = [64-float(v) for v in tmp]
        # print(np.array(self.sensor_val).size)
        # self.logger = np.append(self.logger, np.array(self.sensor_val).reshape(1,10), axis=0)
        
        
        #指数平均平滑フィルタ
        if np.allclose(self.old_ema, np.zeros(num_of_sensor, dtype=np.float)):
            self.old_ema = self.sensor_val
        else:
            for i in range(num_of_sensor):
                self.new_ema[i] = (
                    self.sensor_val[i] - self.old_ema[i]) * alpha + self.old_ema[i]
                self.sensor_val[i] = self.new_ema[i]
            self.old_ema = self.new_ema
        #指数平均平滑フィルタ
        # print(self.sensor_val)

        if self.do_teacher_data_collection:
            if self.current_frame_number < 100:
                v = np.array(self.sensor_val)
                v = np.append(v, self.gesture_number).reshape(1,11)
                self.gesture_dataset = np.append(self.gesture_dataset, v, axis=0)
                print(self.current_frame_number)
                self.current_frame_number += 1
            else:
                self.current_frame_number = 0
                self.do_teacher_data_collection = False
                self.gesture_number += 1
                print("next gesture: {}".format(self.gesture_number))
                



        self.update()



    def main(self):
        self.show()
        app.exec_()
        np.savetxt(output_path, self.logger, delimiter=',', fmt='%.2f')

rd = sensor_read()
app = QApplication(sys.argv)
window = main_window()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Input 1 argument. \nUsage: $python gesture_recognition.py 6")
        exit(0)
    else:
        gestures = 1 + int(sys.argv[1])
        print(gestures)
        window.main()
