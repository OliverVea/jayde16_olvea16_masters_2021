import json
import matplotlib.pyplot as plt
import numpy as np
from workspace import Workspace

with open('noisy_lidar_data.json') as f:
    file = json.load(f)

ws = Workspace('./workspaces/office_workspace_1.json')
ws.plot()

true_path = [[],[]]
noisy_path = [[],[]]
error = []

for ms in file:
    true_path[0].append(ms['groundtruth']['origin'][0])
    true_path[1].append(ms['groundtruth']['origin'][1])
    noisy_path[0].append(ms['noisy']['origin'][0])
    noisy_path[1].append(ms['noisy']['origin'][1])
    error.append(np.sqrt((ms['groundtruth']['origin'][0] - ms['noisy']['origin'][0])**2 + (ms['groundtruth']['origin'][1] - ms['noisy']['origin'][1])**2))

plt.plot(true_path[0], true_path[1])
plt.plot(noisy_path[0], noisy_path[1])
plt.show()

plt.figure()
plt.plot(error)
plt.show()