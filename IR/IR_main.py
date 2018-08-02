#PyQt
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QGridLayout, QSizePolicy, QLineEdit,
                             QLineEdit)
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
#PySerial
import serial

window_size = 1280
#window_size = QtGui.qApp.desktop().width()


class sensor_read:
    def __init__(self):
        self.ser = serial.Serial('/dev/cu.usbmodem1421', 9600)
        for i in range(10):
            self.ser.readline()  # 読み飛ばし(欠けたデータが読み込まれるのを避ける)

    def read_test_ser(self):
        line = float(0)
        while self.ser.in_waiting > 0:
            line = self.ser.readline().strip().decode('utf-8')  # .split(",")
        #line_f = [float(s) for s in self.line]
        #return line_f

        return float(line)


class draw_gui(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.old_x = window_size/2
        self.new_x = 0
        self.resize(window_size, int(window_size*16/10))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.value_upd)
        self.timer.start(50)  # 20Hz

        self.button_left_calb = QPushButton(self)
        self.button_right_calb = QPushButton(self)
        self.button_reset = QPushButton(self)

        self.button_left_calb.move(0, 50)
        self.button_left_calb.setText("キャリブレーション:左")
        self.button_left_calb.clicked.connect(self.calibration_left)
        self.left_calb_flag = False

        self.button_right_calb.move(200, 50)
        self.button_right_calb.setText("キャリブレーション:右")
        self.button_right_calb.clicked.connect(self.calibration_right)
        self.right_calb_flag = False

        self.button_reset.move(400, 50)
        self.button_reset.setText("リセット")
        self.button_reset.clicked.connect(self.calibration_reset)

        self.textbox = QLineEdit(self)
        self.textbox.move(10, 10)

    #描画と数値計算を直列でやっている
    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        self.textbox.setText(str(self.new_x))  # 座標確認用
        painter.setPen(Qt.black)
        painter.setBrush(Qt.red)
        painter.drawRect(self.new_x, 400, 20, 20)
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
            for i in range(200):
                val = rd.read_test_ser()
                lst.append(val)
            pos_x0 = min(lst)
            self.left_calb_flag = True

    def calibration_right(self):
        if not self.right_calb_flag:
            lst = []
            for i in range(200):
                val = rd.read_test_ser()
                lst.append(val)
            pos_x1 = max(lst)
            self.right_calb_flag = True

    def calibration_reset(self):
        self.left_calb_flag = False
        self.right_calb_flag = False

    def value_upd(self):
        if self.left_calb_flag and self.right_calb_flag:
            new_data = rd.read_test_ser()  # シリアル読み取り
            # センサ値から画面上のカーソル位置を計算
            self.new_x = int((new_data - pos_x0) /
                             (pos_x1-pos_x0) * window_size)
            if (self.new_x > 0 and self.new_x < 1280)and(abs(self.new_x - self.old_x) > 10):
                self.update()
            self.old_x = self.new_x
            #print(new_data)

    def main(self):
        self.show()
        app.exec_()


rd = sensor_read()
pos_x0 = 600  # 画面左端を示すセンサ値(仮)  x=0
pos_x1 = 400  # 画面右端を示すセンサ値(仮)  x=1920
app = QApplication(sys.argv)
window = draw_gui()


if __name__ == '__main__':
    window.main()
