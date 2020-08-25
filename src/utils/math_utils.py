class Vec2(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def to_tuple(self):
        tup = (self.x, self.y)
        return tup

    def distance(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return pow(x * x + y * y, 0.5)

    def calc(self, value, other):
        x = self.x + value * other.x
        y = self.y + value * other.y
        return Vec2(x, y)
