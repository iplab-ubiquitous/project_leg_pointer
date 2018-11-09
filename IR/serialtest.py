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

window_size_x = 1920
window_size_y = 1080
#window_size = QtGui.qApp.desktop().width()
num_of_sensor = 10
wait_flame = 10
alpha = 0.01
pointer_size = 20
output_path = 'data_p0_leg.csv'


class sensor_read:
    def __init__(self):
        self.ser = serial.Serial('/dev/cu.usbmodem14201', 230400)
        for i in range(10):
            self.ser.readline()  # 読み飛ばし(欠けたデータが読み込まれるのを避ける)

    def read_test_ser(self):
        lst = float(0)
        while self.ser.in_waiting > 1 or lst == float(0):
            lst = self.ser.readline().strip().decode("utf-8").split(',')

        #line_f = [float(s) for s in self.line]
        #return line_f

        return lst


class main_window(QWidget):

    #膝位置計算用変数リセット
    def value_init(self):
        self.sensor_val = np.zeros(num_of_sensor, dtype=np.float)
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

    #実験データ収集用
    #操作時間計測


    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        painter.setPen(Qt.black)
        painter.setBrush(Qt.red)

        for i in range(num_of_sensor):
            painter.drawRect(window_size_x / 12 * (i+1), window_size_y -
                             (64-self.sensor_val[i])*10-100, 40,  (64-self.sensor_val[i])*10)


    def value_upd(self):
        #print(self.left_limit, self.right_limit,self.upper_limit, self.lower_limit)
        tmp = rd.read_test_ser()
        self.sensor_val = [float(v) for v in tmp]

        #指数平均平滑フィルタ
        if np.allclose(self.old_ema, np.zeros(num_of_sensor, dtype=np.float)):
            self.old_ema = self.sensor_val
        else:
            for i in range(num_of_sensor):
                self.new_ema[i] = (
                    self.sensor_val[i] - self.old_ema[i]) * alpha + self.old_ema[i]
            self.old_ema = self.new_ema
        self.sensor_val = self.new_ema
        #指数平均平滑フィルタ

        max_n = np.argmax(self.sensor_val)

        '''
        for i1 in range(max_n-1, -1):
            if self.sensor_val[i1]-20 > self.sensor_val[i1+1]:
                self.sensor_val[i1] = 0
        for i2 in range(max_n, num_of_sensor-1):
            if self.sensor_val[i2] < self.sensor_val[i2+1]-20:
                self.sensor_val[i2+1] = 0
        '''
        self.update()



    def main(self):
        self.show()
        app.exec_()

rd = sensor_read()
app = QApplication(sys.argv)
window = main_window()


if __name__ == '__main__':
    window.main()
