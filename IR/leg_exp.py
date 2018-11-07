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
alpha = 0.1
pointer_size = 20
output_path = 'exp_data/leg/data_p0_leg.csv'


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

    #ターゲット円配置
    def set_target(self):
        #選択すべきターゲット順を定義
        #マルチポインティングタスクに倣った順
        self.target_order = [0]
        n = 0
        for i in range(self.num_of_targets):
            n += int(self.num_of_targets/2)
            self.target_order.append(n % self.num_of_targets)
        #print(self.target_order) 
        self.order_num = 0

        #単純なランダム順
        #self.target_order = list(range(self.num_of_targets))
        #random.shuffle(self.target_order)
        
        #配置する座標の計算
        self.target_point = []
        for i in range(self.num_of_targets):
            cx = window_size_x / 2 + self.radius*math.cos(2 * math.pi * (float(i) / self.num_of_targets))
            cy = window_size_y / 2 + self.radius*math.sin(2 * math.pi * (float(i) / self.num_of_targets))
            self.target_point.append(QPoint(cx, cy))

    def __init__(self, parent=None):
        super().__init__(parent)
        #膝検出・位置計算用
        self.sensor_val = np.zeros(num_of_sensor, dtype=np.float)
        self.weight = ([1.00] * num_of_sensor)
        self.val = np.zeros((wait_flame, num_of_sensor), dtype=np.float)
        self.leg_flag = False

        #指数平均平滑フィルタ(EMA)用
        self.old_ema = np.zeros(num_of_sensor, dtype=np.float)
        self.new_ema = np.zeros(num_of_sensor, dtype=np.float)
        self.new_x = 0
        self.old_x = window_size_x / 2
        self.new_y = 0
        self.old_y = window_size_y / 2

        #実験条件
        self.num_of_targets = 13    #ターゲット数
        self.radius = 300           #全体の円の半径
        self.target_radius = 40     #ターゲット円の半径=Width

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

        
        #nカウントごとにタイムアウト、タイムアウト時に任意の関数を呼び出す
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.value_upd)
        self.timer.start(5)  #200fps以下

        
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

        self.textbox_t = QLineEdit(self)
        self.textbox_t.move(window_size_x/2, window_size_y/2)
        self.textbox_t.resize(70, 20)

        #実験条件の変更
        #ターゲット数 = num_of_target の変更(初期値:13)
        self.num_of_targets_label = QLabel(self)
        self.num_of_targets_label.setText("ターゲット数")
        self.num_of_targets_label.move(200, 0)
        self.set_num_of_target = QLineEdit(self)
        self.set_num_of_target.move(200, 20)
        self.set_num_of_target.setText(str(self.num_of_targets))
        self.set_num_of_target.resize(100, 20)

        #全体の円の半径 = radius の変更(初期値:300)
        self.radius_label = QLabel(self)
        self.radius_label.setText("ターゲット距離")
        self.radius_label.move(350, 0)
        self.set_radius = QLineEdit(self)
        self.set_radius.move(350, 20)
        self.set_radius.setText(str(self.radius))
        self.set_radius.resize(100, 20)

        #ターゲット数 = target_radius の変更(初期値:40)
        self.target_radius_label = QLabel(self)
        self.target_radius_label.setText("ターゲット半径")
        self.target_radius_label.move(500, 0)
        self.set_target_radius = QLineEdit(self)
        self.set_target_radius.move(500, 20)
        self.set_target_radius.setText(str(self.target_radius))
        self.set_target_radius.resize(100, 20)

        #実験条件の変更の反映
        self.button_exec = QPushButton(self)
        self.button_exec.move(700, 20)
        self.button_exec.setText("設定")
        self.button_exec.clicked.connect(self.set_target_config)

    #実験データ収集用
    #操作時間計測
    def exp_timer_init(self):
        self.start = 0          #計測開始時刻
        self.selected = 0       #選択時の時刻
    def exp_timer_start(self):
        self.start = time.time()
    def exp_timer_select(self):
        self.selected = time.time()-self.start 
        self.amplitude = self.calc_amplitude(self.order_num, self.order_num-1) #前のターゲットと次のターゲットとの距離
        print('direction:' + str(self.target_order[self.order_num-1]) + '->' + str(
                    self.target_order[self.order_num]))
        print('time: ' + str(self.selected))
        print('amplitude: ' + str(self.amplitude))
        self.result = np.append(self.result, np.array([[self.radius, self.target_radius, self.selected, self.amplitude, 1+self.amplitude/self.target_radius]]), axis=0)
        #全体半径・ターゲット円半径・時間・距離・ID値の順に出力

        self.start = time.time()
    def exp_timer_stop(self):
        print('selection miss: ' + str(self.miss) + ' time(s)')
        print(self.result)
        np.savetxt(output_path, self.result, delimiter=',', fmt=[
                   '%.0f', '%.0f', '%.5f', '%.5f', '%.5f'], header='radius, width, time, distance, ID', comments='')
        self.exp_timer_init()
    #操作時間計測

    #ターゲット同士のユークリッド距離計算
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
        if self.leg_flag: 
            painter.setBrush(Qt.red)
        else:
            painter.setBrush(Qt.white)
        painter.drawEllipse(self.x, self.y, pointer_size, pointer_size)

        if not self.exp_end_flag:
            painter.setBrush(QColor(0x48, 0xcb, 0xeb))
            for i in range(self.num_of_targets):
                painter.drawEllipse(
                    self.target_point[i], self.target_radius, self.target_radius)
            painter.setBrush(QColor(0x00, 0x00, 0xff))
            painter.drawEllipse(
                self.target_point[self.target_order[self.order_num]], self.target_radius, self.target_radius)
        else:
            painter.setBrush(QColor(0xff, 0xff, 0xff))
            for i in range(self.num_of_targets):
                painter.drawEllipse(
                    self.target_point[i], self.target_radius, self.target_radius)
        if self.collision_flag:
            painter.setBrush(Qt.white)
            painter.drawEllipse(
                self.target_point[self.collision_num], self.target_radius, self.target_radius)
            self.textbox_t.setText(str(self.collision_num))

    def keyPressEvent(self, keyevent):
        #print(keyevent.key())
        if keyevent.key() == Qt.Key_Shift and self.collision_flag:  # Key:Shift
            if self.order_num == 0:
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
            
                
    #膝位置計算
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

        if self.leg_flag:
            #y座標計算
            self.new_y = (window_size_y) * (min(sensor_val)-5.0) / 12.0-5.0

            #x座標計算
            for i in range(num_of_sensor):
                self.weight[i] = 1 / (sensor_val[i] - min(sensor_val) + 2)
            s = sum(self.weight)
            self.new_x = -2
            for j in range(num_of_sensor):
                self.new_x += ((j * self.weight[j] / s) * 1.5)
            self.new_x *= (window_size_x / 9)

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

            x = (window_size_x) * (self.new_x - left_limit) / \
                (right_limit-left_limit)
            y = (window_size_y) * (self.new_y - upper_limit) / \
                (lower_limit-upper_limit)
        return x, y

    #左方向キャリブレーション
    def calibration_left(self):
        x = 0
        y = 0
        if not self.left_calb_flag:
            for i in range(30):
                tmp = rd.read_test_ser()
                val = [float(v) for v in tmp]
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
            for i in range(30):
                tmp = rd.read_test_ser()
                val = [float(v) for v in tmp]
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
                val = [float(v) for v in tmp]
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
                val = [float(v) for v in tmp]
                x, y = self.pointer_calc(
                    val, 0, window_size_x, 0, window_size_y, True)
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
        #print(self.left_limit, self.right_limit,self.upper_limit, self.lower_limit)
        self.value_init()
        self.new_x = 0
        not_update = True
        tmp = rd.read_test_ser()
        sensor_val = [float(v) for v in tmp]
        #膝検出
        self.leg_flag = False
        pick = 0
        for i in range(num_of_sensor):
            pick += sensor_val[i] < 50
            if(pick > 3):
                self.leg_flag = True
                break
        #膝検出
        if self.calibration_check():
            self.x, self.y = self.pointer_calc(
                sensor_val, self.left_limit, self.right_limit, self.upper_limit, self.lower_limit, self.flag)

            #衝突判定
        for i in range(self.num_of_targets):
                self.collision_flag = ((self.x - self.target_point[i].x()) * (self.x - self.target_point[i].x())) + (
                    (self.y - self.target_point[i].y()) * (self.y - self.target_point[i].y())) <= (self.target_radius + pointer_size) * (self.target_radius + pointer_size)
                if self.collision_flag:
                    self.collision_num = i
                    break
        self.update()

    def main(self):
        self.show()
        app.exec_()

rd = sensor_read()
app = QApplication(sys.argv)
window = main_window()


if __name__ == '__main__':
    window.main()
