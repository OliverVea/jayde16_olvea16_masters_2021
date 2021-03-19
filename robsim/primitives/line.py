from primitives.point import Point

from math import pi, atan2, tan

class Line:
    def __init__(self, a: Point, b: Point):
        assert (a != b), 'Points cannot be the same.'
        
        self.a = a
        self.b = b

        self.d = Point(b.x - a.x, b.y - a.y)

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

    def eval_at(self, t):
        return Point(self.a.x + t * (self.b.x - self.a.x), self.a.y + t * (self.b.y - self.a.y))

    def get_scale(self, x: float = None, y: float = None):
        if y != None:
            return (y - self.a.y) / (self.b.y - self.a.y)
        return (x - self.a.x) / (self.b.x - self.a.x)