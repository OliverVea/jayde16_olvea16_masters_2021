from primitives.point import Point
from primitives.line import Line
from utility import dist_l2

from math import log, atan2, pi, radians, degrees
from random import choice, random

def fit_line(pts, threshold: float, T: int = None, p: float = 0.99, e: float = 0.5):
    assert len(pts) > 1

    # https://www.youtube.com/watch?v=9D5rrtCC_E0 (3:30)
    if T == None:
        T = int(log(1 - p) / log(1 - (1 - e)**2))

    inliers = []
    outliers = []
    for t in range(T):
        a = b = choice(pts)

        # Samples point b to be different to a, since random.choice doesnt have replace = False for some reason.
        while b == a:
            b = choice(pts)

        temp_line = Line(a, b)

        # temp_inliers = []
        # for pt in pts:
        #     if temp_line.get_distance(pt) <= threshold:
        #         temp_inliers.append(pt)
        #     else:
        #         # This makes sure that there are no gaps in lines.
        #         if len(temp_inliers) > 0:
        #             break

        temp_inliers = [pt for pt in pts if temp_line.get_distance(pt) <= threshold]
        temp_outliers = [pt for pt in pts if not pt in temp_inliers]

        if len(temp_inliers) > len(inliers):
            line = temp_line
            inliers = temp_inliers
            outliers = temp_outliers

    return line, inliers, outliers

def angle_diff(a, b):
    return min(abs(a - b), abs(a - b + 2*pi), abs(a - b - 2*pi))

def is_between(angle, a_from, a_to, d: float = 0):
    if a_from < a_to:
        return a_from - d <= angle <= a_to + d
    return a_to - d <= angle <= a_from + d

def get_angular_difference(origin: Point, a: Point, b: Point, t: str = 'radians'):
    v = [atan2(pt.y - origin.y, pt.x - origin.x) for pt in [a, b]]
    d = angle_diff(*v)

    if t == 'degrees':
        return degrees(d)
    return d

def get_corners(pts, angle_threshold: float = 7, pt_threshold: int = 6, dist_threshold: float = 0.01, T: int = None, p: float = 0.99, e: float = 0.5):
    lines = []

    while len(pts) > pt_threshold:
        line, inliers, pts = fit_line(pts, 
            threshold=dist_threshold, 
            T=T, 
            p=p, 
            e=e)

        if len(inliers) < pt_threshold:
            break

        lines.append((line, inliers))

    pts = []

    for i, (a, inliers_a) in enumerate(lines):
        for (b, inliers_b) in lines[i + 1:]:
            dists = [get_angular_difference(Point(0,0), inlier_a, inlier_b, t='degrees') for inlier_a in inliers_a for inlier_b in inliers_b]

            if min(dists) > angle_threshold:
                continue

            r = a.get_intersection(b)
            if r == None:
                continue

            p, t, u = r
            pts.append(p)
    
    return lines, pts

    print(len(lines))

import matplotlib.pyplot as plt
import json

with open('lidar_data.json') as f:
    data = json.load(f)

while True:
    pts = choice(data)['scan']

    max_range = 4

    pts = [Point(pt[0], pt[1]) for pt in pts if dist_l2(Point(0, 0), pt) < max_range]

    dists = [dist_l2(Point(0, 0), pt) for pt in pts]

    lines, corners = get_corners(pts, pt_threshold=3, dist_threshold=0.02)

    plt.plot((0,), (0,), 'o', color='r')

    for pt in pts:
        plt.plot((0, pt.x), (0, pt.y), '--', color='black')

    plt.plot([pt.x for pt in pts], [pt.y for pt in pts], 'x')

    for (line, inliers) in lines:
        plt.axline((line.a.x, line.a.y), (line.b.x, line.b.y))
        plt.plot([pt.x for pt in inliers], [pt.y for pt in inliers], 'o')

    plt.plot([pt.x for pt in corners], [pt.y for pt in corners], 'x', color='r')

    ax = plt.gca()
    ax.set_aspect(1)

    plt.show()

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    a = 0.1
    b = 2
    N = 20

    xs = [100 * i / N for i in range(N)]
    ys = [a*x + b + random() for x in xs]

    pts = [Point(x, y) for x, y in zip(xs, ys)]

    line, inliers, outliers = fit_line(pts, threshold=1)

    plt.axline((line.a.x, line.a.y), (line.b.x, line.b.y))
    plt.plot([pt.x for pt in inliers], [pt.y for pt in inliers], 'o')
    plt.plot([pt.x for pt in outliers], [pt.y for pt in outliers], 'x')

    plt.show()
    