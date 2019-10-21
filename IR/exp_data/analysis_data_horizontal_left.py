import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import sys
import math
import statistics 
from scipy.stats import norm
from sklearn.metrics import r2_score

#ppi = 128       #macbookpro 13.3 2018 1440*900
#ppi = 102.42   #研究室のDELLのディスプレイ
#ppi = 94.0     #家のディスプレイ(EV2455)
ppi = 91.788   #S2409Wb(24inch 1920*1080)

num_of_targets = 3 #分析対象とする選択回数の指定
persons = 1 #1回の分析データは何人ぶんのデータか

f = plt.figure(figsize=(8, 6))
ax = f.add_subplot(111)
ax.yaxis.tick_left()
ax.yaxis.set_label_position("left")
plt.title("左膝の選択時間（水平操作のみ抽出）", fontsize=16)
plt.xlabel("ID_e = log(D_e/W_e + 1) [bit/s]", fontsize=16)
plt.ylabel("選択時間 [s]", fontsize=16)
xp = np.linspace(0, 6, 6)
cmap = plt.get_cmap("tab10")
throughput = np.zeros(4)
error = np.zeros(4)
error_s = np.zeros(5)


def calc_amplitude(x1, x2, y1, y2):
        return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))




def fitts_fit(name, path, cmap_num, shape):
        import_file = np.loadtxt(path, delimiter=',', skiprows=1)
        w_raw = np.array([86.7, 65.0, 28.9, 86.7,  65.0,  86.7,  65.0,  28.9,  28.9])
        d_raw = np.array([108.4, 108.4, 108.4, 542.1, 542.1, 939.6, 939.6, 542.1, 939.6])
        #x = import_file[:, 0]
        #y = import_file[:, 1]


        import_file = import_file[np.argsort(import_file[:, 6])]
        id_raw = import_file[:, 6]
        id_unique = np.unique(id_raw)
        time_raw = import_file[:, 3]
        for i in range(5):
                s = import_file[import_file[:,0] == i][:,7]
                error_s[i] = s[s == 1].size/s.size
        print("session_error: {}".format(error_s))
        err = import_file[import_file[:, 7] == 1][:, 7].size/import_file[:, 7].size
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
        # id_effective1 = np.log2(d_raw / w_effective + 1)
        # print("id_e = log(D/W_e + 1): {}".format(id_effective1))
        id_effective = np.log2(d_effective / w_effective + 1)
        print("id_e = log(D_e/W_e + 1): {}".format(id_effective))

        #print(import_file[:, 5])
        true_time = np.empty(0)
        # id_effective_forfit1 = np.empty(0)
        id_effective_forfit = np.empty(0)
        for i in id_raw:
                d = import_file[import_file[:,6] == i][:, 3]
                true_time = np.append(true_time, statistics.mean(d))
        true_time = np.unique(true_time)
        print(true_time)

        for i in range(9):
                for j in range(num_of_targets*persons*5):
                        id_effective_forfit = np.append(id_effective_forfit, id_effective[i])

        print("id_e = log(D_e/W_e + 1)")
        fitted = np.polyfit(id_effective_forfit, time_raw, 1)
        b, a = fitted
        print("MT =  {} + {}  log(D/W + 1) ".format(a,b))
        mt_predict = a+b*id_unique
        tp = id_effective / true_time
        print("TP = {}".format(statistics.mean(tp)))
        print("Err = {}".format(err))
        r2 = np.round(r2_score(true_time, mt_predict), decimals=3)
        print("r2 = {}\n".format(r2_score(true_time, mt_predict)))

        plt.scatter(id_effective_forfit, time_raw, s=5, marker=shape,
                    c=cmap(cmap_num), label="選択時間({})".format(name))
        p = np.poly1d(fitted)(xp)
        plt.plot(xp, p, label=("選択予想時間 ({}): {}+{}*ID, r2:{}".format(name,
                                                                     round(fitted[1], 3), round(fitted[0], 3), r2)))
        return statistics.mean(tp), err


throughput[0], error[0] = fitts_fit(
    "P1", "./leg/data_p1_left_horizontal.csv", 0, '^')
throughput[1], error[1] = fitts_fit(
    "P2", "./leg/data_p2_left_horizontal.csv", 1, 'x')
throughput[2], error[2] = fitts_fit(
    "P3", "./leg/data_p3_left_horizontal.csv", 2, '+')
throughput[3], error[3] = fitts_fit("P4", "./leg/data_p4_left_horizontal.csv", 3, '+')

# plt.scatter(id_effective_forfit, time_raw, s=5, c='red', label='selection time')
# plt.plot(xp, p, label=("predict time (r2: " + str(r2) + ")"))
plt.legend(loc='upper left',borderaxespad=0, fontsize=10)
#plt.xlim(0, 1920)
plt.ylim(0,10)
plt.xlim(0.0,5.5)
plt.savefig('Horizontal_left.png')
print("TPs: {}".format(throughput))
print("mean TP: {}".format(statistics.mean(throughput)))
print(statistics.mean(error))
#plt.show()




