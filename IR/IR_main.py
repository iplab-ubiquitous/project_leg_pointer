#PyQt
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QGridLayout, QSizePolicy, QLineEdit,
                             QLineEdit)
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
#PySerial
import serial
import numpy as np

window_size_x = 1280
window_size_y = 720
#window_size = QtGui.qApp.desktop().width()
num_of_sensor = 10
wait_flame = 10
alpha = 0.1


class sensor_read:
    def __init__(self):
        self.ser = serial.Serial('/dev/cu.usbmodem1421', 115200)
        for i in range(10):
            self.ser.readline()  # 読み飛ばし(欠けたデータが読み込まれるのを避ける)

    def read_test_ser(self):
        lst = float(0)
        while self.ser.in_waiting > 1 or lst == float(0):
            lst = self.ser.readline().strip().decode("utf-8").split(',')
            
        #line_f = [float(s) for s in self.line]
        #return line_f

        return lst


class draw_gui(QWidget):
    def value_init(self):
        self.sensor_val = np.zeros(num_of_sensor, dtype=np.float)
        self.weight = ([1.00] * num_of_sensor)

    def ema_reset(self):
        self.old_ema = np.zeros(num_of_sensor, dtype=np.float)
        self.new_ema = np.zeros(num_of_sensor, dtype=np.float)
        self.new_x = 0
        self.old_x = window_size_x / 2
        self.new_y = 0
        self.old_y = window_size_y / 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sensor_val = np.zeros(num_of_sensor, dtype=np.float)
        self.weight = ([1.00] * num_of_sensor)
        self.pos = np.zeros(num_of_sensor, dtype=np.float)
        self.val = np.zeros((wait_flame, num_of_sensor), dtype=np.float)
        self.flag = False

        self.old_ema = np.zeros(num_of_sensor, dtype=np.float)
        self.new_ema = np.zeros(num_of_sensor, dtype=np.float)
        self.new_x = 0
        self.old_x = window_size_x / 2
        self.new_y = 0
        self.old_y = window_size_y / 2
        self.x = 0
        self.y = 0
        self.resize(window_size_x, window_size_y)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.value_upd)
        #self.timer.timeout.connect(self.value_upd_y)
        self.timer.start(10)  # 100Hz

        self.button_left_calb = QPushButton(self)
        self.button_right_calb = QPushButton(self)
        self.button_up_calb = QPushButton(self)
        self.button_down_calb = QPushButton(self)
        self.button_reset = QPushButton(self)

        self.button_left_calb.move(0, 50)
        self.button_left_calb.setText("キャリブレーション:左")
        self.button_left_calb.clicked.connect(self.calibration_left)
        self.left_calb_flag = False
        self.left_limit = window_size_x

        self.button_right_calb.move(200, 50)
        self.button_right_calb.setText("キャリブレーション:右")
        self.button_right_calb.clicked.connect(self.calibration_right)
        self.right_calb_flag = False
        self.right_limit = 0

        self.button_up_calb.move(0, 100)
        self.button_up_calb.setText("キャリブレーション:上")
        self.button_up_calb.clicked.connect(self.calibration_up)
        self.up_calb_flag = False
        self.upper_limit = window_size_y

        self.button_down_calb.move(200, 100)
        self.button_down_calb.setText("キャリブレーション:下")
        self.button_down_calb.clicked.connect(self.calibration_down)
        self.down_calb_flag = False
        self.lower_limit = 0

        self.button_reset.move(400, 50)
        self.button_reset.setText("リセット")
        self.button_reset.clicked.connect(self.calibration_reset)

        self.textbox_x = QLineEdit(self)
        self.textbox_x.move(10, 10)
        self.textbox_y = QLineEdit(self)
        self.textbox_y.move(150, 10)

        for i in range(num_of_sensor):
            self.pos[i] = (window_size_x / 7) * (i-1)
        #self.pos[num_of_sensor-1] = window_size_x + abs(self.pos[0])
        print(self.pos)
    
    #描画と数値計算を直列でやっている
    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        self.textbox_x.setText(str(int(self.x)))  # 座標確認用
        self.textbox_y.setText(str(int(self.y)))  # 座標確認用
        painter.setPen(Qt.black)
        if self.flag:
            painter.setBrush(Qt.red)
        else:
            painter.setBrush(Qt.blue)
        painter.drawRect(self.x, self.y, 20, 20)

    def pointer_calc(self, sensor_val, left_limit, right_limit, upper_limit, lower_limit, flag):
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

        if flag:
            #y座標計算
            self.new_y = (window_size_y) * (min(sensor_val)-5.0) / 12.0-5.0
            #y座標計算
            
            #x座標計算
            for i in range(num_of_sensor):
                self.weight[i] = 1 / (sensor_val[i] - min(sensor_val) + 2)
            s = sum(self.weight)
            self.new_x = -2
            for j in range(num_of_sensor):
                self.new_x += ((j * self.weight[j] / s) * 1.5)
            self.new_x *= (window_size_x / 9)
            #x座標計算

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
                print(self.new_y)
            #座標平滑フィルタ
            
            x = (window_size_x) * (self.new_x - left_limit) / (right_limit-left_limit)
            y = (window_size_y) * (self.new_y - upper_limit) / (lower_limit-upper_limit)
        return x, y
        
    def calibration_left(self):
        x = 0
        y = 0
        if not self.left_calb_flag:
            for i in range(30):
                tmp = rd.read_test_ser()
                val = [float(v) for v in tmp]
                x, y = self.pointer_calc(val, 0, window_size_x, 0, window_size_y
                , True)
            self.left_limit = x
            #print(lst)
            self.left_calb_flag = True
            self.ema_reset()
    

    def calibration_right(self):
        x = 0
        y = 0
        if not self.right_calb_flag:
            for i in range(30):
                tmp = rd.read_test_ser()
                val = [float(v) for v in tmp]
                x, y = self.pointer_calc(val, 0, window_size_x, 0, window_size_y, True)
            self.right_limit = x
            #print(lst)
            self.right_calb_flag = True
            self.ema_reset()

    def calibration_up(self):
        x = 0
        y = 0
        if not self.up_calb_flag:
            for i in range(200):
                tmp = rd.read_test_ser()
                val = [float(v) for v in tmp]
                x, y = self.pointer_calc(val, 0, window_size_x, 0, window_size_y, True)
            self.upper_limit = y
            #print(lst)
            self.up_calb_flag = True
            self.ema_reset()

    def calibration_down(self):
        x = 0
        y = 0
        if not self.down_calb_flag:
            for i in range(200):
                tmp = rd.read_test_ser()
                val = [float(v) for v in tmp]
                x, y = self.pointer_calc(val, 0, window_size_x, 0, window_size_y, True)
            self.lower_limit = y
            #print(lst)
            self.down_calb_flag = True
            self.ema_reset()
    
    def calibration_check(self):
        return self.left_calb_flag and self.right_calb_flag and self.up_calb_flag and self.down_calb_flag

    def calibration_reset(self):
        self.left_calb_flag = False
        self.right_calb_flag = False
        self.up_calb_flag = False
        self.down_calb_flag = False


    

    def value_upd(self):
        print(self.left_limit, self.right_limit, self.upper_limit, self.lower_limit)
        self.value_init()
        self.new_x = 0
        not_update = True
        tmp = rd.read_test_ser()
        sensor_val = [float(v) for v in tmp]
        #膝検出
        self.flag = False
        pick = 0
        for i in range(num_of_sensor):
            pick += sensor_val[i] < 50
            if(pick > 3):
                self.flag = True
                break
        #膝検出
        if self.calibration_check():
            self.x, self.y = self.pointer_calc(sensor_val, self.left_limit, self.right_limit, self.upper_limit, self.lower_limit, self.flag)
        self.update()

    def main(self):
        self.show()
        app.exec_()


rd = sensor_read()
app = QApplication(sys.argv)
window = draw_gui()


if __name__ == '__main__':
    window.main()
