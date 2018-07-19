#データ取得関係
import serial
import pandas as pd
ser = serial.Serial('/dev/cu.usbmodem14131', 115200, timeout=None)
data = pd.DataFrame(index=[], columns=['Left_ACC_X', 'Left_ACC_Y', 'Left_ACC_Z',
                                       'Left_GYR_X', 'Left_GYR_Y', 'Left_GYR_Z',
                                       'Right_ACC_X', 'Right_ACC_Y', 'Right_ACC_Z',
                                       'Right_GYR_X', 'Right_GYR_Y', 'Right_GYR_Z',
                                       'move'])

while True:
        line = ser.readline()
        line = line.strip().decode('utf-8').split(",")
        line.append("right")
        #print(line)
        series = pd.Series(line, index=data.columns)
        data = data.append(series, ignore_index=True)
        print(series)
