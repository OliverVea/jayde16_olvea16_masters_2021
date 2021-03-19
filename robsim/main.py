from workspace import Workspace
from planners import PRM, RKMP
from primitives.line import Line
from primitives.point import Point
from utility import dist_l2, closest_point
from obstacles import CircleObstacle, RectangleObstacle
from robot import SimpleRobot

from SLAM import extended_kalman_filter

import matplotlib.pyplot as plt
import json
from random import random
from math import pi, sin, cos

test = 4

if test == 1:
    ws = Workspace('./workspaces/simple_test_1.json')
    ws.plot()

    prm = PRM(ws, delta=0.01, k=1, r=2, distance_type='l2')
    prm.construct(500)
            
    for edge in prm.edges:
        x = [prm.nodes[edge[0]].x, prm.nodes[edge[1]].x]
        y = [prm.nodes[edge[0]].y, prm.nodes[edge[1]].y]
        
        plt.plot(x, y, '-', color='blue')

    plt.plot([pt.x for pt in prm.nodes], [pt.y for pt in prm.nodes], 'o', color='red')

    plt.show()

if test == 2:
    while True:
        h = 10
        w = 10

        pts = [Point(random() * w, random() * h) for _ in range(4)]

        l0 = Line(pts[0], pts[1])
        l1 = Line(pts[2], pts[3])

        p, t, u = l0.get_intersection(l1)

        d = 10000

        for l, pts, c in zip([l0, l1], [[l.eval_at(-d), l.eval_at(d + 1)] for l in [l0, l1]], ['r', 'b']):
            plt.plot([pt.x for pt in pts], [pt.y for pt in pts], '--', color=c)
            plt.plot([pt.x for pt in [l.a, l.b]], [pt.y for pt in [l.a, l.b]], '-', color=c)
            plt.plot([l.a.x, l.b.x], [l.a.y, l.b.y], 'o', color=c)
        
        if p != None:
            if 0 <= t <= 1:
                plt.plot(p.x, p.y, 'o', c='black')
            else:
                plt.plot(p.x, p.y, 'x', c='black')
        
        ax = plt.gca()
        ax.set(xlim=(-1, w + 1), ylim=(-1, h + 1))

        plt.show()

if test == 3:
    ws = Workspace('./workspaces/simple_test_1.json')

    while True:
        ws.plot()

        pts = [Point(random() * ws.dimensions[0], random() * ws.dimensions[1]) for _ in range(2)]

        while any([obstacle.check(pts[0]) for obstacle in ws.obstacles]):
             pts[0] = Point(random() * ws.dimensions[0], random() * ws.dimensions[1])

        line = Line(pts[0], pts[1])

        intersections = []

        for obstacle in ws.obstacles:
            intersections.extend(obstacle.get_intersections(line))

        #actual_intersections = [i[0] for i in intersections if 0 <= i[1] <= 1 and i[2] > 0]
        actual_intersections = intersections

        closest_pt = None
        if len(actual_intersections) > 0:
            closest_pt = closest_point(pts[0], actual_intersections)

        d = 10000

        p0 = line.eval_at(-d)
        p1 = line.eval_at(d + 1)

        plt.plot([p0.x, pts[0].x], [p0.y, pts[0].y], '--', color='black')
        plt.plot([pts[0].x, p1.x], [pts[0].y, p1.y], '-', color='black')


        for p in intersections:
            if p == closest_pt:
                plt.plot(p.x, p.y, 'o', color='r')
            elif 0 <= t <= 1 and u > 0:
                plt.plot(p.x, p.y, 'o', color='black')
            elif 0 <= t <= 1:
                plt.plot(p.x, p.y, 'x', color='black')

        plt.plot(pts[0].x, pts[0].y, '^', color='r')

        plt.show()

    pass

