#PyQt
import sys, math
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QGridLayout, QSizePolicy, QLineEdit,
                             QLineEdit, QDialog, QLabel)
from PyQt5.QtGui import QPainter, QFont, QColor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint
#PySerial
import pyautogui
import numpy as np
import random
import time

window_size_x = 1920
window_size_y = 1080
#window_size = QtGui.qApp.desktop().width()
pointer_size = 20

output_path = 'data_p0_mouse.csv'





class main_window(QWidget):
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
    def set_target(self):
        #self.target_order = list(range(self.num_of_targets))
        #random.shuffle(self.target_order)

        self.target_order = [0]
        n = 0
        for i in range(self.num_of_targets):
            n += int(self.num_of_targets/2)
            self.target_order.append(n % self.num_of_targets)
        print(self.target_order)
        self.order_num = 0
        
        self.target_point = []
        for i in range(self.num_of_targets):
            cx = window_size_x / 2 + self.radius*math.cos(2 * math.pi * (float(i) / self.num_of_targets))
            cy = window_size_y / 2 + self.radius*math.sin(2 * math.pi * (float(i) / self.num_of_targets))
            self.target_point.append(QPoint(cx, cy))

    def __init__(self, parent=None):
        super().__init__(parent)
        #実験条件
        self.num_of_targets = 13
        self.radius = 300
        self.target_radius = 40

        #ウィンドウサイズ
        self.resize(window_size_x, window_size_y)

        #ポインタ座標値
        self.x = 0
        self.y = 0

        #実験データ収集
        self.exp_timer_init()
        self.exp_end_flag = False
        self.miss = 0
        self.amplitude = 0
        self.result = np.empty((0, 5), float)
        
        #衝突判定とターゲット位置計算
        self.collision_flag = False
        self.collision_num = 0
        self.set_target()


        self.timer = QTimer(self)
        self.timer.timeout.connect(self.value_upd)
        self.timer.start(5)  # smaller than200Hz

        #座標値(x,y)と衝突円の番号(t)の出力
        self.textlabel_x = QLabel(self)
        self.textlabel_x.setText("X：")
        self.textlabel_x.move(10,0)
        self.textbox_x = QLineEdit(self)
        self.textbox_x.move(10, 20)
        self.textbox_x.resize(40,20)

        self.textlabel_y = QLabel(self)
        self.textlabel_y.setText("Y：")
        self.textlabel_y.move(60, 0)
        self.textbox_y = QLineEdit(self)
        self.textbox_y.move(60, 20)
        self.textbox_y.resize(40, 20)

        self.textbox_t = QLineEdit(self)
        self.textbox_t.move(window_size_x/2, window_size_y/2)
        self.textbox_t.resize(70, 20)

        self.num_of_targets_label = QLabel(self)
        self.num_of_targets_label.setText("ターゲット数")
        self.num_of_targets_label.move(200, 0)
        self.set_num_of_target = QLineEdit(self)
        self.set_num_of_target.move(200, 20)
        self.set_num_of_target.setText(str(self.num_of_targets))
        self.set_num_of_target.resize(100, 20)

        self.radius_label = QLabel(self)
        self.radius_label.setText("ターゲット距離")
        self.radius_label.move(350, 0)
        self.set_radius = QLineEdit(self)
        self.set_radius.move(350, 20)
        self.set_radius.setText(str(self.radius))
        self.set_radius.resize(100, 20)

        self.target_radius_label = QLabel(self)
        self.target_radius_label.setText("ターゲット半径")
        self.target_radius_label.move(500, 0)
        self.set_target_radius = QLineEdit(self)
        self.set_target_radius.move(500, 20)
        self.set_target_radius.setText(str(self.target_radius))
        self.set_target_radius.resize(100, 20)

        self.button_exec = QPushButton(self)
        self.button_exec.move(700, 20)
        self.button_exec.setText("設定")
        self.button_exec.clicked.connect(self.set_target_config)

        #self.pos[num_of_sensor-1] = window_size_x + abs(self.pos[0])
    def exp_timer_init(self):
        self.start = 0
        self.selected = 0
    def exp_timer_start(self):
        self.start = time.time()
    def exp_timer_select(self):
        self.selected = time.time()-self.start 
        print('direction:' + str(self.target_order[self.order_num-1]) + '->' + str(
            self.target_order[self.order_num]))
        print('time: ' + str(self.selected))
        self.amplitude = self.calc_amplitude(self.order_num, self.order_num-1)
        print('amplitude: ' + str(self.amplitude))
        self.result = np.append(self.result, np.array([[self.radius, self.target_radius, self.selected, self.amplitude, 1+self.amplitude/self.target_radius]]), axis=0)
        
        self.start = time.time()
    def exp_timer_stop(self):
        print('selection miss: ' + str(self.miss) + ' time(s)')
        print(self.result)
        np.savetxt(output_path, self.result, delimiter=',', fmt=[
                   '%.0f', '%.0f', '%.5f', '%.5f', '%.5f'], header='radius, width, time, distance, ID', comments='')
        self.exp_timer_init()

    def calc_amplitude(self, n1, n2):
        return math.sqrt(math.pow(self.target_point[self.target_order[n1]].x() - self.target_point[self.target_order[n2]].x(), 2) + math.pow(self.target_point[self.target_order[n1]].y() - self.target_point[self.target_order[n2]].y(), 2))


    def set_target_config(self):
        self.num_of_targets = int(self.set_num_of_target.text())
        self.radius = int(self.set_radius.text())
        self.target_radius = int(self.set_target_radius.text())
        self.set_target()
        self.exp_end_flag = False
        self.miss = 0
        self.update()

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        self.textbox_x.setText(str(int(self.x)))  # 座標確認用
        self.textbox_y.setText(str(int(self.y)))  # 座標確認用
        painter.setPen(Qt.black)
        #painter.setBrush(Qt.red)
        #painter.drawEllipse(self.x, self.y, pointer_size, pointer_size)
        
        if not self.exp_end_flag:
            painter.setBrush(QColor(0x48, 0xcb, 0xeb))
            for i in range(self.num_of_targets):
                painter.drawEllipse(
                    self.target_point[i], self.target_radius, self.target_radius)
            painter.setBrush(QColor(0x00, 0x00, 0xff))
            painter.drawEllipse(self.target_point[self.target_order[self.order_num]], self.target_radius, self.target_radius)
        else:
            painter.setBrush(QColor(0xff, 0xff, 0xff))
            for i in range(self.num_of_targets):
                painter.drawEllipse(
                    self.target_point[i], self.target_radius, self.target_radius)
        if self.collision_flag: 
            painter.setBrush(Qt.white)
            painter.drawEllipse(self.target_point[self.collision_num], self.target_radius, self.target_radius)
            self.textbox_t.setText(str(self.collision_num))

    def keyPressEvent(self, keyevent):
        #print(keyevent.key())
        if keyevent.key() == Qt.Key_Shift and self.collision_flag:  # Key:Z
            if self.order_num == 0 :
                self.exp_timer_start()
            elif self.order_num == self.num_of_targets - 1:
                self.exp_timer_select()
                self.exp_timer_stop()
                self.exp_end_flag = True
            else:
                self.exp_timer_select()
            
            if not self.collision_num == self.target_order[self.order_num]:
                self.miss += 1
            self.order_num += 1
            self.order_num = self.order_num % self.num_of_targets

    def value_upd(self):
        self.x, self.y = pyautogui.position()
        self.update()
        

    def main(self):
        self.show()
        app.exec_()

app = QApplication(sys.argv)
window = main_window()


if __name__ == '__main__':
    window.main()
