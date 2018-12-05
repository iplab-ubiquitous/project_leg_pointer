#PyQt
import sys
import math
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QGridLayout, QSizePolicy, QLineEdit,
                             QLineEdit, QDialog, QLabel)
from PyQt5.QtGui import QPainter, QFont, QColor, QCursor, QPixmap
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint
#PySerial
import serial
import pyautogui
import numpy as np
import random
import time

window_size_x = 1920
window_size_y = 1080
window_size_x, window_size_y = pyautogui.size()
#window_size = QtGui.qApp.desktop().width()
num_of_sensor = 10
wait_flame = 100
alpha = 0.095
pointer_size = 20
ppi = 102.42  # 研究室のDELLのディスプレイ
#ppi = 94.0   #家のディスプレイ(EV2455)

output_path_log = 'exp_data/leg/log_p1_leg.csv'
output_path_data = 'exp_data/leg/data_p1_leg.csv'


class sensor_read:
    def __init__(self):
        self.ser = serial.Serial('/dev/cu.usbmodem14201', 460800)
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
        #膝検出・位置計算用
        self.sensor_val = np.zeros(num_of_sensor, dtype=np.float)
        self.weight = ([1.00] * num_of_sensor)
        self.val = np.zeros((wait_flame, num_of_sensor), dtype=np.float)
        self.leg_flag = False
        self.sensor_flt = np.zeros((wait_flame, num_of_sensor), dtype=np.float)

        #指数平均平滑フィルタ(EMA)用
        self.old_ema = np.zeros(num_of_sensor, dtype=np.float)
        self.new_ema = np.zeros(num_of_sensor, dtype=np.float)
        self.new_x = 0
        self.old_x = window_size_x / 2
        self.new_y = 0
        self.old_y = window_size_y / 2


        #ウィンドウサイズ
        self.resize(window_size_x, window_size_y)

        #ポインタ座標値
        self.x = 0
        self.y = 0



        #nカウントごとにタイムアウト、タイムアウト時に任意の関数を呼び出す
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.value_upd)
        self.timer.start(5)  # 200fps以下

        #キャリブレーション:左
        self.button_left_calb = QPushButton(self)
        self.button_left_calb.move(0, 50)
        self.button_left_calb.setText("キャリブレーション:左")
        self.button_left_calb.clicked.connect(self.calibration_left)
        self.left_calb_flag = False
        self.left_limit = window_size_x

        #キャリブレーション:右
        self.button_right_calb = QPushButton(self)
        self.button_right_calb.move(200, 50)
        self.button_right_calb.setText("キャリブレーション:右")
        self.button_right_calb.clicked.connect(self.calibration_right)
        self.right_calb_flag = False
        self.right_limit = 0

        #キャリブレーション:上
        self.button_up_calb = QPushButton(self)
        self.button_up_calb.move(0, 100)
        self.button_up_calb.setText("キャリブレーション:上")
        self.button_up_calb.clicked.connect(self.calibration_up)
        self.up_calb_flag = False
        self.upper_limit = window_size_y

        #キャリブレーション:下
        self.button_down_calb = QPushButton(self)
        self.button_down_calb.move(200, 100)
        self.button_down_calb.setText("キャリブレーション:下")
        self.button_down_calb.clicked.connect(self.calibration_down)
        self.down_calb_flag = False
        self.lower_limit = 0

        #リセット
        self.button_reset = QPushButton(self)
        self.button_reset.move(400, 50)
        self.button_reset.setText("リセット")
        self.button_reset.clicked.connect(self.calibration_reset)

        #座標値(x,y)と衝突円の番号(t)の出力
        self.textlabel_x = QLabel(self)
        self.textlabel_x.setText("X：")
        self.textlabel_x.move(10, 0)
        self.textbox_x = QLineEdit(self)
        self.textbox_x.move(10, 20)
        self.textbox_x.resize(40, 20)

        self.textlabel_y = QLabel(self)
        self.textlabel_y.setText("Y：")
        self.textlabel_y.move(60, 0)
        self.textbox_y = QLineEdit(self)
        self.textbox_y.move(60, 20)
        self.textbox_y.resize(40, 20)


        self.cursor_hider = QCursor(QPixmap("bitmap.png"))


    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        self.textbox_x.setText(str(int(self.x)))  # 座標確認用
        self.textbox_y.setText(str(int(self.y)))  # 座標確認用
        painter.setPen(Qt.black)
        #painter.setBrush(Qt.red)
        #painter.drawEllipse(self.x, self.y, pointer_size, pointer_size)
        painter.setBrush(Qt.red)
        painter.drawEllipse(self.x, self.y, pointer_size, pointer_size)
    #膝位置計算

    def pointer_calc(self, sensor_val, flag):
        x = 0
        y = 0
        #print(left_limit, right_limit, upper_limit, lower_limit)
        
        #指数平均平滑フィルタ
        if np.allclose(self.old_ema, np.zeros(num_of_sensor, dtype=np.float)):
            self.old_ema = sensor_val
        else:
            for i in range(num_of_sensor):
                self.new_ema[i] = (
                    sensor_val[i] - self.old_ema[i]) * alpha + self.old_ema[i]
            self.old_ema = self.new_ema
        sensor_val = self.new_ema
        #指数平均平滑フィルタ

        
        for i in range(wait_flame-1):
            self.sensor_flt[i+1, :] = self.sensor_flt[i, :]
        n_sensor_val = np.zeros(num_of_sensor, dtype=np.float)
        max_val = np.max(sensor_val)
        near_snum = []
        for v in range(num_of_sensor):
            if sensor_val[v] < (max_val) * 0.6:
                self.sensor_flt[0, v] = sensor_val[v]*0.1
            else:
                near_snum.append(v)
                self.sensor_flt[0, v] = sensor_val[v]
        for v in range(num_of_sensor):
            if v in near_snum:
                n_sensor_val[v] = np.average(self.sensor_flt[:, v])

            else:
                n_sensor_val[v] = np.average(
                    self.sensor_flt[[1, wait_flame-1], v])*0.9 + self.sensor_flt[0, v] * 0.1

        sensor_val = n_sensor_val

        if self.leg_flag:
            #y座標計算
            top_sensor = np.argsort(-sensor_val)
            self.new_y = (max(sensor_val)-52)
            #self.new_y = (window_size_y) * (59.0-max(sensor_val)) / 59.0-52.0
            #self.new_y = (window_size_y) * (59.0 - sensor_val[int(np.median(near_snum))]) / 59.0-52.0
            #self.new_y = (window_size_y) * (59.0 - np.average([sensor_val[v] for v in near_snum])) / 59.0-52.0

            #x座標計算
            for i in range(num_of_sensor):
                if i > 6:
                    sensor_val[top_sensor[i]] = 0
            for i in range(num_of_sensor):
                self.weight[i] = 1 / (max(sensor_val) - sensor_val[i] + 2)
            s = sum(self.weight)
            self.new_x = -2
            for j in range(num_of_sensor):
                self.new_x += ((j * self.weight[j] / s) * 3)
            #self.new_x *= (window_size_x / 9)

            '''
            #座標平滑フィルタ
            if self.old_x == window_size_x / 2:
                self.old_x = self.new_x
            else:
                self.new_x = (self.new_x - self.old_x) * alpha + self.old_x
                self.old_x = self.new_x

            if self.old_y == window_size_y / 2:
                self.old_y = self.new_y
            else:
                self.new_y = (self.new_y - self.old_y) * alpha + self.old_y
                self.old_y = self.new_y
            '''

            #x = (window_size_x) * (self.new_x - left_limit) / \
            #    (right_limit-left_limit)
            #y = (window_size_y) * (self.new_y - upper_limit) / \
            #    (lower_limit-upper_limit)
            if self.new_x < self.left_limit:
                self.left_limit = self.new_x
            if self.new_x > self.right_limit:
                self.right_limit = self.new_x
            print([self.left_limit, self.right_limit, self.new_x])


            
            if self.new_x < (self.right_limit-self.left_limit) * 1/9 + self.left_limit:
                x = -16
            elif self.new_x < (self.right_limit-self.left_limit) * 2/9 + self.left_limit:
                x = -9
            elif self.new_x < (self.right_limit-self.left_limit) * 3/9 + self.left_limit:
                x = -4
            elif self.new_x < (self.right_limit-self.left_limit) * 4/9 + self.left_limit:
                x = -1
            elif self.new_x < (self.right_limit-self.left_limit) * 5/9 + self.left_limit:
                x = 0
            elif self.new_x < (self.right_limit-self.left_limit) * 6/9 + self.left_limit:
                x = 1
            elif self.new_x < (self.right_limit-self.left_limit) * 7/9 + self.left_limit:
                x = 4
            elif self.new_x < (self.right_limit-self.left_limit) * 8/9 + self.left_limit:
                x = 9
            else:
                x = 16
            

        return x

    #左方向キャリブレーション
    def calibration_left(self):
        x = 0
        y = 0
        if not self.left_calb_flag:
            for i in range(200):
                tmp = rd.read_test_ser()
                val = [64-float(v) for v in tmp]
                x, y = self.pointer_calc(
                    val, 0, window_size_x, 0, window_size_y, True)
            self.left_limit = x
            #print(lst)
            self.left_calb_flag = True
            self.ema_reset()

    #右方向キャリブレーション
    def calibration_right(self):
        x = 0
        y = 0
        if not self.right_calb_flag:
            for i in range(200):
                tmp = rd.read_test_ser()
                val = [64-float(v) for v in tmp]
                x, y = self.pointer_calc(
                    val, 0, window_size_x, 0, window_size_y, True)
            self.right_limit = x
            #print(lst)
            self.right_calb_flag = True
            self.ema_reset()

    #上方向キャリブレーション
    def calibration_up(self):
        x = 0
        y = 0
        if not self.up_calb_flag:
            for i in range(200):
                tmp = rd.read_test_ser()
                val = [64-float(v) for v in tmp]
                x, y = self.pointer_calc(
                    val, 0, window_size_x, 0, window_size_y, True)
            self.upper_limit = y
            #print(lst)
            self.up_calb_flag = True
            self.ema_reset()

    #下方向キャリブレーション
    def calibration_down(self):
        x = 0
        y = 0
        if not self.down_calb_flag:
            for i in range(200):
                tmp = rd.read_test_ser()
                val = [64-float(v) for v in tmp]
                x, y = self.pointer_calc(
                    val, 0, window_size_x, 0, window_size_y, True)
            self.lower_limit = y
            #print(lst)
            self.down_calb_flag = True
            self.ema_reset()

    def calibration_check(self):
        return self.left_calb_flag and self.right_calb_flag and self.up_calb_flag and self.down_calb_flag

    def calibration_reset(self):
        self.left_calb_flag = True
        self.right_calb_flag = True
        self.up_calb_flag = True
        self.down_calb_flag = True

    def value_upd(self):
        #print(self.left_limit, self.right_limit,self.upper_limit, self.lower_limit)
        self.value_init()
        self.new_x = 0
        not_update = True
        tmp = rd.read_test_ser()
        sensor_val = [64-float(v) for v in tmp]
        #膝検出
        self.leg_flag = False
        pick = 0
        for i in range(num_of_sensor):
            pick += sensor_val[i] > 20
            if(pick > 3):
                self.leg_flag = True
                break
        #膝検出
        if self.calibration_check():
            y = self.pointer_calc(
                sensor_val, self.leg_flag)
            self.y += y

        #衝突判定
        self.update()
    def main(self):
        self.show()
        app.exec_()


rd = sensor_read()
app = QApplication(sys.argv)
window = main_window()


if __name__ == '__main__':
    window.main()
