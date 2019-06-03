import numpy as np
import matplotlib.pyplot as plt
import sys
import math
import statistics 
from scipy.stats import norm
from sklearn.metrics import r2_score

path = str(sys.argv[1])

import_file = np.loadtxt(path, delimiter=',', skiprows=1)
w_raw = np.array([2.4, 1.8, 0.8, 2.4, 1.8, 2.4, 1.8, 0.8, 0.8])
d_raw = np.array([3.0, 3.0, 3.0, 15.0, 15.0, 26.0, 15.0, 26.0, 26.0])
#x = import_file[:, 0]
#y = import_file[:, 1]



import_file = import_file[np.argsort(import_file[:, 4])]
id_raw = import_file[:, 4]
id_unique = np.unique(id_raw)
time_raw = import_file[:, 3]

print(id_unique)

stdev_offsets = np.empty(0)
for i in id_unique:
        offsets = import_file[import_file[:, 4] == i][:, 6]
        offsets = offsets / (91.788*0.39370)
        stdev_offsets = np.append(stdev_offsets, statistics.stdev(offsets))

print("{}".format(stdev_offsets))
w_effective = stdev_offsets * 4.133
print("w_e: {}".format(w_effective))

id_effective = np.log2(d_raw / w_effective + 1)
print("id_e = log(D/W_e + 1): {}".format(id_effective))
err = import_file[import_file[:, 5] == 1][:, 5].size/import_file[:, 5].size






#print(import_file[:, 5])
true_time = np.empty(0)
id_effective_forfit = np.empty(0)
for i in id_raw:
    d = import_file[import_file[:,4] == i][:, 3]
    true_time = np.append(true_time, statistics.mean(d))
true_time = np.unique(true_time)

for i in range(9):
        for j in range(13*5):
                id_effective_forfit = np.append(id_effective_forfit, id_effective[i])

print(id_effective_forfit.shape)
print(time_raw.shape)



fitted1 = np.polyfit(id_effective_forfit, time_raw, 1)
b, a = fitted1
print("MT =  {} + {}  log(D/W + 1) ".format(a,b))
mt_predict = a+b*id_unique
tp = id_effective / mt_predict
print("TP = {}".format(statistics.mean(tp)))
print("Err = {}".format(err))
print("r2 = {}\n".format(r2_score(true_time, mt_predict)))

fitted2 = np.polyfit(id_raw, time_raw, 1)
b, a = fitted2
print("MT =  {} + {}  log(D/W + 1) ".format(a,b))
mt_predict = a+b*id_unique
tp = id_unique / mt_predict
print("TP = {}".format(statistics.mean(tp)))
print("Err = {}".format(err))
print("r2 = {}\n".format(r2_score(true_time, mt_predict)))


xp = np.linspace(0, 6, 6)
p = np.poly1d(fitted1)(xp)


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


