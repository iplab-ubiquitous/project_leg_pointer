import numpy as np
import matplotlib.pyplot as plt
import sys
import math

path = str(sys.argv[1])

import_file = np.loadtxt(path, delimiter=',', skiprows=1)

x = import_file[:, 0]
y = import_file[:, 1]
d_id = []

delta_t = min(import_file[import_file[:, 2] == 2][:, 4]) - import_file[import_file[:, 2] == 1][:, 4]
#d_id = import_file[import_file[:, 2] == 1][:, 6]
d_id = np.array([math.log2(v) for v in import_file[import_file[:, 2] == 1][:, 6]] )

print(delta_t.shape[0])
print(d_id)



fitted = np.polyfit(d_id, delta_t, 1)
b, a = fitted
print("T = " + str(a) + " + " + str(b) + " log(D/W + 1) ")
p = np.poly1d(fitted)
p30 = np.poly1d(np.polyfit(d_id, delta_t, 30))
xp = np.linspace(0, 10, 100)

plt.plot(d_id, delta_t, '.')
#plt.xlim(0, 1920)
plt.ylim(1,5)
plt.show()
plt.savefig('image.png')
