class Vec2(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __repr__(self):
        return f'({self.x}, {self.y})'

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


def binary_search_frame_index(frames, target):
    n = len(frames)
    low = 0
    high = n - 1
    mid = 0

    if target >= frames[n - 1]:
        return n - 1

    if target <= frames[0]:
        return 0

    while low < high:
        mid = (low + high) // 2
        if target < frames[mid]:
            high = mid
        elif target > frames[mid]:
            low = mid + 1
        else:
            return mid

    if target < frames[mid]:
        return mid
    else:
        return mid + 1
