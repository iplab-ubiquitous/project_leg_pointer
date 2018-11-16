import numpy as np
import matplotlib.pyplot as plt
import sys
import math

path = str(sys.argv[1])

import_file = np.loadtxt(path, delimiter=',', skiprows=1)

log_id = [math.log2(i) for i in import_file[:, 4]]
tm = import_file[:, 2]

fitted = np.polyfit(log_id, tm, 1)
b, a = fitted
print("T = " + str(a) + " + " + str(b) + " log(D/W + 1) ")
p = np.poly1d(fitted)
p30 = np.poly1d(np.polyfit(log_id, tm, 30))
xp = np.linspace(0, 10, 100)

plt.plot(log_id, tm, '.', xp, p(xp), '-')
plt.ylim(-2, 2)
plt.show()
plt.savefig('image.png')
