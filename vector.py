import math


class Vector:
    def __init__(self, x: float = 0, y: float = 0):
        self._x = float(x)
        self._y = float(y)

    @property
    def x(self) -> float: return self._x
    @x.setter
    def x(self, value: float): self._x = value
    @property
    def y(self) -> float: return self._y
    @y.setter
    def y(self, value: float): self._y = value

    def __getitem__(self, i) -> float:
        return self.y if i else self.x

    def __setitem__(self, i, value: float):
        if i:
            self.y = value
        else:
            self.x = value

    def __iter__(self):
        yield self.x
        yield self.y

    def keys(self):
        return (0, 1)

    def __add__(self, other):
        return Vector(*(self[k].__add__(other[k]) for k in self.keys()))

    # def __sub__(self, other):
    #     return Vector(
    #         self.x.__sub__(other.x),
    #         self.y.__sub__(other.y)
    #     )

    def __sub__(self, other):
        return Vector(*(self[k].__sub__(other[k]) for k in self.keys()))

    def __mul__(self, other):
        if isinstance(other, Vector):
            return Vector(*(self[k].__mul__(other[k]) for k in self.keys()))
        else:
            return Vector(*(self[k].__mul__(other) for k in self.keys()))

    def __rmul__(self, other):
        if isinstance(other, Vector):
            return Vector(*(self[k].__rmul__(other[k]) for k in self.keys()))
        else:
            return Vector(*(self[k].__rmul__(other) for k in self.keys()))

    def __truediv__(self, other):
        return Vector(*(self[k].__truediv__(other) for k in self.keys()))

    def __le__(self, other):
        return Vector(*(self[k].__le__(other[k]) for k in self.keys()))

    def __lt__(self, other):
        return Vector(*(self[k].__lt__(other[k]) for k in self.keys()))

    def __ge__(self, other):
        return Vector(*(self[k].__ge__(other[k]) for k in self.keys()))

    def __gt__(self, other):
        return Vector(*(self[k].__gt__(other[k]) for k in self.keys()))

    def __neg__(self):
        return Vector(*(self[k].__neg__() for k in self.keys()))

    def __pos__(self):
        return Vector(*(self[k].__pos__() for k in self.keys()))

    def __floor__(self):
        return Vector(*(self[k].__floor__() for k in self.keys()))

    def __int__(self):
        return Vector(*(self[k].__int__() for k in self.keys()))

    def __str__(self):
        return ' '.join(self[k].__str__() for k in self.keys())

    def lengthSq(self):
        return sum(self[k]**2 for k in self.keys())

    def length(self): return math.sqrt(self.lengthSq())
    def dotProduct(self, other: 'Vector'): return sum(self * other)

    def project(self, other: 'Vector'):
        return self.dotProduct(other) / self.lengthSq() * self

    def projectScalar(self, other: 'Vector'):
        return self.dotProduct(other) / self.length()

    def complexMul(self, other: 'Vector'):
        return Vector(self.x * other.x - self.y * other.y, self.x * other.y + self.y * other.x)

    def complexConjugate(self):
        return Vector(self.x, -self.y)

    def reflect(self, other: 'Vector'):
        "other reflected by self"
        return self.complexMul(self).complexMul(other.complexConjugate()) / self.lengthSq()

    @property
    def f(self): return int(self.x), int(self.y)
