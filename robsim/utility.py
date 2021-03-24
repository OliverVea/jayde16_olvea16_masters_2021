from primitives.point import Point

from math import sqrt, ceil, pow

def dist_l1(a: Point, b: Point) -> float:
    s = 0
    for ai, bi in zip(a, b):
        s += abs(ai - bi)
    return s

def dist_l2(a: Point, b: Point) -> float:
    s = 0
    for ai, bi in zip(a, b):
        s += (ai - bi) * (ai - bi)
    return sqrt(s)

def dist_max(a: Point, b: Point) -> float:
    s = 0
    for ai, bi in zip(a, b):
        s = max(s, abs(ai - bi))
    return s

dist_names = {'l1': dist_l1, 'l2': dist_l2, 'max': dist_max}

def closest_point(a: Point, b: list, dist='l2') -> Point:
    dist = dist_names[dist]

    return min(b, key= lambda pt: dist(a, pt))

def interpolate(a: Point, b: Point, d: int = None, N: int = None):
    if N == None:
        dist = dist_l2(a, b)
        N = ceil(dist / d)

    K = [(n) / (N - 1) for n in range(N)]
    pts = [(a * (1 - k) + b * k) for k in K]

    return pts

def rom_spline(P, d: float = None, N: int = None, alpha: float = 0, t: tuple = (0.0, 0.333, 0.667, 1.0)):
    if N == None:
        dist = dist_l2(P[1], P[2])
        N = ceil(dist / d)

    x = [pt.x for pt in P]
    y = [pt.y for pt in P]
    v = [pt.theta for pt in P]

    t0 = 0
    t1 = pow(sqrt((x[1] - x[0])**2 + (y[1] - y[0])**2 + (v[1] - v[0])**2), alpha) + t0
    t2 = pow(sqrt((x[2] - x[1])**2 + (y[2] - y[1])**2 + (v[2] - v[1])**2), alpha) + t1
    t3 = pow(sqrt((x[3] - x[2])**2 + (y[3] - y[2])**2 + (v[3] - v[2])**2), alpha) + t2

    T = [(t2 - t1) * n / (N - 1) + t1 for n in range(N)]

    pts = []
    for t in T:
        A1 = P[0] * (t1 - t) / (t1 - t0) + P[1] * (t - t0) / (t1 - t0)
        A2 = P[1] * (t2 - t) / (t2 - t1) + P[2] * (t - t1) / (t2 - t1)
        A3 = P[2] * (t3 - t) / (t3 - t2) + P[3] * (t - t2) / (t3 - t2) 

        B1 = A1 * (t2 - t) / (t2 - t0) + A2 * (t - t0) / (t2 - t0)
        B2 = A2 * (t3 - t) / (t3 - t1) + A3 * (t - t1) / (t3 - t1) 
        
        pt = B1 * (t2 - t) / (t2 - t1) + B2 * (t - t1) / (t2 - t1)

        pts.append(pt)

    return pts




