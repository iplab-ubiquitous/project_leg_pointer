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
sensor_val = np.zeros(num_of_sensor, dtype=np.float)
weight = ([64.00] * num_of_sensor)
pos = np.zeros(num_of_sensor, dtype=np.float)


class sensor_read:
    def __init__(self):
        self.ser = serial.Serial('/dev/cu.usbmodem1421', 115200)
        for i in range(10):
            self.ser.readline()  # 読み飛ばし(欠けたデータが読み込まれるのを避ける)

    def read_test_ser(self):
        lst = float(0)
        while self.ser.in_waiting > 1 or lst == float(0):
            lst = self.ser.readline().strip().decode("utf-8").split(',')
            print(lst)
            print(type(lst))

        #line_f = [float(s) for s in self.line]
        #return line_f

        return lst


class draw_gui(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pos_x0 = 0
        self.pos_x1 = 0
        self.pos_y0 = 0
        self.pos_y1 = 0
        self.old_x = window_size_x/2
        self.new_x = 0
        self.old_y = window_size_y/2
        self.new_y = 0
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

        self.button_right_calb.move(200, 50)
        self.button_right_calb.setText("キャリブレーション:右")
        self.button_right_calb.clicked.connect(self.calibration_right)
        self.right_calb_flag = False

        self.button_up_calb.move(0, 100)
        self.button_up_calb.setText("キャリブレーション:上")
        self.button_up_calb.clicked.connect(self.calibration_up)
        self.up_calb_flag = False

        self.button_down_calb.move(200, 100)
        self.button_down_calb.setText("キャリブレーション:下")
        self.button_down_calb.clicked.connect(self.calibration_down)
        self.down_calb_flag = False

        self.button_reset.move(400, 50)
        self.button_reset.setText("リセット")
        self.button_reset.clicked.connect(self.calibration_reset)

        self.textbox = QLineEdit(self)
        self.textbox.move(10, 10)

        for i in range(num_of_sensor):
            pos[i] = (window_size_x / -2) + ((window_size_x / 10) * i)

        #pyautogui.FAILSAFE = False

    #描画と数値計算を直列でやっている

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        self.textbox.setText(str(self.new_x-640))  # 座標確認用
        painter.setPen(Qt.black)
        painter.setBrush(Qt.red)
        painter.drawRect(self.new_x, self.new_y, 20, 20)

        '''
        painter.drawRect(100, 400, 100, 100)
        painter.drawRect(250, 400, 100, 100)
        painter.drawRect(400, 400, 100, 100)
        painter.drawRect(550, 400, 100, 100)
        painter.setBrush(Qt.red)  # 座標と重なっている四角形は赤く塗る
        if self.x >= 100 and self.x <= 200:
            painter.drawRect(100, 400, 100, 100)
        elif self.x >= 250 and self.x <= 350:
            painter.drawRect(250, 400, 100, 100)
        elif self.x >= 400 and self.x <= 500:
            painter.drawRect(400, 400, 100, 100)
        elif self.x >= 550 and self.x <= 650:
            painter.drawRect(550, 400, 100, 100)
        '''  # この部分をスレッド化
        ##################

        #座標とどの四角形が重なっているかの当たり判定'''
    def calibration_left(self):
        if not self.left_calb_flag:
            lst = []
            for i in range(100):
                lst = rd.read_test_ser()
            print(lst)
            self.left_calb_flag = True

    def calibration_right(self):
        if not self.right_calb_flag:
            lst = []
            for i in range(100):
                lst = rd.read_test_ser()
            print(lst)
            self.right_calb_flag = True

    def calibration_up(self):
        if not self.up_calb_flag:
            lst = []
            for i in range(100):
                lst = rd.read_test_ser()
            print(lst)
            self.up_calb_flag = True

    def calibration_down(self):
        if not self.down_calb_flag:
            lst = []
            for i in range(100):
                lst = rd.read_test_ser()
            print(lst)
            self.down_calb_flag = True

    def calibration_reset(self):
        self.left_calb_flag = False
        self.right_calb_flag = False
        self.up_calb_flag = False
        self.down_calb_flag = False

    def value_upd(self):
        sensor_val = rd.read_test_ser()
        print(sensor_val)

 
    def main(self):
        self.show()
        app.exec_()


rd = sensor_read()
#pos_x0 = 0  # 画面左端を示すセンサ値(仮)  x=0
#pos_x1 = 0  # 画面右端を示すセンサ値(仮)  x=1920
app = QApplication(sys.argv)
window = draw_gui()


if __name__ == '__main__':
    window.main()
