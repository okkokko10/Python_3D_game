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
        return Vector(*(a.__add__(b) for a, b in zip(self, other)))

    # def __sub__(self, other):
    #     return Vector(
    #         self.x.__sub__(other.x),
    #         self.y.__sub__(other.y)
    #     )

    def __sub__(self, other):
        return Vector(*(a.__sub__(b) for a, b in zip(self, other)))

    def __mul__(self, other):
        if isinstance(other, Vector):
            return Vector(*(a.__mul__(b) for a, b in zip(self, other)))
        else:
            return Vector(*(a.__mul__(other) for a in self))

    def __rmul__(self, other):
        if isinstance(other, Vector):
            return Vector(*(a.__rmul__(b) for a, b in zip(self, other)))
        else:
            return Vector(*(a.__rmul__(other) for a in self))

    def __truediv__(self, other):
        return Vector(*(a.__truediv__(other) for a in self))

    def __le__(self, other):
        return Vector(*(a.__le__(b) for a, b in zip(self, other)))

    def __lt__(self, other):
        return Vector(*(a.__lt__(b) for a, b in zip(self, other)))

    def __ge__(self, other):
        return Vector(*(a.__ge__(b) for a, b in zip(self, other)))

    def __gt__(self, other):
        return Vector(*(a.__gt__(b) for a, b in zip(self, other)))

    def __neg__(self):
        return Vector(*(a.__neg__() for a in self))

    def __pos__(self):
        return Vector(*(a.__pos__() for a in self))

    def __floor__(self):
        return Vector(*(a.__floor__() for a in self))

    def __int__(self):
        return Vector(*(a.__int__() for a in self))

    def __str__(self):
        return 'V({})'.format(' '.join(a.__str__() for a in self))

    def lengthSq(self) -> float:
        return sum(k**2 for k in self)

    def length(self) -> float: return math.sqrt(self.lengthSq())
    def dotProduct(self, other: 'Vector') -> float: return sum(self * other)

    def project(self, other: 'Vector') -> 'Vector':
        return self.dotProduct(other) / self.lengthSq() * self

    def projectScalar(self, other: 'Vector') -> float:
        return self.dotProduct(other) / self.length()

    def projectScalarSq(self, other: 'Vector') -> float:
        return self.dotProduct(other)**2 / self.lengthSq()

    def complexMul(self, other: 'Vector'):
        return Vector(self.x * other.x - self.y * other.y, self.x * other.y + self.y * other.x)

    def complexConjugate(self):
        return Vector(self.x, -self.y)

    def reflect(self, other: 'Vector'):
        "other reflected by self"
        return self.complexMul(self).complexMul(other.complexConjugate()) / self.lengthSq()

    @property
    def f(self): return int(self.x), int(self.y)

    def unit(self):
        return self / (self.length() or 1)

    def round(self, size: 'Vector') -> 'Vector':

        return Vector(*((self[k] // size[k] * size[k]) for k in self.keys()))

    def normal(self):
        "a vector perpendicular to this one"
        return Vector(-self.y, self.x)
