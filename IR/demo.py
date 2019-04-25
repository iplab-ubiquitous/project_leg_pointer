#PyQt
import sys
import math
#PySerial
import serial
import pyautogui
import numpy as np
import random
import time

from pynput.keyboard import Key, Listener

window_size_x = 1440
window_size_y = 900
window_size_x, window_size_y = pyautogui.size()
#window_size = QtGui.qApp.desktop().width()
num_of_sensor = 10
wait_flame = 100
alpha = 0.1
beta = 0.65
pointer_size = 20
ppi = 102.42  # 研究室のDELLのディスプレイ
#ppi = 94.0   #家のディスプレイ(EV2455)
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.001

output_path_log = 'exp_data/leg/log_p1_leg.csv'
output_path_data = 'exp_data/leg/data_p1_leg.csv'


class sensor_read:
    def __init__(self):
        self.ser = serial.Serial('/dev/cu.usbmodem143201', 460800)
        for i in range(10):
            self.ser.readline()  # 読み飛ばし(欠けたデータが読み込まれるのを避ける)

    def read_test_ser(self):
        lst = float(0)
        while self.ser.in_waiting > 1 or lst == float(0):
            lst = self.ser.readline().strip().decode("utf-8").split(',')

        #line_f = [float(s) for s in self.line]
        #return line_f

        return lst


class move_mouse:

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
        #super().__init__(parent)
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


        #ポインタ座標値
        self.x = 0
        self.y = 0
        self.left_limit = 3.50
        self.right_limit = 6.98
        self.center_posx = 4.99
        self.center_posy = 52.5
        self.upper_limit = 57.0
        self.lower_limit = 49.4

        self.mousemode = False

    def my_on_press(key):
        print('hi tohu!')

    def my_on_release(key):
        print('hi tohu!')

    def keyPressEvent(self, keyevent):
        if keyevent.key() == Qt.Key_Shift:
            if self.mousemode:
                self.mousemode = False
            else:
                self.mousemode = True
        if keyevent.key() == Qt.Key_Control:
            if self.mousemode:
                pyautogui.click(self.x, self.y, 1, 1, 'left')
    
    #膝位置計算

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
        #指数平均平滑フィルタ
        n_sensor_val = np.zeros(num_of_sensor, dtype=np.float)
        for i in range(wait_flame-1):
            self.sensor_flt[i+1, :] = self.sensor_flt[i, :]
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

        if self.leg_flag:
            #y座標計算
            top_sensor = np.argsort(-sensor_val)
            self.new_y = max(sensor_val)

            #x座標計算
            for i in range(num_of_sensor):
                if i > 6:
                    sensor_val[top_sensor[i]] = 0
            for i in range(num_of_sensor):
                self.weight[i] = 1 / (max(sensor_val) - sensor_val[i] + 2)
            s = sum(self.weight)
            self.new_x = 0
            for j in range(num_of_sensor):
                self.new_x += ((j * self.weight[j] / s))
            #print(self.new_x)

            #座標平滑フィルタ
            if self.old_x == window_size_x / 2:
                self.old_x = self.new_x
            else:
                self.new_x = (self.new_x - self.old_x) * alpha + self.old_x
                self.old_x = self.new_x

            if self.old_y == window_size_y / 2:
                self.old_y = self.new_y
            else:
                self.new_y = (self.new_y - self.old_y) * beta + self.old_y
                self.old_y = self.new_y

        return self.new_x, self.new_y

    def calibration_check(self):
        return True


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

        if self.calibration_check():
            '''
            if self.slower_mode:
                x, y = self.pointer_calc(
                    sensor_val, self.left_limit, self.right_limit, self.upper_limit, self.lower_limit, self.leg_flag)
                self.x = self.xs + int(((x - self.xs) / window_size_x) * 100)
                self.y = self.ys + int(((y - self.ys) / window_size_y) * 100)


            else:
            '''
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
                
                pyautogui.moveTo(self.x, self.y)
    def main(self):
        while True:
            self.value_upd()


rd = sensor_read()
window = move_mouse()

if __name__ == '__main__':
    window.main()
