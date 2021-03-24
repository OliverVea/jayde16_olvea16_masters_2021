from math import sin, cos, degrees, radians

from json import JSONEncoder, JSONDecoder, dumps, loads

degree_sign= u'\N{DEGREE SIGN}'

class Coordinate:
    def __init__(self, x: float, y: float, theta: float):
        self.x = x
        self.y = y
        self.theta = theta

    def __str__(self):
        return f'({self.x:.1f}, {self.y:.1f}, {degrees(self.theta):.1f}{degree_sign})'

    def __iter__(self):
        return iter([self.x, self.y, self.theta])

    # Returns a relative coordinate in respect to another coordinate.
    def relative(self, other):
        x = self.x - other.x
        y = self.y - other.y

        theta = self.theta - other.theta
        x, y = x * cos(-other.theta) - y * sin(-other.theta), \
               x * sin(-other.theta) + y * cos(-other.theta)

        return Coordinate(x, y, theta)

    # Returns the global coordinate in respect to another coordinate.
    def absolute(self, other):
        theta = other.theta + self.theta

        x, y = self.x * cos(other.theta) - self.y * sin(other.theta), \
               self.x * sin(other.theta) + self.y * cos(other.theta)

        x = x + other.x
        y = y + other.y

        return Coordinate(x, y, theta)

    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y, self.theta + other.theta)

    def __sub__(self, other):
        return Coordinate(self.x - other.x, self.y - other.y, self.theta - other.theta)

    def __mul__(self, k):
        return Coordinate(self.x * k, self.y * k, self.theta * k)

    def __truediv__(self, k):
        return Coordinate(self.x / k, self.y / k, self.theta / k)

    def set_x(self, val):
        self.x = val
        return self

    def set_y(self, val):
        self.y = val
        return self

    def set_theta(self, val):
        self.theta = val
        return self

    def to_json(self):
        return [self.x, self.y] + [t for t in [self.theta] if t != 0.0]

    @staticmethod
    def from_json(obj):   
        return Coordinate(x=obj[0], y=obj[1], theta=(obj[2:] + [0])[0])
        
if __name__ == '__main__':
    a = Coordinate(5, 3, radians(90))
    b = Coordinate(8, 1, radians(0))

    print(f'{a} - {b} = {a - b}')
    print(f'{b} - {a} = {b - a}')
    
    print(f'{a} - {b} + {b} = {a - b + b}')
    print(f'{b} - {a} + {a} = {b - a + a}')

    s = dumps(a.to_json())
    print(f'{a} as JSON: {s}')
    print(f'{s} as Coordinate: {Coordinate.from_json(loads(s))}')
    
    s = dumps(b.to_json())
    print(f'{b} as JSON: {s}')
    print(f'{s} as Coordinate: {Coordinate.from_json(loads(s))}')

    