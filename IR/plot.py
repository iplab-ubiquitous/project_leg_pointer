import numpy as np
import matplotlib.pyplot as plt
import sys
import math
import statistics
from sklearn.metrics import r2_score

path = str(sys.argv[1])

import_file = np.loadtxt(path, delimiter=',', skiprows=1)

#x = import_file[:, 0]
#y = import_file[:, 1]


delta_t = import_file[:, 2]
#d_id = import_file[import_file[:, 2] == 1][:, 6]
d_id = import_file[:, 4]
true_time = np.empty(0)
id_series = np.empty(0)
for i in range(9):
    d = import_file[import_file[:,0] == i][:,2]
    true_time = np.append(true_time, statistics.mean(d))
    d = import_file[import_file[:, 0] == i][:, 4]
    id_series = np.append(id_series, statistics.mean(d))
print(true_time)
print(id_series)


fitted = np.polyfit(d_id, delta_t, 1)
b, a = fitted
print("MT = " + str(a) + " + " + str(b) + " log(D/W + 1) ")
tp = d_id / (a+b*d_id)
print("TP = " + str(statistics.mean(tp)))
p = np.poly1d(fitted)
p30 = np.poly1d(np.polyfit(d_id, delta_t, 30))
xp = np.linspace(0, 10, 100)
print(true_time)
print(id_series)
pred_time = a+b*id_series
print(pred_time)
print(r2_score(true_time, pred_time))



plt.plot(d_id, delta_t, '.')
#plt.xlim(0, 1920)
plt.ylim(1,5)
plt.show()
plt.savefig('image.png')

