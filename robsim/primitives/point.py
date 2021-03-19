from math import sqrt

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __iter__(self):
        return iter([self.x, self.y])

    def norm(self):
        return sqrt(self.x * self.x + self.y * self.y)

    def normalize(self):
        n = self.norm()
        return Point(self.x / n, self.y / n)