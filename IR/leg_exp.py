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
import statistics

window_size_x = 1920        
window_size_y = 1080
#window_size_x, window_size_y = pyautogui.size()

num_of_sensor = 10
wait_flame = 100
alpha = 0.7
beta = 0.65
pointer_size = 8
#ppi = 128       #macbookpro 13.3 2018 1440*900
#ppi = 102.42   #研究室のDELLのディスプレイ
#ppi = 94.0     #家のディスプレイ(EV2455)
ppi = 91.788   #S2409Wb(24inch 1920*1080)

output_path_log = 'exp_data/leg/log_p0_left_leg.csv'
output_path_data = 'exp_data/leg/data_p0_left_leg.csv'

class sensor_read:
    def __init__(self):
        self.ser = serial.Serial('/dev/cu.usbmodem141201', 460800)
        for i in range(10):
            self.ser.readline()  # 読み飛ばし(欠けたデータが読み込まれるのを避ける)

    def read_test_ser(self):
        lst = float(0)
        while self.ser.in_waiting > 1 or lst == float(0):
            lst = self.ser.readline().strip().decode("utf-8").split(',')


        return lst


class main_window(QWidget):

    #膝位置計算用変数リセット
    def value_init(self):
        self.sensor_val = np.zeros(num_of_sensor, dtype=np.float)
        self.weight = ([1.00] * num_of_sensor)

    #キャリブレーションとそれ以外でEMAフィルタを分けるためリセット
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
        self.order_num = 0
        
        #配置する座標の計算、MacKenzieらのものを参考
        self.target_point = []
        for i in range(self.num_of_targets):
            cx = window_size_x / 2 + self.t_distance * math.cos(2 * math.pi * (float(i) / self.num_of_targets) - (math.pi/2))
            cy = window_size_y / 2 + self.t_distance * math.sin(2 * math.pi * (float(i) / self.num_of_targets) - (math.pi/2))
            self.target_point.append(QPoint(cx, cy))

    def cmetre_to_pixel(self, val):
        return val * (ppi*0.39370)
    def pixel_to_cmetre(self, val):
        return val / (ppi*0.39370)

    def __init__(self, parent=None):
        super().__init__(parent)
        #膝検出・位置計算用
        self.sensor_val = np.zeros(num_of_sensor, dtype=np.float)
        self.weight = ([1.00] * num_of_sensor)
        self.val = np.zeros((wait_flame, num_of_sensor), dtype=np.float)
        self.leg_flag = False
        self.sensor_flt = np.zeros((wait_flame,num_of_sensor),dtype=np.float)

        #指数平均平滑フィルタ(EMA)用
        self.old_ema = np.zeros(num_of_sensor, dtype=np.float)
        self.new_ema = np.zeros(num_of_sensor, dtype=np.float)
        self.new_x = 0
        self.old_x = window_size_x / 2
        self.new_y = 0
        self.old_y = window_size_y / 2

        #メディアンフィルタ用
        self.med_filter_d = np.zeros((num_of_sensor, 10), dtype=np.float)
        self.med_filter_x = np.zeros(10, dtype=np.float)
        self.med_filter_y = np.zeros(10, dtype=np.float)


        #低速モード用フラグ
        self.slower_mode = False

        #実験条件
        self.num_of_targets = 13  
        self.t_distance = self.cmetre_to_pixel(1.0)  # 全体の円の直径
        self.t_width = self.cmetre_to_pixel(0.5)  # ターゲット円の直径

        #ウィンドウサイズ
        self.resize(window_size_x, window_size_y)

        #ポインタ座標値
        self.x = 0
        self.y = 0
        self.xs= 0
        self.ys = 0


        #実験データ収集
        self.exp_timer_init()
        self.exp_start_flag = False
        self.exp_end_flag = False
        self.task_num = 0
        self.session_num = 0
        self.miss = 0
        self.miss_flag = False
        self.clicked = 0
        self.amplitude = 0
        self.logger = np.empty((0, 10), float)
        self.data = np.empty((0, 14), float)

        #衝突判定とターゲット位置計算
        self.collision_flag = False
        #self.collision_num = 0
        self.set_target()

        #実験条件[D,W] ランダムシャッフルで順番を決定しセッションごとに自動で呼び出し
        self.condition = [[3.0, 0.8], [3.0, 1.8], [3.0, 2.4], [15.0, 0.8], [15.0, 1.8], [15.0, 2.4], [26.0, 0.8], [26.0, 1.8], [26.0, 2.4]]
        random.shuffle(self.condition)

        
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
        
        #キャリブレーション:真中
        self.button_center_calb = QPushButton(self)
        self.button_center_calb.move(100, 100)
        self.button_center_calb.setText("キャリブレーション:真中")
        self.button_center_calb.clicked.connect(self.calibration_center)
        self.center_calb_flag = False
        self.center_posx = 0
        self.center_posy = 0

        #キャリブレーション:上
        self.button_up_calb = QPushButton(self)
        self.button_up_calb.move(0, 150)
        self.button_up_calb.setText("キャリブレーション:上")
        self.button_up_calb.clicked.connect(self.calibration_up)
        self.up_calb_flag = False
        self.upper_limit = window_size_y

        #キャリブレーション:下
        self.button_down_calb = QPushButton(self)
        self.button_down_calb.move(200, 150)
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

        #実験条件の変更
        #ターゲット数 = num_of_target の変更(初期値:13)
        self.num_of_targets_label = QLabel(self)
        self.num_of_targets_label.setText("ターゲット数")
        self.num_of_targets_label.move(200, 0)
        self.set_num_of_target = QLineEdit(self)
        self.set_num_of_target.move(200, 20)
        self.set_num_of_target.setText(str(self.num_of_targets))
        self.set_num_of_target.resize(100, 20)

        #全体の円の半径 = t_distance の変更(初期値:300)
        self.t_distance_label = QLabel(self)
        self.t_distance_label.setText("タスク番号")
        self.t_distance_label.move(350, 0)
        self.set_t_distance = QLineEdit(self)
        self.set_t_distance.move(350, 20)
        self.set_t_distance.setText(str(self.pixel_to_cmetre(self.t_distance)))
        self.set_t_distance.resize(100, 20)


        #実験条件の変更の反映
        self.button_exec = QPushButton(self)
        self.button_exec.move(700, 20)
        self.button_exec.setText("Next")
        self.button_exec.clicked.connect(self.set_target_config)

        self.cursor_hider = QCursor(QPixmap("bitmap.png"))

    #実験データ収集
    #操作時間計測
    def data_log(self):
        if self.exp_start_flag:
            _id = math.log2(1+self.condition[self.task_num][0]/self.condition[self.task_num][1])
            tm = time.time()-self.start
            self.logger = np.append(self.logger, np.array(
                [[self.session_num, self.task_num, self.order_num, self.miss, self.cmetre_to_pixel(self.condition[self.task_num][0]), self.cmetre_to_pixel(self.condition[self.task_num][1]), _id, tm, self.x, self.y]]), axis=0)
            self.miss_flag = False
    def exp_timer_init(self):
        self.start = 0
        self.tstamp = 0
        self.exp_start_flag = False
    def exp_timer_clicked(self):
        if self.order_num > 0:
            tm = time.time()-self.tstamp
            _id = math.log2(1+self.condition[self.task_num][0]/self.condition[self.task_num][1])
            #ofs = self.calc_amplitude(self.x, self.target_point[self.target_order[self.order_num]].x(), self.y, self.target_point[self.target_order[self.order_num]].y())
            #ofs = pixel_to_cmetre(ofs)
            x_end = self.x
            y_end = self.y
            self.data = np.append(self.data, np.array([[self.session_num, self.task_num, self.order_num, tm, self.cmetre_to_pixel(self.condition[self.task_num][0]), self.cmetre_to_pixel(self.condition[self.task_num][1]),_id, self.miss_flag, \
                self.xs, self.ys, self.x, self.y, self.target_point[self.target_order[self.order_num]].x(), self.target_point[self.target_order[self.order_num]].y()]]), axis=0)
        self.xs = self.x
        self.ys = self.y
        self.tstamp = time.time()
        
    def exp_timer_stop(self):
        self.exp_start_flag = False
        self.exp_end_flag = True
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        _id = math.log2(1+self.condition[self.task_num][0]/self.condition[self.task_num][1])
        tm = time.time()-self.start
        self.logger = np.append(self.logger, np.array(
                [[self.session_num, self.task_num, self.order_num, self.miss, self.cmetre_to_pixel(self.condition[self.task_num][0]), self.cmetre_to_pixel(self.condition[self.task_num][1]), _id, tm, self.x, self.y]]), axis=0)
        print('selection miss: ' + str(self.miss) + ' time(s)')
        np.savetxt(output_path_log, self.logger, delimiter=',', fmt=[
                   '%.0f', '%.0f', '%.0f', '%.0f', '%.1f', '%.1f', '%.3f', '%.3f', '%.3f', '%.3f'], header='session_num, task_num, try_num, miss, D, W, ID, time, x, y', comments='')
        np.savetxt(output_path_data, self.data, delimiter=',', fmt=[
                '%.0f', '%.0f', '%.0f', '%.3f', '%.1f', '%.1f', '%.3f', '%.0f', '%.3f', '%.3f', '%.3f', '%.3f', '%.0f', '%.0f'], header='session_num, task_num, try_num, time, D, W, ID, miss, x_start, y_start, x_end, y_end, x_target, y_target', comments='')
        self.exp_timer_init()

    def calc_amplitude(self, x1, x2, y1, y2):
        return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))


    def set_target_config(self):
        if self.exp_end_flag:
            self.task_num += 1
            self.exp_end_flag = False
            if self.task_num == 9:
                self.session_num += 1
                if self.session_num < 5:
                    random.shuffle(self.condition)  
                    self.task_num = 0
                else:
                    exit(1)
        print(str(self.session_num) + "-" + str(self.task_num))
        self.num_of_targets = int(self.set_num_of_target.text())
        self.t_distance = self.cmetre_to_pixel(self.condition[self.task_num][0]/2)
        self.t_width = self.cmetre_to_pixel(self.condition[self.task_num][1]/2)
        self.set_target()
        self.exp_timer_init()
        
        self.clicked = 0
        self.miss = 0
        self.miss_flag = False
 
        self.update()


    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        self.textbox_x.setText(str(int(self.x)))  
        self.textbox_y.setText(str(int(self.y)))  
        self.set_t_distance.setText(str(self.task_num))
        painter.setPen(Qt.black)
        
        if self.exp_start_flag:
            painter.setBrush(QColor(0xee, 0xee, 0xee)) #背景と同じ色
            for i in range(self.num_of_targets):
                painter.drawEllipse(
                    self.target_point[i], self.t_width, self.t_width)
            painter.setBrush(QColor(0x48, 0xcb, 0xeb)) #青
            painter.drawEllipse(
                self.target_point[self.target_order[self.order_num]], self.t_width, self.t_width)
        else:
            painter.setBrush(QColor(0xff, 0xaa, 0x00)) #オレンジ
            for i in range(self.num_of_targets):
                painter.drawEllipse(
                    self.target_point[i], self.t_width, self.t_width)
        painter.setBrush(Qt.red)
        painter.drawEllipse(QPoint(self.x, self.y), pointer_size, pointer_size)


    def keyPressEvent(self, keyevent):
        #print(keyevent.key())
        if keyevent.key() == Qt.Key_Return:  
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
        if keyevent.key() == Qt.Key_Control:
            if not self.exp_end_flag:
                QApplication.setOverrideCursor(self.cursor_hider)
                self.start = time.time()
                self.tstamp = time.time()
                self.exp_start_flag = True
                print("start")

        if keyevent.key() == Qt.Key_Shift:
            self.set_target_config()
    
    def my_map(self, val, in_min, in_max, out_min, out_max):
        return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def pointer_calc(self, sensor_val):
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
        
        n_sensor_val = np.zeros(num_of_sensor, dtype=np.float)
        #上のフィルタはセンサ値に対して行っているが、こちらのフィルタは、EMAを通過したセンサ値を記録している
        for i in range(wait_flame-1):
            self.sensor_flt[i+1, :] = self.sensor_flt[i, :]
        max_val = np.max(sensor_val)
        near_snum = []

        if self.leg_flag:
            #y座標計算
            # top_sensor = np.argsort(-sensor_val)
            self.new_y = max(sensor_val)
        
            #x座標計算
            # for i in range(num_of_sensor):
            #     if i > 6:
            #         sensor_val[top_sensor[i]] = 0
            for i in range(num_of_sensor):
                self.weight[i] = 1 / (max(sensor_val) - sensor_val[i] + 2)
            s = sum(self.weight)
            self.new_x = 0
            for j in range(num_of_sensor):
                self.new_x += ((j * self.weight[j] / s))
            #print(self.new_x)

            #座標平滑フィルタ
            #xとyで分けてるだけ

            self.new_x = (self.new_x - self.old_x) * alpha + self.old_x
            self.old_x = self.new_x

            self.new_y = (self.new_y - self.old_y) * beta + self.old_y
            self.old_y = self.new_y


        print("x: {}, y: {}".format(self.new_x, self.new_y))    
        return self.new_x, self.new_y
    
    #左方向キャリブレーション
    #早くも遅くもないフレーム数が100Fくらい？調整の結果
    def calibration_left(self):
        x = 0
        y = 0
        if not self.left_calb_flag:
            for i in range(60):
                tmp = rd.read_test_ser()
                val = [64-float(v) for v in tmp]
                x, y = self.pointer_calc(val)
            self.left_limit = x
            #print(lst)
            self.left_calb_flag = True
            self.ema_reset()

    #右方向キャリブレーション
    def calibration_right(self):
        x = 0
        y = 0
        if not self.right_calb_flag:
            for i in range(60):
                tmp = rd.read_test_ser()
                val = [64-float(v) for v in tmp]
                x, y = self.pointer_calc(val)
            self.right_limit = x
            #print(lst)
            self.right_calb_flag = True
            self.ema_reset()
    #真中キャリブレーション

    def calibration_center(self):
        x = 0
        y = 0
        if not self.center_calb_flag:
            for i in range(60):
                tmp = rd.read_test_ser()
                val = [64-float(v) for v in tmp]
                x, y = self.pointer_calc(val)
            self.center_posx = x
            self.center_posy = y
            #print(lst)
            self.center_calb_flag = True
            self.ema_reset()

    #上方向キャリブレーション
    def calibration_up(self):
        x = 0
        y = 0
        if not self.up_calb_flag:
            for i in range(60):
                tmp = rd.read_test_ser()
                val = [64-float(v) for v in tmp]
                x, y = self.pointer_calc(val)
            self.upper_limit = y
            #print(lst)
            self.up_calb_flag = True
            self.ema_reset()

    #下方向キャリブレーション
    def calibration_down(self):
        x = 0
        y = 0
        if not self.down_calb_flag:
            for i in range(60):
                tmp = rd.read_test_ser()
                val = [64-float(v) for v in tmp]
                x, y = self.pointer_calc(val)
            self.lower_limit = y
            #print(lst)
            self.down_calb_flag = True
            self.ema_reset()

    def calibration_check(self):
        return self.left_calb_flag and self.right_calb_flag and self.up_calb_flag and self.down_calb_flag and self.center_calb_flag

    def calibration_reset(self):
        self.left_calb_flag = False
        self.right_calb_flag = False
        self.up_calb_flag = False
        self.down_calb_flag = False
        self.center_calb_flag = False


    def value_upd(self):
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

        if self.calibration_check():
            self.new_x, self.new_y = self.pointer_calc(sensor_val)
            if self.new_x < self.center_posx:
                self.x = self.my_map(
                    self.new_x, self.left_limit, self.center_posx, 0, window_size_x/2)
            else:
                self.x = self.my_map(
                    self.new_x, self.center_posx, self.right_limit, window_size_x/2, window_size_x)

            if self.new_y < self.center_posy:
                self.y = self.my_map(
                    self.new_y, self.upper_limit, self.center_posy, 0, window_size_y/2)
            else:
                self.y = self.my_map(
                    self.new_y, self.center_posy, self.lower_limit, window_size_y/2, window_size_y)

            if self.x < 0:
                self.x = 0
            elif self.x > window_size_x:
                self.x = window_size_x
            if self.y < 0:
                self.y = 0
            elif self.y > window_size_y:
                self.y = window_size_y
            #pyautogui.moveTo(self.x, self.y)
        #衝突判定
            self.collision_flag = ((self.x - self.target_point[self.target_order[self.order_num]].x()) * (self.x - self.target_point[self.target_order[self.order_num]].x())) + (
                (self.y - self.target_point[self.target_order[self.order_num]].y()) * (self.y - self.target_point[self.target_order[self.order_num]].y())) <= (self.t_width + pointer_size) * (self.t_width + pointer_size)
            self.update()
            self.data_log()

    def main(self):
        self.show()
        app.exec_()

rd = sensor_read()
app = QApplication(sys.argv)
window = main_window()


if __name__ == '__main__':
    window.main()