if test == 4:
    ws = Workspace('./workspaces/simple_test_1.json')

    while True:
        ws.plot()

        origin = ws.sample_free()
        angle = random() * 360

        l = 0.4
        dx, dy = cos(pi/180 * angle) * l, sin(pi/180 * angle) * l

        samples = ws.lidar_scan(origin, angle, 270, 1.25)

        for sample in samples:
            plt.plot([origin.x, sample.x], [origin.y, sample.y], '--', color=(1, 0, 0, 0.2))
            plt.plot(sample.x, sample.y, 'o', color=(0.7, 0, 0, 1), markersize=2)
        plt.plot([origin.x, origin.x + dx], [origin.y, origin.y + dy], color='black')
        plt.plot(origin.x, origin.y, '8', color='black')
        plt.show()

if test == 5:
    ws = Workspace('./workspaces/simple_test_1.json')        
    
    ws.plot()
    plt.show(block=False)
    clicks = plt.ginput(n=2)

    origin = Point(clicks[0][0], clicks[0][1])
    goal = Point(clicks[1][0], clicks[1][1])

    robot = SimpleRobot(
        dt=0.01, 
        v_min=-1, 
        v_max=2, 
        omega_min=-pi, 
        omega_max=pi, 
        logistic_max=True,
        a_mean=0.5,
        a_std=0.75,
        alpha_std=0.1)

    r = 0.1

    print('[STATUS] Searching for route..')

    planner = RKMP(ws, (origin.x, origin.y, 0, 0, 0),  robot, 
        steps=100, 
        grid_size=0.5, 
        check_state=lambda state: dist_l2(Point(state[0], state[1]), goal) < r)

    route = planner.solve(1e6)

    print('[STATUS] Route found.')

    # Save LiDAR
    if True:
        print('[STATUS] Extracting LiDAR data.')
        fov = 270   
        da = 1.25

        reduction = 0.5
        reduced_route = []
        for i, state in enumerate(route):
            if len(reduced_route) < i * reduction:
                reduced_route.append(state)

        data = [{'state': state, 'lidar': [(p.x, p.y) for p in ws.lidar_scan(Point(state[0], state[1]), angle=state[2], fov=fov, da=da)]} for state in reduced_route]

        filename = 'route.json'

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

        print(f'[STATUS] LiDAR data saved to \'{filename}\'.')

    if len(route) > 0:
        ws.plot()
        plt.plot([node[0] for node in route], [node[1] for node in route], '-', color='r')
        plt.plot(origin.x, origin.y, 'o', color='red')
        plt.plot(goal.x, goal.y, 'o', color='green')
        plt.show()

if test == 6:
    while True:
        circle_origin = Point(random() * 10 - 5, random() * 10 - 5)
        circle_radius = random() * 5

        p1 = Point(random() * 10 - 5, random() * 10 - 5)
        p2 = Point(random() * 10 - 5, random() * 10 - 5)

        obs = CircleObstacle(circle_origin, circle_radius)
        line = Line(p1, p2)

        intersections = obs.get_intersections(line)

        plt.figure()
        ax = plt.gca()

        ax.add_patch(obs.get_patch())
        d = 1

        p0 = line.eval_at(-d)
        p3 = line.eval_at(d + 1)

        plt.plot([p0.x, p1.x], [p0.y, p1.y], '--', color='r')
        plt.plot([p1.x, p2.x], [p1.y, p2.y], '-', color='r')
        plt.plot([p2.x, p3.x], [p2.y, p3.y], '--', color='r')

        for intersection in intersections:
            plt.plot(intersection.x, intersection.y, 'x', color='black')

        plt.show()

if test == 7:
    ws = Workspace('./workspaces/simple_test_1.json')
    
    density = 10

    co = CircleObstacle(Point(1, 3), 0.5)
    pts = co.get_points(density)

    ro = RectangleObstacle(Point(4, 2), (3, 2))
    pts.extend(ro.get_points(density)) 

    plt.plot([pt.x for pt in pts] + [pts[0].x], [pt.y for pt in pts] + [pts[0].y], 'o')
    plt.show()

    pass
        