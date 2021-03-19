from primitives.point import Point

from math import sqrt

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
