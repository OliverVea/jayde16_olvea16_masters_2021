from primitives.point import Point
from primitives.line import Line

from math import log, atan2
from random import choice, random

def fit_line(pts, threshold: float, T: int = None, p: float = 0.99, e: float = 0.5):
    assert len(pts) > 1
    if T == None:
        T = int(log(1 - p) / log(1 - (1 - e)**2))

    inliers = []
    outliers = []
    for t in range(T):
        a = b = choice(pts)
        while b == a:
            b = choice(pts)

        temp_line = Line(a, b)

        temp_inliers = [pt for pt in pts if temp_line.get_distance(pt) <= threshold]
        temp_outliers = [pt for pt in pts if not pt in temp_inliers]

        if len(temp_inliers) > len(inliers):
            line = temp_line
            inliers = temp_inliers
            outliers = temp_outliers

    return line, inliers, outliers


def get_corners(pts, angle_threshold: float = 5, pt_threshold: int = 6, dist_threshold: float = 0.01, T: int = None, p: float = 0.99, e: float = 0.5):
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

            a0, a1 = inliers_a[0], inliers_a[-1]
            b0, b1 = inliers_b[0], inliers_b[-1]

            va0, va1 = atan2(a0.y, a0.x), atan2(a1.y, a1.x)
            vb0, vb1 = atan2(b0.y, b0.x), atan2(b1.y, b1.x)

            p, t, u = a.get_intersection(b)

            if -0.1 <= t <= 1.1 and -0.1 <= u <= 1.1:
                pts.append(p)
    
    return p

    print(len(lines))

import matplotlib.pyplot as plt

xs = [100 * i / 20 for i in range(20)]
ys = [x + random() for x in xs]

pts = [Point(x, y) for x, y in zip(xs, ys)]

xs = [100 * i / 20 for i in range(20)]
ys = [-x + 50 + random() for x in xs]

pts = pts + [Point(x, y) for x, y in zip(xs, ys)]

pts = sorted(pts, key = lambda pt: atan2(pt.y, pt.x))

for i in range(len(pts) - 1):
    plt.plot([pt.x for pt in pts[:i + 1]], [pt.y for pt in pts[:i + 1]], 'o')
    plt.axline((0, 0), (pts[i].x, pts[i].y))
    plt.show()

corners = get_corners(pts, pt_threshold=6, dist_threshold=1)

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
    