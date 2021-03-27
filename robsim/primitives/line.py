from primitives.point import Point

from math import pi, atan2, tan
from utility import dist_l2

import numpy as np

class Line:
    @staticmethod
    def from_points(pts):
        assert len(pts) > 1
        pts = np.array([[pt.x, pt.y] for pt in pts]).transpose()

        covariance_matrix = np.cov(pts)
        weights, axes = np.linalg.eig(covariance_matrix)

        axis = axes[np.argmax(weights)]

        mean = np.average(pts, axis=1)

        line = Line(Point(mean[0], mean[1]), Point(mean[0] + axis[0], mean[1] + axis[1]))

        return line

    def from_points_fast(pts):
        assert len(pts) > 1
        return Line(pts[0], pts[-1])

    def __init__(self, a: Point, b: Point):
        assert (a != b), 'Points cannot be the same.'
        
        self.a = a
        self.b = b

    def get_intersection(self, line) -> (Point, bool):
        x1, x2, x3, x4 = self.a.x, self.b.x, line.a.x, line.b.x 
        y1, y2, y3, y4 = self.a.y, self.b.y, line.a.y, line.b.y

        b = ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))

        if b == 0:
            return None

        t =  ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / b

        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / b

        p = self.eval_at(t)

        return p, t, u

    def get_distance(self, point) -> float:
        a = atan2(self.b.y - self.a.y, self.b.x - self.a.x) + pi/2

        if 1/4 * pi <= a <= 3/4 * pi or 5/4 * pi <= a <= 7/4 * pi:
            y = point.y + 1
            x = point.x - tan(a) * (point.y - y)
        else:
            x = point.x + 1
            y = point.y - tan(a) * (point.x - x)

        line = Line(point, Point(x, y))

        p, t, u = self.get_intersection(line)

        return dist_l2(point, p)


    def eval_at(self, t):
        return Point(self.a.x + t * (self.b.x - self.a.x), self.a.y + t * (self.b.y - self.a.y))

    def get_scale(self, x: float = None, y: float = None):
        if y != None:
            return (y - self.a.y) / (self.b.y - self.a.y)
        return (x - self.a.x) / (self.b.x - self.a.x)