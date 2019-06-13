import numpy as np
import matplotlib.pyplot as plt
import sys
import math
import statistics 
from scipy.stats import norm
from sklearn.metrics import r2_score

#ppi = 128       #macbookpro 13.3 2018 1440*900
#ppi = 102.42   #研究室のDELLのディスプレイ
#ppi = 94.0     #家のディスプレイ(EV2455)
ppi = 91.788   #S2409Wb(24inch 1920*1080)


def calc_amplitude(x1, x2, y1, y2):
        return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))

path = str(sys.argv[1])

import_file = np.loadtxt(path, delimiter=',', skiprows=1)
w_raw = np.array([86.7, 65.0, 28.9, 86.7,  65.0,  86.7,  65.0,  28.9,  28.9])
d_raw = np.array([108.4, 108.4, 108.4, 542.1, 542.1, 939.6, 939.6, 542.1, 939.6])
#x = import_file[:, 0]
#y = import_file[:, 1]


import_file = import_file[np.argsort(import_file[:, 6])]
id_raw = import_file[:, 6]
id_unique = np.unique(id_raw)
time_raw = import_file[:, 3]



print(id_unique)

d_effective = np.empty(0)
stdev_offsets_w = np.empty(0)
for i in id_unique:
        mean_distance_d = np.empty(0)
        offsets_w = np.empty(0)
        x_start = import_file[import_file[:, 6] == i][:, 8]
        y_start = import_file[import_file[:, 6] == i][:, 9]
        x_end = import_file[import_file[:, 6] == i][:, 10]
        y_end = import_file[import_file[:, 6] == i][:, 11]
        x_target = import_file[import_file[:, 6] == i][:, 12]
        y_target = import_file[import_file[:, 6] == i][:, 13]
        for j in range(x_end.size):
                u = calc_amplitude(x_start[j], x_end[j], y_start[j], y_end[j])
                v = calc_amplitude(x_end[j], x_target[j], y_end[j], y_target[j])
                mean_distance_d = np.append(mean_distance_d, u)
                offsets_w = np.append(offsets_w, v)
        d_effective = np.append(d_effective, statistics.mean(mean_distance_d))
        stdev_offsets_w = np.append(stdev_offsets_w, statistics.stdev(offsets_w))
        

print("D_e: {}".format(d_effective))
#print("{}".format(stdev_offsets_w))
w_effective = stdev_offsets_w * 4.133
print("w_e: {}".format(w_effective))

print("id: {}".format(id_unique))
id_effective1 = np.log2(d_raw / w_effective + 1)
print("id_e = log(D/W_e + 1): {}".format(id_effective1))
id_effective2 = np.log2(d_effective / w_effective + 1)
print("id_e = log(D_e/W_e + 1): {}".format(id_effective2))


err = import_file[import_file[:, 7] == 1][:, 7].size/import_file[:, 7].size

#print(import_file[:, 5])
true_time = np.empty(0)
id_effective_forfit1 = np.empty(0)
id_effective_forfit2 = np.empty(0)
for i in id_raw:
    d = import_file[import_file[:,6] == i][:, 3]
    true_time = np.append(true_time, statistics.mean(d))
true_time = np.unique(true_time)

for i in range(9):
        for j in range(13*5):
                id_effective_forfit1 = np.append(id_effective_forfit1, id_effective1[i])
                id_effective_forfit2 = np.append(id_effective_forfit2, id_effective2[i])



fitted1 = np.polyfit(id_effective_forfit1, time_raw, 1)
b, a = fitted1
print("MT =  {} + {}  log(D/W + 1) ".format(a,b))
mt_predict = a+b*id_unique
tp = id_effective1 / mt_predict
print("TP = {}".format(statistics.mean(tp)))
print("Err = {}".format(err))
print("r2 = {}\n".format(r2_score(true_time, mt_predict)))

fitted2 = np.polyfit(id_effective_forfit2, time_raw, 1)
b, a = fitted2
print("MT =  {} + {}  log(D/W + 1) ".format(a,b))
mt_predict = a+b*id_unique
tp = id_effective2 / mt_predict
print("TP = {}".format(statistics.mean(tp)))
print("Err = {}".format(err))
print("r2 = {}\n".format(r2_score(true_time, mt_predict)))

fitted3 = np.polyfit(id_raw, time_raw, 1)
b, a = fitted3
print("MT =  {} + {}  log(D/W + 1) ".format(a,b))
mt_predict = a+b*id_unique
tp = id_unique / mt_predict
print("TP = {}".format(statistics.mean(tp)))
print("Err = {}".format(err))
print("r2 = {}\n".format(r2_score(true_time, mt_predict)))


'''
xp = np.linspace(0, 6, 6)
p = np.poly1d(fitted2)(xp)


plt.figure(figsize=(10, 5))
plt.title("Left Leg")
plt.xlabel("ID = log(D/W + 1) [bit/s]")
plt.ylabel("Moving Time [s]")
plt.scatter(id_raw, time_raw, s=5, c='red', label='selection time')
plt.plot(xp, p, label="predict time")
plt.legend(bbox_to_anchor=(1, 1), loc='lower right',
           borderaxespad=0, fontsize=10)
#plt.xlim(0, 1920)
plt.ylim(0,4.5)
plt.xlim(1.0,5.5)
plt.show()
plt.savefig('image.png')
'''


