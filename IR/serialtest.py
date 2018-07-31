import serial
import numpy as np
from matplotlib import pyplot as plt

ser = serial.Serial()
ser.baudrate = 9600
ser.port = "/dev/cu.usbmodem1421"
ser.open()

t = np.zeros(100)
y = np.zeros(100)

plt.ion()
plt.figure()
li, = plt.plot(t, y)
plt.ylim(0, 5)
plt.xlabel("time[s]")
plt.ylabel("Voltage[V]")

ser.write("*".encode())
data = ser.readline().strip().rsplit()
tInt = float(data[0])
print("a")

while True:
    try:
        ser.write("*".encode())
        data = ser.readline().strip().rsplit()
        # 配列をキューと見たてて要素を追加・削除
        t = np.append(t, (float(data[0])-tInt)/10**6)
        t = np.delete(t, 0)
        y = np.append(y, float(data[1])*5/1023)
        y = np.delete(y, 0)

        li.set_xdata(t)
        li.set_ydata(y)
        plt.xlim(min(t), max(t))
        plt.draw()

    except KeyboardInterrupt:
        ser.close()
        break
