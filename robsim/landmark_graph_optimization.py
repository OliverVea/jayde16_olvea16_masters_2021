from SLAM import *

from primitives import Pose, Point, Line

import json
from tqdm import tqdm
import matplotlib.pyplot as plt

with open('lidar_data.json') as f:
    data = json.load(f)

reduction = 0.1
reduced_data = []
for i, state in enumerate(data):
    if len(reduced_data) < i * reduction:
        reduced_data.append(state)

data = reduced_data

last_pose = Pose(*data[0]['origin'])
slam = Graph(initial_pose=last_pose)

corners = []

for row in tqdm(data[1:50]):
    pose, scan = row.values()

    pose = Pose(*pose)
    scan = [Point(*pt) for pt in scan]

    odometry_constraint = pose.relative(last_pose)

    lines, landmarks = get_corners(scan, angle_threshold=2, pt_threshold=5, dist_threshold=0.02)

    for landmark in landmarks:
        corner = landmark.absolute(pose)
        corners.append(corner)

    slam.add_odometry(odometry_constraint)

    last_pose = pose

ws = Workspace('./workspaces/office_workspace_1.json') 
ws.plot()

plt.plot([corner.x for corner in corners], [corner.y for corner in corners], 'x', c='r')
plt.plot([pose.x for pose in slam.poses], [pose.y for pose in slam.poses])
plt.show()