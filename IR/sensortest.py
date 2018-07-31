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

#PyQt
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QGridLayout, QSizePolicy, QLineEdit)
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtCore import Qt, QTimer


#others
from time import sleep


ser = serial.Serial('/dev/cu.usbmodem1421', 9600)



data_x0 = pd.DataFrame(index=[], columns=['IR_00', 'IR_10', 
                                       'IR_01', 'IR_11'
                                       ])
data_x1 = pd.DataFrame(index=[], columns=['IR_00', 'IR_10',
                                          'IR_01', 'IR_11'
                                          ])
test_data = pd.DataFrame(index=[], columns=[['IR_left', 'IR_right',
                                        'Pres_follow', 'Pres_back'
                                       ]])

class sensor_read:
    def __init__(self):
        for i in range(10):
            ser.readline()

    def read_ser(self, label):
        line = ser.readline()
        line = line.strip().decode('utf-8').split(",")
        line_f = [float(s) for s in line]
        print(line_f)
        #line.append(label)
        return line_f
    def my_sleep(self, interval):
        for i in range(10*interval):
            ser.readline()
    def read_test_ser(self):
        line = ser.readline()
        line = line.strip().decode('utf-8').split(",")
        line_f = [float(s) for s in line]
        #series = pd.Series(line, index=test_data.columns)
        #new_data = test_data.append(series, ignore_index=True)
        #return new_data
        return line_f


rd = sensor_read()
pos_x0 = 100
pos_x1 = 700

class draw_gui(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.x = 0
        self.resize(1280, 800)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(10)  # 0.01秒間隔で更新

        self.textbox = QLineEdit(self)
        self.textbox.move(10, 10)

    '''
    def create_button(self, size, name):
        button = QPushButton(name)
        button.setMaximumSize(size, size)
        button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        return button
    def draw(self):
        button1 = self.create_button(140, '1')
        button2 = self.create_button(140, '2')
        button3 = self.create_button(140, '3')
        button4 = self.create_button(140, '4')
        button5 = self.create_button(140, '5')
        button6 = self.create_button(140, '6')
        button7 = self.create_button(140, '7')
        button8 = self.create_button(140, '8')
        

        grbox = QGridLayout()
        grbox.addWidget(button1, 0, 0)
        grbox.addWidget(button2, 0, 1)
        grbox.addWidget(button3, 0, 2)
        grbox.addWidget(button4, 0, 3)
        grbox.addWidget(button5, 0, 4)
        grbox.addWidget(button6, 0, 5)
        grbox.addWidget(button7, 0, 6)
        grbox.addWidget(button8, 0, 7)
        self.setLayout(grbox)
    '''

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        painter.setPen(Qt.black)
        painter.setBrush(Qt.white)
        painter.drawRect(100, 400, 100, 100)
        painter.drawRect(250, 400, 100, 100)
        painter.drawRect(400, 400, 100, 100)
        painter.drawRect(550, 400, 100, 100)

        
        new_data = rd.read_test_ser()
        self.x = int((new_data[1] - pos_x0) / (pos_x1-pos_x0) * 1280)
        self.textbox.setText(str(self.x))
        painter.setBrush(Qt.red)
        

        if self.x >= 100 and self.x <= 200:
            painter.drawRect(100, 400, 100, 100)
        elif self.x >=  250 and self.x <= 350:
            painter.drawRect(250, 400, 100, 100)
        elif self.x >=  400 and self.x <= 500:
            painter.drawRect(400, 400, 100, 100)
        elif self.x >= 550 and self.x <= 650:
            painter.drawRect(550, 400, 100, 100)
        
    def main(self):
        #self.paint_rect()
        self.show()
        app.exec_()
    
        
app = QApplication(sys.argv)
window = draw_gui()

if __name__ == '__main__':
    '''
    print("キャリブレーションを行います")
    

    print("座席にしっかりと座ってください")
    rd.my_sleep(400)


    data_xc = np.empty([0, 4])
    data_x0 = np.empty([0, 4])
    data_x1 = np.empty([0, 4])


    for i in range(200):
        line = rd.read_ser("neutral")
        data_xc = np.r_[data_xc, np.array(line).reshape(1, 4)]




    print("足を左に傾けてください")
    rd.my_sleep(400)

    for i in range(200):
        line = rd.read_ser("left")
        #series = pd.Series(line, index=data.columns)
        #print(series)
        #data_x0 = data_x0.append(series, ignore_index=True)
        data_x0 = np.r_[data_x0, np.array(line).reshape(1,4)]

    avg_x0 = np.average(data_x0, axis=0)
    pos_x0 = avg_x0[1]
    print("足を右に傾けてください")
    rd.my_sleep(400)

    for i in range(200):
        line = rd.read_ser("right")
        #series = pd.Series(line, index=data.columns)
        #print(series)
        #data_x1 = data_x1.append(series, ignore_index=True)
        data_x1 = np.r_[data_x1, np.array(line).reshape(1,4)]

    avg_x1 = np.average(data_x1, axis=0)
    pos_x1 = avg_x1[1]


    avg_x_r = (avg_x1 - avg_x0) / 1920
    avg_x_l = (avg_x0 - avg_x1) / 1920



    print(avg_x_r)
    print(avg_x_l)

    
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

    '''

    print("キャリブレーション終了")
    print(pos_x0)
    print(pos_x1)
    #rd.my_sleep(10)
    #old_data = np.array(rd.read_test_ser())
    #pyautogui.moveTo(960, 540)
    
    window.main()
    
    '''
    while True:
        #window.show()
        while ser.in_waiting > 0:
            new_data = rd.read_test_ser()
        pos_x = int((new_data[1] - pos_x0) / (pos_x1-pos_x0) * 1280)
        #pyautogui.moveTo(pos_x, 540);
        print(pos_x)
        #rd.my_sleep(1)
    sys.exit(app.exec_())

    '''
