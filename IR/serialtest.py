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
wait_flame = 8
sensor_val = np.zeros(num_of_sensor, dtype=np.float)
weight = ([64.00] * num_of_sensor)
pos = np.zeros(num_of_sensor, dtype=np.float)
val = np.zeros((wait_flame, num_of_sensor), dtype=np.float)

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

        return lst


class draw_gui(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.new_y_arr = np.zeros(num_of_sensor, dtype=np.float)
        self.resize(window_size_x, window_size_y)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.value_upd)
        self.timer.start(10)  # 100Hz
        




        self.textbox = QLineEdit(self)
        self.textbox.move(10, 10)

        for i in range(num_of_sensor):
            pos[i] = (window_size_x / -2) + ((window_size_x / 10) * i)

        #pyautogui.FAILSAFE = False
        self.old_ema = np.zeros(num_of_sensor, dtype=np.float)
        self.new_ema = np.zeros(num_of_sensor, dtype=np.float)
    #描画と数値計算を直列でやっている

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        self.textbox.setText(str(int(min(self.new_y_arr))))  # 座標確認用
        painter.setPen(Qt.black)
        painter.setBrush(Qt.red)
        for i in range(num_of_sensor):
            painter.drawRect(i*50+240, self.new_y_arr[i], 20, 20)

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
  
    def value_upd(self):
        tmp = rd.read_test_ser()
        sensor_val = [float(v) for v in tmp]

        for i in range(1, wait_flame):
            val[i-1] = val[i]
        val[wait_flame-1] = sensor_val
        #加重平均フィルタ
        '''
        for i in range(num_of_sensor):
            s = 0
            l = 0
            for j in range(wait_flame):
                s += (wait_flame - j) * val[j][i]
                l += j+1
            sensor_val[i] = s / l
            val[wait_flame-1][i] = sensor_val[i]
        print(sensor_val)
        '''
        #指数平均フィルタ
        if np.allclose(self.old_ema, np.zeros(num_of_sensor, dtype=np.float)):
            self.old_ema = sensor_val
        else:
            for i in range(num_of_sensor):
                self.new_ema[i] = (sensor_val[i] - self.old_ema[i]) * alpha + self.old_ema[i]
            for i in range(num_of_sensor):
                self.new_y_arr[i] = (window_size_y-20) * self.new_ema[i] / 64.0
            self.old_ema = self.new_ema
        self.update()


        

 
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
