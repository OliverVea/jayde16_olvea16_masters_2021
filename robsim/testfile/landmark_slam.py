# %% Imports
import sys
import os
import json

from math import atan2, pi

import matplotlib.pyplot as plt
from numpy.random import standard_cauchy

cwd = os.path.abspath(os.path.join('..')) + '\\'
#cwd = 'D:\\WindowsFolders\\Code\\Master\\jayde16_olvea16_masters_2021\\robsim\\'
if cwd not in sys.path:
    sys.path.append(cwd)

print(f'cwd: {cwd}')

import robsim as rs

print(f'robsim module version: {rs.__version__}')

# %% Load workspace

config_file = f'{cwd}\\workspaces\\office_workspace_1.json'
map_file = f'{cwd}\\workspaces\\office_workspace_1.png'

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
    with open(f'{cwd}data\\office_workspace_1_default_landmarks.json', 'r') as f:
        landmarks = json.load(f)

default_landmarks = (i != 'y')

ws.set_landmarks(landmarks)
# %% Getting route nodes

i = rs.timed_input('Enter manual path? (y/n): ', 'Timed out, using default path.', timeout=2)

if i == 'y':
    ws.plot(figname='Workspace', grid_size=1)
    plt.show(block=False)

    print(f'Click to make a path for the robot to follow.')

    nodes = plt.ginput(n=-1)

else:
    with open(f'{cwd}data\\office_workspace_1_default_route.json', 'r') as f:
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

route = [pose for path in paths for pose in path]

# %% Plot the route

if rs.check_ipython() or rs.timed_input('Enter manual path? (y/n): ', 'Timed out, using default path.', timeout=2) == 'y':
    ws.plot(figname='Workspace', grid_size=1)

    route_x = [pose.x for pose in route]
    route_y = [pose.y for pose in route]

    plt.plot(route_x, route_y, '--', color='green')

    plt.figure('Angle')

    ax = plt.gca()
    ax.set_ylabel('Angle [radians]')
    ax.set_xlabel('Time')
    ax.set_xticks([])

    plt.plot([pose.theta for pose in route], '-')

    plt.show()

# %% Get landmark measurements
from tqdm import tqdm

print(f'Default landmarks - {default_landmarks} and default route . {default_route}: ', end='')

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
    with open(f'{cwd}data\\office_workspace_1_default_landmark_measurements.json', 'r') as f:
        landmarks = json.load(f)
    
    landmarks = [[(pt[0], rs.Point(*pt[1:])) for pt in measurements] for measurements in landmarks]
    
# %% Save landmark measurements
with open(f'{cwd}data\\office_workspace_1_landmark_measurements.json', 'w') as f:
    json.dump([[[i, pt.x, pt.y] for i, pt in measurements] for measurements in landmarks], f)

print(f'Landmarks saved.')
# %% Show the route

if not rs.check_ipython() and False:
    # Doesnt actually work lmfao
    from matplotlib import animation
    from IPython.display import HTML

    fig = ws.plot(figname='Workspace', figsize=(8, 8))

    pose = route[0]
    landmarks = [pt.absolute(pose) for pt in landmarks[0]]

    plt_pose = plt.plot(pose.x, pose.y, 'o', color='red')[0]
    plt_landmarks = plt.plot([pt.x for pt in landmarks], [pt.y for pt in landmarks], 's', color='green')[0]
    plt_landmark_lines = plt.plot()

    reduced_route = route
    reduced_landmarks = landmarks

    def update(i):
        pose = reduced_route[i]
        landmarks = [pt.absolute(pose) for pt in reduced_landmarks[i]]

        plt_pose.set_data(pose.x, pose.y)
        plt_landmarks.set_data([pt.x for pt in landmarks], [pt.y for pt in landmarks])

        return (plt_pose, plt_landmarks)

    reduced_route = rs.reduce_list(route, 0.1)
    reduced_landmarks = rs.reduce_list(landmarks, 0.1)

    anim = animation.FuncAnimation(fig, update, frames=len(reduced_route), interval=25, blit=True)

    plt.show()

else:
    print('I\'m too lazy to get the animation working in IPython.')

# %% Add noise to route
from robsim.utility import add_radial_noise_pose as noise

std_d = 0.55
std_a1 = 0.5
std_a2 = 0.5

print(f'Adding noise with standard deviations:\ndistance - {std_d}\nangle 1 - {std_a1}\nangle 2 - {std_a2}')

relative_route = [b.relative(a) for a, b in zip(route[:-1], route[1:])]
noisy_relative_route = [noise(pose, std_d=std_d, std_a1=std_a1, std_a2=std_a2) for pose in relative_route]
noisy_route = [route[0]]
for pose in noisy_relative_route: noisy_route.append(pose.absolute(noisy_route[-1]))

fig = ws.plot(figname='Workspace', figsize=(8, 8))
plt.plot([p.x for p in route], [p.y for p in route], '--', color='green', label='true route')
plt.plot([p.x for p in noisy_route], [p.y for p in noisy_route], '-', color='red', label='noisy route')
plt.legend()
plt.show()

# %% Add noise to landmarks
from robsim.utility import add_radial_noise_point as noise

print('Adding noise to points...')
noisy_landmarks = [[[i, noise(point, std_d=0.01, std_a=0.005)] for i, point in measurements] for measurements in tqdm(landmarks)]

cmap = plt.cm.get_cmap('hsv', len(ws.landmarks))

fig = ws.plot(figname='Workspace', figsize=(8, 8))

print('Plotting points...')
for i in tqdm(range(len(ws.landmarks))):
    pts = []
    for j, measurements in enumerate(noisy_landmarks):
        for k, point in measurements:
            if i == k:
                pts.append(point.absolute(route[j]))

    plt.plot([pt.x for pt in pts], [pt.y for pt in pts], 'x', color=cmap(i))

plt.show()

# %% Normal distribution power demo
import numpy as np

n = 100000

v1 = np.random.normal(0, 1, (n,))
v2 = np.random.normal(0, 1, (n,)) * np.random.normal(0, 1, (n,))
v3 = np.random.normal(0, 1, (n,)) * np.random.normal(0, 1, (n,)) \
    * np.random.normal(0, 1, (n,)) * np.random.normal(0, 1, (n,)) \
    * np.random.normal(0, 1, (n,)) * np.random.normal(0, 1, (n,))

plt.hist(v1, 100, label='Baseline', density=True)
plt.hist(v2, 200, label='Multiplied with itself', density=True)
plt.hist(v3, 600, label='Multiplied with itself six times', density=True)

plt.legend()

ax = plt.gca()
ax.set_xlim((-10, 10))
ax.set_ylim((0, 0.65))

plt.show()

plt.figure(dpi=200)

im = plt.imread(f'{cwd}output\\noise_hypothesis.png')
plt.imshow(im)

print(f'This is kind of what happens when the error is applied with a normal on every odometry step with a really high sample frequency. It technically works but the expected variation of the error is tiny and extremes become more common.')

# %% Do SLAM
