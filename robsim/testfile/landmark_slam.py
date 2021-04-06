# %% Imports
import sys
import os
import json

from math import atan2, pi

import matplotlib.pyplot as plt

cwd = os.path.abspath(os.path.join('..'))
cwd = 'd:\\WindowsFolders\\Code\\Master\\jayde16_olvea16_masters_2021\\robsim'

if cwd not in sys.path:
    sys.path.append(cwd)

print(f'cwd: {cwd}')

import robsim as rs

print(f'robsim module version: {rs.__version__}')

# %% Load workspace

config_file = os.path.join(cwd, 'workspaces/office_workspace_1.json')
map_file = os.path.join(cwd, 'workspaces/office_workspace_1.png')

ws = rs.Workspace(
    config_file=config_file, 
    background_file=map_file
)

# %% Getting landmarks

i = rs.timed_input('Enter manual landmarks? (y/n): ', 'Timed out, using default landmarks.', timeout=2)

if i == 'y':
    ws.plot(figname='Workspace', grid_size=1)
    plt.show(block=False)

    print(f'Click to place landmarks.')

    landmarks = plt.ginput(n=-1)

else:
    path = os.path.join(cwd, 'data/office_workspace_1_default_landmarks.json')
    with open(path, 'r') as f:
        landmarks = json.load(f)

default_landmarks = (i != 'y')

ws.set_landmarks(landmarks)
# %% Getting route nodes

i = rs.timed_input('Enter manual path? (y/n): ', 'Timed out, using default path.', timeout=2)

if i == 'y':
    ws.plot(figname='Workspace', grid_size=1)
    plt.show()

    print(f'Click to make a path for the robot to follow.')

    nodes = plt.ginput(n=-1)

else:
    path = os.path.join(cwd, 'data/office_workspace_1_default_route.json')
    with open(path, 'r') as f:
        nodes = json.load(f)

default_route = (i != 'y')

# %% Interpolating route

d = 0.01 # Approximate step size for the interpolation.

angles = [atan2((y2 - y1), (x2 - x1)) for (x1, y1), (x2, y2) in zip(nodes[:-1], nodes[1:])]
angles = [angles[0]] + angles

angles = [angle % (2 * pi) for angle in angles]

for i in range(len(angles) - 1):
    angles[i + 1] = rs.minimize_angular_difference(angles[i], angles[i + 1])

poses = [rs.Pose(click[0], click[1], v) for v, click in zip(angles, nodes)]

poses = [poses[0]] + poses + [poses[-1]]

paths = [rs.rom_spline(poses[i:i+4], d=d) for i in range(len(poses) - 3)]

full_route = [pose for path in paths for pose in path]

# This breaks noise application
#route = [rs.Pose(pose.x, pose.y, pose.theta % (2 * pi)) for pose in route]

# %% Plot the route
if rs.check_ipython() or rs.timed_input('Enter manual path? (y/n): ', 'Timed out, using default path.', timeout=2) == 'y':
    ws.plot(figname='Workspace', grid_size=1)

    route_x = [pose.x for pose in full_route]
    route_y = [pose.y for pose in full_route]

    plt.plot(route_x, route_y, '--', color='green')

    plt.figure('Angle')

    ax = plt.gca()
    ax.set_ylabel('Angle [radians]')
    ax.set_xlabel('Time')
    ax.set_xticks([])

    plt.plot([pose.theta for pose in full_route], '.', markersize=1)

    plt.show(block=False)

# %% Reduce poses in the route
route = rs.reduce_list(full_route, 0.05)

default_route = False

print(f'Reduced route from {len(full_route)} nodes to {len(route)} nodes.')

# %% Get landmark measurements
from tqdm import tqdm

print(f'Default landmarks - {default_landmarks} and default route - {default_route}: ', end='')

default_measurements = (default_landmarks and default_route)

if not default_measurements:
    print('Computing measurements.')
    landmarks = []
    for pose in tqdm(route):
        measurements = []
        for i, landmark in enumerate(ws.landmarks):
            origin = rs.Point(pose.x, pose.y)
            landmark = rs.Point(*landmark)
            line = rs.Line(origin, landmark)

            intersections = ws.get_intersections(line)
            intersections = [rs.Point(*i) for i in intersections]
            
            d = rs.dist_l2(origin, landmark)

            if not any([False] + [d > rs.dist_l2(origin, i) for i in intersections]):
                pt = landmark.relative(pose)
                measurements.append((i, pt))
        landmarks.append(measurements)
else:
    print('Using pre-computed measurements.')
    path = os.path.join(cwd, 'data/office_workspace_1_default_landmark_measurements.json')
    with open(path, 'r') as f:
        landmarks = json.load(f)
    
    landmarks = [[(pt[0], rs.Point(*pt[1:])) for pt in measurements] for measurements in landmarks]
    
# %% Save landmark measurements
path = os.path.join(cwd, 'data/office_workspace_1_default_landmark_measurements.json')
with open(path, 'w') as f:
    json.dump([[[i, pt.x, pt.y] for i, pt in measurements] for measurements in landmarks], f)

# %% Get LIDAR measurements
if not default_route:
    lidar_scans = [ws.lidar_scan(pose, fov=360, da=1.25) for pose in route]
    lidar_scans = [[pt.relative(pose) for pt in scan] for pose, scan in zip(route, lidar_scans)]
 
    path = os.path.join(cwd, 'data/office_workspace_1_default_lidar_scans.json')
    with open(path, 'w') as f:
        obj = [[[pt.x, pt.y] for pt in scan] for scan in lidar_scans]
        json.dump(obj, f)

else: 
    path = os.path.join(cwd, 'data/office_workspace_1_default_lidar_scans.json')
    with open(path, 'r') as f:
        lidar_scans = json.load(f)
        lidar_scans = [[rs.Point(*pt) for pt in scan] for scan in lidar_scans]
        
