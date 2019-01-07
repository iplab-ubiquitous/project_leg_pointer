import numpy as np
import matplotlib.pyplot as plt
import sys
import math
import statistics
from sklearn.metrics import r2_score
from scipy.stats import norm

path = str(sys.argv[1])

import_file = np.loadtxt(path, delimiter=',', skiprows=1)

#x = import_file[:, 0]
#y = import_file[:, 1]


#d_id = import_file[import_file[:, 2] == 1][:, 6]
import_file = import_file[np.argsort(import_file[:, 4])]

delta_t = import_file[:, 2]
d_id = import_file[:, 4]
err = sum(import_file[:, 5]) / len(import_file[:,5])
we = np.array([0.5, 1.0, 1.5]) * 2.066 / norm.ppf(1-err/2)
dis = np.array([2.0, 5.0, 8.0])
print("W(e) = " + str(we))
d_id_e = np.empty(0)
for i in range(dis.shape[0]):
    for j in range(we.shape[0]):
        d_id_e = np.append(d_id_e, math.log2(1 + (dis[j]/we[i])))

d_id_e = np.sort(d_id_e)
print("ID(e) = " + str(d_id_e))



d_id_e_pred = np.empty(0)
for i in range(d_id_e.shape[0]):
    for j in range(13*1):
        d_id_e_pred = np.append(d_id_e_pred, d_id_e[i])



#print(import_file[:, 5])
true_time = np.empty(0)
id_series = np.empty(0)
for i in d_id:
    d = import_file[import_file[:,4] == i][:,2]
    true_time = np.append(true_time, statistics.mean(d))
    d = import_file[import_file[:, 4] == i][:, 4]
    id_series = np.append(id_series, statistics.mean(d))
true_time = np.unique(true_time)
id_series = np.unique(id_series)
print(id_series)


fitted = np.polyfit(d_id_e_pred, delta_t, 1)
b, a = fitted
print("MT = " + str(a) + " + " + str(b) + " log(D/W + 1) ")
tp = d_id_e / (a+b*d_id_e)
print("TP = " + str(statistics.mean(tp)))
print("Err = " + str(err))
pred_time = a+b*d_id_e
print(true_time)
print(pred_time)
print("r2 = " + str(r2_score(true_time, pred_time)))


'''
p = np.poly1d(fitted)
p30 = np.poly1d(np.polyfit(d_id, delta_t, 30))
xp = np.linspace(0, 10, 100)


plt.plot(d_id, delta_t, '.')
#plt.xlim(0, 1920)
plt.ylim(1,5)
plt.show()
plt.savefig('image.png')
'''

