import math
from typing import Iterable

# TODO: Merge IntVec and Vector, stop the automatic float() and int() there


class Vector:
    def __init__(self, x: float = 0, y: float = 0):
        self._x = (x)
        self._y = (y)

    @property
    def x(self): return self._x
    @x.setter
    def x(self, value: float): self._x = value
    @property
    def y(self): return self._y
    @y.setter
    def y(self, value: float): self._y = value

    def __getitem__(self, i):
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
        return self.__class__(*(a + (b) for a, b in zip(self, other)))

    # def __sub__(self, other):
    #     return Vector(
    #         self.x.__sub__(other.x),
    #         self.y.__sub__(other.y)
    #     )

    def __sub__(self, other):
        return self.__class__(*(a - (b) for a, b in zip(self, other)))

    def __mul__(self, other):
        if isinstance(other, Vector):
            return self.__class__(*(a * (b) for a, b in zip(self, other)))
        else:
            return self.__class__(*(a * (other) for a in self))

    def __rmul__(self, other):
        if isinstance(other, Vector):
            return self.__class__(*(b * a for a, b in zip(self, other)))
        else:
            return self.__class__(*(other * a for a in self))

    def __truediv__(self, other):
        return self.__class__(*(a / (other) for a in self))

    def __le__(self, other):
        return self.__class__(*(a.__le__(b) for a, b in zip(self, other)))

    def __lt__(self, other):
        return self.__class__(*(a.__lt__(b) for a, b in zip(self, other)))

    def __ge__(self, other):
        return self.__class__(*(a.__ge__(b) for a, b in zip(self, other)))

    def __gt__(self, other):
        return self.__class__(*(a.__gt__(b) for a, b in zip(self, other)))

    def __neg__(self):
        return self.__class__(*(a.__neg__() for a in self))

    def __pos__(self):
        return self.__class__(*(a.__pos__() for a in self))

    def __floor__(self):
        return self.__class__(*(a.__floor__() for a in self))

    def __int__(self):
        return self.__class__(*(a.__int__() for a in self))
        # return IntVec(*self)

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
        return self.__class__(self.x * other.x - self.y * other.y, self.x * other.y + self.y * other.x)

    def complexConjugate(self):
        return self.__class__(self.x, -self.y)

    def reflect(self, other: 'Vector'):
        "other reflected by self"
        return self.complexMul(self).complexMul(other.complexConjugate()) / self.lengthSq()

    @property
    def f(self): return int(self.x), int(self.y)

    def unit(self):
        return self / (self.length() or 1)

    def round(self, size: 'Vector', offset=(0, 0)) -> 'Vector':
        "always rounds down"
        return self.__class__(*(((k - o) // s * s + o) for k, s, o in zip(self, size, offset)))

    def normal(self):
        "a vector perpendicular to this one"
        return self.__class__(-self.y, self.x)

    def __eq__(self, other) -> bool:
        return all(a == b for a, b in zip(self, other))

    def __floordiv__(self, other):
        return self.__class__(*(a // (other) for a in self))

    def roundClosest(self, size: 'Vector') -> 'Vector':
        "alligns to the grid's center"
        return (self + size / 2).round(size)

    def __hash__(self):
        return tuple(self).__hash__()

    @classmethod
    @property
    def ONE(cls):
        return cls(1, 1)

    @classmethod
    def Rotation(cls, circuits):
        "in whole turns"
        r = circuits * math.pi * 2
        return cls(math.cos(r), math.sin(r))

    def complexDiv(self, other: 'Vector'):
        "self / other"
        self.complexMul(other.complexConjugate()) / other.lengthSq()


class IntVec(Vector):
    def __init__(self, x=0, y=0):
        "initialization also accepts Vectors"
        if isinstance(x, Iterable):
            x, y = x
        self._x = (x)
        self._y = (y)

    def __str__(self):
        return 'iV({})'.format(' '.join(a.__str__() for a in self))