# %% Add noise to route
from robsim.utility import add_radial_noise_pose as noise

std_d = 0.5
std_a1 = 0.25
std_a2 = 0.25

print(f'Adding odometry noise with standard deviations:\ndistance - {std_d}\nangle 1 - {std_a1}\nangle 2 - {std_a2}')

relative_route = [b.relative(a) for a, b in zip(route[:-1], route[1:])]
noisy_relative_route = [noise(pose, std_d=std_d, std_a1=std_a1, std_a2=std_a2) for pose in relative_route]
noisy_route = [route[0]]
for pose in noisy_relative_route: noisy_route.append(pose.absolute(noisy_route[-1]))

fig = ws.plot(figname='Workspace', figsize=(8, 8))
plt.title('Odometry noise')
plt.plot([p.x for p in route], [p.y for p in route], '--', color='green', label='true route')
plt.plot([p.x for p in noisy_route], [p.y for p in noisy_route], '-', color='red', label='noisy route')
plt.legend()
plt.show()

# %% Add noise to landmarks
from robsim.utility import add_radial_noise_point as noise
std_d = 0.01
std_a = 0.005

print(f'Adding landmark noise with standard deviations:\ndistance - {std_d}\nangle 1 - {std_a1}\nangle 2 - {std_a2}')

noisy_landmarks = [[[i, noise(point, std_d=std_d, std_a=std_a)] for i, point in measurements] for measurements in tqdm(landmarks)]

cmap = plt.cm.get_cmap('hsv', len(ws.landmarks))

fig = ws.plot(figname='Workspace', figsize=(8, 8))
plt.title('Noisy landmark measurements')

print('Plotting points...')
for i in tqdm(range(len(ws.landmarks))):
    pts = []
    for j, measurements in enumerate(noisy_landmarks):
        for k, point in measurements:
            if i == k:
                pts.append(point.absolute(route[j]))

    plt.plot([pt.x for pt in pts], [pt.y for pt in pts], 'x', color=cmap(i))
plt.show()

# %% Plot LIDAR with original route
lidar_absolute = [[pt.absolute(pose) for pt in scan] for pose, scan in zip(route, lidar_scans)]

ws.plot(figsize=(8, 8), dpi=200)
plt.title('Lidar data without odometry noise')
x = [pt.x for scan in lidar_absolute for pt in scan]
y = [pt.y for scan in lidar_absolute for pt in scan]
plt.plot(x, y, '.', color='black', markersize=1)
plt.show()

# %% Plot LIDAR with noisy route
noisy_lidar_absolute = [[pt.absolute(pose) for pt in scan] for pose, scan in zip(noisy_route, lidar_scans)]

plt.figure(figsize=(8, 8), dpi=200)
plt.title('Lidar data with odometry noise')
x = [pt.x for scan in noisy_lidar_absolute for pt in scan]
y = [pt.y for scan in noisy_lidar_absolute for pt in scan]
plt.plot(x, y, '.', color='black', markersize=1)
ax = plt.gca()
ax.invert_yaxis()
ax.set_aspect(1)
plt.plot()
plt.show()
# %%
print(f'{len(route)}, {len(noisy_route)}, {len(relative_route)}, {len(noisy_relative_route)}')

# %% Do SLAM
slam = rs.Slam(route[0], n_landmarks=len(ws.landmarks), cov_odometry=None, cov_landmarks=None)

for i, (odometry_constraint, landmark_constraints) in tqdm(enumerate(zip(noisy_relative_route, noisy_landmarks[1:])), total=len(noisy_relative_route)):
    slam.add_constraints(odometry_constraint, landmark_constraints)
    slam.optimize()

# %% Plot sparsity
sparsity = slam.get_sparsity()

print(f'route: {len(slam.route)}')
print(f'landmarks: {len(slam.landmarks)}')

n = len(slam.route)*3+len(slam.landmarks)*2
m = len(slam.odometry_constraints) + sum(len(constraints) for constraints in slam.landmark_constraints)

print(f'm = {m}, n = {n}')
print(f'Sparsity matrix shape: {sparsity.shape}')

fig = plt.figure(figsize=(8,12), dpi=300)
plt.spy(sparsity)

# %% Plot SLAM
ws.plot(figsize=(8, 8), dpi=200)

x = [pt.x for pt in noisy_route]
y = [pt.y for pt in noisy_route]
plt.plot(x, y, '-', color='red', label='noisy route')


x = [pt.x for pt in route]
y = [pt.y for pt in route]
plt.plot(x, y, '--', color='green', label='original route')

x = [pt.x for pt in slam.route]
y = [pt.y for pt in slam.route]
plt.plot(x, y, '--', label='SLAM route')

x = [pt.x for pt in slam.landmarks if pt != None]
y = [pt.y for pt in slam.landmarks if pt != None]
plt.plot(x, y, 'x', color='green')

plt.legend()
plt.show(block=False)

fig = slam.plot(plot_landmark_measurements=True)
ax = plt.gca()
ax.invert_yaxis()
plt.show()
# %% Plot LIDAR with SLAM route
slam_lidar_absolute = [[pt.absolute(pose) for pt in scan] for pose, scan in zip(slam.route, lidar_scans)]

plt.figure(figsize=(8, 8), dpi=200)
plt.title('Lidar data with odometry noise')
x = [pt.x for scan in slam_lidar_absolute for pt in scan]
y = [pt.y for scan in slam_lidar_absolute for pt in scan]
plt.plot(x, y, '.', color='black', markersize=1)
ax = plt.gca()
ax.invert_yaxis()
ax.set_aspect(1)
plt.plot()
plt.show()
# %%
