#PyQt
import sys, math
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QGridLayout, QSizePolicy, QLineEdit,
                             QLineEdit, QDialog, QLabel)
from PyQt5.QtGui import QPainter, QFont, QColor, QCursor ,QPixmap
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
ppi = 102.42 #研究室のDELLのディスプレイ
#ppi = 94.0   #家のディスプレイ(EV2455)

output_path_log = 'exp_data/mouse/log_p0_mouse.csv'
output_path_data = 'exp_data/mouse/data_p0_mouse.csv'





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
            cx = window_size_x / 2 + self.radius * \
                math.cos(2 * math.pi * (float(i) /
                                        self.num_of_targets) - (math.pi/2))
            cy = window_size_y / 2 + self.radius * \
                math.sin(2 * math.pi * (float(i) /
                                        self.num_of_targets) - (math.pi/2))
            self.target_point.append(QPoint(cx, cy))
    
    def inch_to_pixel(self, val):
        return val * ppi
    def pixel_to_inch(self, val):
        return val / ppi

    def __init__(self, parent=None):
        super().__init__(parent)

        #実験条件
        self.num_of_targets = 13  # ターゲット数
        self.radius = self.inch_to_pixel(1.0)  # 全体の円の直径
        self.target_radius = self.inch_to_pixel(0.5)  # ターゲット円の直径

        #ウィンドウサイズ
        self.resize(window_size_x, window_size_y)

        #ポインタ座標値
        self.x = 0
        self.y = 0

        #実験データ収集
        self.exp_timer_init()
        self.exp_start_flag = False
        self.exp_end_flag = False
        self.exp_num = 0
        self.miss = 0
        self.miss_flag = False
        self.clicked = 0
        self.amplitude = 0
        self.logger = np.empty((0,6),float)
        self.data = np.empty((0, 6), float)
        
        #衝突判定とターゲット位置計算
        self.collision_flag = False
        #self.collision_nums = []
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

        #self.textbox_t = QLineEdit(self)
        #self.textbox_t.move(window_size_x/2, window_size_y/2)
        #self.textbox_t.resize(70, 20)

        self.num_of_targets_label = QLabel(self)
        self.num_of_targets_label.setText("ターゲット数")
        self.num_of_targets_label.move(200, 0)
        self.set_num_of_target = QLineEdit(self)
        self.set_num_of_target.move(200, 20)
        self.set_num_of_target.setText(str(self.num_of_targets))
        self.set_num_of_target.resize(100, 20)

        self.radius_label = QLabel(self)
        self.radius_label.setText("D = ")
        self.radius_label.move(350, 0)
        self.set_radius = QLineEdit(self)
        self.set_radius.move(350, 20)
        self.set_radius.setText(str(self.pixel_to_inch(self.radius)))
        self.set_radius.resize(100, 20)

        self.target_radius_label = QLabel(self)
        self.target_radius_label.setText("W = ")
        self.target_radius_label.move(500, 0)
        self.set_target_radius = QLineEdit(self)
        self.set_target_radius.move(500, 20)
        self.set_target_radius.setText(str(self.pixel_to_inch(self.target_radius)))

        self.set_target_radius.resize(100, 20)

        self.button_exec = QPushButton(self)
        self.button_exec.move(700, 20)
        self.button_exec.setText("設定")
        self.button_exec.clicked.connect(self.set_target_config)

        self.cursor_hider = QCursor(QPixmap("bitmap.png"))

        #self.pos[num_of_sensor-1] = window_size_x + abs(self.pos[0])
    def data_log(self):
        if self.exp_start_flag:
            dist = self.calc_amplitude(
                self.target_point[self.target_order[self.order_num]].x(), self.x, self.target_point[self.target_order[self.order_num]].y(), self.y)
            tm = time.time()-self.start
            self.logger = np.append(self.logger, np.array(
                [[self.exp_num,  self.x, self.y, self.clicked, self.miss, tm]]), axis=0)
            self.miss_flag = False
    def exp_timer_init(self):
        self.start = 0
        self.tstamp = 0
        self.exp_start_flag = False
    def exp_timer_clicked(self):
        if self.order_num > 0:
            tm = time.time()-self.tstamp
            self.data = np.append(self.data, np.array([[self.exp_num, self.order_num, tm, self.pixel_to_inch(self.radius*2), math.log2(
                1+self.pixel_to_inch(self.radius*2)/self.pixel_to_inch(self.target_radius*2)), self.miss_flag]]), axis=0)
            
        self.tstamp = time.time()
    def exp_timer_stop(self):
        self.exp_start_flag = False
        self.exp_end_flag = True
        QApplication.setOverrideCursor(Qt.ArrowCursor)

        tm = time.time()-self.start
        self.logger = np.append(self.logger, np.array(
            [[self.exp_num, self.x, self.y, self.clicked, self.miss, tm]]), axis=0)
        print('selection miss: ' + str(self.miss) + ' time(s)')
        np.savetxt(output_path_log, self.logger, delimiter=',', fmt=[
                   '%.0f', '%.0f', '%.0f', '%.0f', '%.0f', '%.3f'], header='exp_num, x, y, keypress, missed, time', comments='')
        np.savetxt(output_path_data, self.data, delimiter=',', fmt=[
            '%.0f', '%.0f', '%.3f', '%.2f', '%.3f', '%.0f'], header='exp_num, try_num, time, distance, ID, miss', comments='')
        self.exp_timer_init()

    def calc_amplitude(self, x1, x2, y1, y2):
        return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))


    def set_target_config(self):
        self.num_of_targets = int(self.set_num_of_target.text())
        self.radius = self.inch_to_pixel(float(self.set_radius.text())/2)
        self.target_radius = self.inch_to_pixel(float(self.set_target_radius.text())/2)
        self.set_target()
        self.exp_timer_init()
        
        self.clicked = 0
        self.miss = 0
        self.miss_flag = False
        if self.exp_end_flag:
            self.exp_num += 1
            self.exp_end_flag = False
        self.update()


    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        self.textbox_x.setText(str(int(self.x)))  # 座標確認用
        self.textbox_y.setText(str(int(self.y)))  # 座標確認用
        painter.setPen(Qt.black)
        #painter.setBrush(Qt.red)
        #painter.drawEllipse(self.x, self.y, pointer_size, pointer_size)
        
        if self.exp_start_flag:
            painter.setBrush(QColor(0xee, 0xee, 0xee))
            for i in range(self.num_of_targets):
                painter.drawEllipse(
                    self.target_point[i], self.target_radius, self.target_radius)
            painter.setBrush(QColor(0x48, 0xcb, 0xeb))
            painter.drawEllipse(
                self.target_point[self.target_order[self.order_num]], self.target_radius, self.target_radius)
        else:
            painter.setBrush(QColor(0xff, 0xaa, 0x00))
            for i in range(self.num_of_targets):
                painter.drawEllipse(
                    self.target_point[i], self.target_radius, self.target_radius)
        #if self.collision_flag:
            #painter.setBrush(Qt.white)
            #painter.drawEllipse(
                #self.target_point[self.collision_nums], self.target_radius, self.target_radius)
        #self.textbox_t.setText(str(self.collision_flag))
        painter.setBrush(Qt.red)
        painter.drawEllipse(self.x, self.y, pointer_size, pointer_size)


    def keyPressEvent(self, keyevent):
        #print(keyevent.key())
        if keyevent.key() == Qt.Key_Return:  # Key:Shift
            self.clicked += 1

            if not self.collision_flag and not self.order_num == 0:
                self.miss_flag = True
                self.miss += 1
            self.exp_timer_clicked()
            if self.order_num == self.num_of_targets:
                self.exp_timer_stop()
                

            self.miss_flag = False
            self.order_num += 1
            self.order_num = self.order_num % (self.num_of_targets+1)
        if keyevent.key() == Qt.Key_Shift:
            QApplication.setOverrideCursor(self.cursor_hider)
            self.start = time.time()
            self.tstamp = time.time()
            self.exp_start_flag = True
            print("start")
            

    def value_upd(self):
        self.x, self.y = pyautogui.position()
        self.collision_flag = ((self.x - self.target_point[self.target_order[self.order_num]].x()) * (self.x - self.target_point[self.target_order[self.order_num]].x())) + (
            (self.y - self.target_point[self.target_order[self.order_num]].y()) * (self.y - self.target_point[self.target_order[self.order_num]].y())) <= (self.target_radius + pointer_size) * (self.target_radius + pointer_size)


        self.update()
        self.data_log()

    def main(self):
        self.show()
        sys.exit(app.exec_())

app = QApplication(sys.argv)
window = main_window()


if __name__ == '__main__':
    window.main()
