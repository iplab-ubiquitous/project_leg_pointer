import numpy as np
import matplotlib.pyplot as plt
import sys
import math
import statistics
from sklearn.metrics import r2_score
from scipy.stats import norm


import_file = np.loadtxt("./exp_data/leg/data_right_0109.csv", delimiter=',', skiprows=1)
file_P1 = np.loadtxt("./exp_data/leg/data_P1/P1_right.csv",delimiter=',', skiprows=1)
file_P2 = np.loadtxt("./exp_data/leg/data_P2/P2_right.csv",delimiter=',', skiprows=1)
file_P3 = np.loadtxt("./exp_data/leg/data_P3/P3_right.csv",delimiter=',', skiprows=1)


#x = import_file[:, 0]
#y = import_file[:, 1]

import_file = import_file[np.argsort(import_file[:, 4])]
imp1_x = file_P1[np.argsort(file_P1[:, 4])][:, 4]
imp1_y = file_P1[np.argsort(file_P1[:, 4])][:, 2]
imp2_x = file_P2[np.argsort(file_P2[:, 4])][:, 4]
imp2_y = file_P2[np.argsort(file_P2[:, 4])][:, 2]
imp3_x = file_P3[np.argsort(file_P3[:, 4])][:, 4]
imp3_y = file_P3[np.argsort(file_P3[:, 4])][:, 2]


def model_prediction(data, num):
        data = data[np.argsort(data[:, 4])]
        delta_t = data[:, 2]
        d_id = data[:, 4]

        err = sum(data[:, 5]) / len(data[:, 5])
        '''
        we = np.array([0.5, 1.0, 1.5])
        if err > 0.000049:
                we = we * 2.066 / norm.ppf(1-err/2)
        else:
                we = we * 0.5089
        dis = np.array([2.0, 5.0, 8.0])
        print("W(e) = " + str(we))
        d_id_e = np.empty(0)
        for i in range(dis.shape[0]):
                for j in range(we.shape[0]):
                        d_id_e = np.append(
                            d_id_e, math.log2(1 + (dis[j]/we[i])))

        d_id_e = np.sort(d_id_e)
        print("ID(e) = " + str(d_id_e))

        d_id_e_pred = np.empty(0)
        for i in range(d_id_e.shape[0]):
                for j in range(num):
                        d_id_e_pred = np.append(d_id_e_pred, d_id_e[i])
        '''

        #print(data[:, 5])
        true_time = np.empty(0)
        id_series = np.empty(0)
        for i in d_id:
                d = data[data[:, 4] == i][:, 2]
                true_time = np.append(true_time, statistics.mean(d))
                d = data[data[:, 4] == i][:, 4]
                id_series = np.append(id_series, statistics.mean(d))
        true_time = np.unique(true_time)
        id_series = np.unique(id_series)
        print(id_series)

        fitted = np.polyfit(d_id, delta_t, 1)
        b, a = fitted
        print("MT = " + str(a) + " + " + str(b) + " log(D/W + 1) ")
        #tp = d_id_e / (a+b*d_id_e)
        tp = d_id / (a+b*d_id)
        print("TP = " + str(statistics.mean(tp)))
        print("Err = " + str(err))
        #pred_time = a+b*d_id_e
        pred_time = a+b*id_series
        print(true_time)
        print(pred_time)
        r_2 = np.round(r2_score(true_time, pred_time), decimals=3)
        print("r2 = " + str(r_2))
        print("")

        return fitted, r_2


xp = np.linspace(0, 5, 5)
fitted_left, r_2 = model_prediction(import_file, 13*3*3)
fitted_P1, r_2 = model_prediction(file_P1, 13*3)
P1_label = "predict time (P1): " + \
    str(round(fitted_P1[1], 3)) + "+" + \
    str(round(fitted_P1[0], 3)) + "*" + "ID (r2=" + str(r_2) + ")"
fitted_P2, r_2 = model_prediction(file_P2, 13*3)
P2_label = "predict time (P2): " + \
    str(round(fitted_P2[1], 3)) + "+" + \
    str(round(fitted_P2[0], 3)) + "*" + "ID (r2=" + str(r_2) + ")"
fitted_P3, r_2 = model_prediction(file_P3, 13*3)
P3_label = "predict time (P3): " + \
    str(round(fitted_P3[1], 3)) + "+" + \
    str(round(fitted_P3[0], 3)) + "*" + "ID (r2=" + str(r_2) + ")"
p_left = np.poly1d(fitted_left)(xp)
p1 = np.poly1d(fitted_P1)(xp)
p2 = np.poly1d(fitted_P2)(xp)
p3 = np.poly1d(fitted_P3)(xp)


plt.figure(figsize=(7,5))
plt.title("Right Leg",fontsize=14)
plt.xlabel("ID = log(D/W + 1) [bit]", fontsize=16)
plt.ylabel("Moving Time [s]", fontsize=16)


plt.scatter(imp1_x, imp1_y, s=30, marker="o",
            label='selection time (P1)', c="#e67e22", alpha=0.7)
plt.scatter(imp2_x, imp2_y, s=30, marker="x",
            label='selection time (P2)', c="#27ae60", alpha=0.7)
plt.scatter(imp3_x, imp3_y, s=30, marker="+",
            label='selection time (P3)', c="#2980b9", alpha=0.7)

plt.plot(xp, p1, label=P1_label, linestyle="solid", c="#e67e22")
plt.plot(xp, p2, label=P2_label, linestyle="dashed", c="#27ae60")
plt.plot(xp, p3, label=P3_label, linestyle="dashdot", c="#2980b9")
plt.legend(bbox_to_anchor=(0, 1), loc='upper left',
           borderaxespad=1, fontsize=12)
#plt.plot(xp, p_left, label="predict time (Left)", c='black')

#plt.xlim(0, 1920)
plt.ylim(0.1, 8.1)
plt.xlim(1.0, 4.5)
#plt.show()
plt.savefig('right.pdf', format="pdf")
