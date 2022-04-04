

from collections import namedtuple
from operator import add, neg, sub
from typing import Any, overload


def superscipt(num: int):
    string = str(num)
    return string.translate(string.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))


class Quantity(namedtuple("Quantity", "value mass length time", defaults=(1, 0, 0, 0))):
    __slots__ = ()

    # def __init__(self, value=1, mass=0, length=0, time=0):...

    def __mul__(self, other):
        if isinstance(other, Quantity):
            return Quantity(self.value * other.value, *map(add, self[1:], other[1:]))
        else:
            return self._replace(value=self.value * other)

    def __rmul__(self, other):
        return self._replace(value=other * self.value)

    def __truediv__(self, other):
        if isinstance(other, Quantity):
            return Quantity(self.value / other.value, *map(sub, self[1:], other[1:]))
        else:
            return self._replace(value=self.value / other)

    def __rtruediv__(self, other):
        return Quantity(other / self.value, *map(neg, self[1:]))

    def is_same_dimension(self, other):
        if isinstance(other, Quantity):
            return self[1:] == other[1:]
        else:
            # return not any(self[1:])
            return False

    def assert_same_dimension(self, other):
        if not self.is_same_dimension(other):
            raise TypeError(f"dimension mismatch between quantities {self} and {other}" + ("\none of them is zero" if (self.value ==
                            0 or (other.value if isinstance(other, Quantity) else other) == 0) else ""))

    def __add__(self, other):
        self.assert_same_dimension(other)
        if isinstance(other, Quantity):
            return self._replace(value=self.value + other.value)
        else:
            return self._replace(value=self.value + other)

    def __radd__(self, other):
        self.assert_same_dimension(other)
        return self._replace(value=other + self.value)

    def __sub__(self, other):
        self.assert_same_dimension(other)
        if isinstance(other, Quantity):
            return self._replace(value=self.value - other.value)
        else:
            return self._replace(value=self.value - other)

    def __rsub__(self, other):
        self.assert_same_dimension(other)
        return self._replace(value=other - self.value)

    def __pow__(self, other: float):
        return Quantity(self.value**other, *map(lambda x: x * other, self[1:]))

    def __neg__(self):
        return self._replace(value=-self.value)

    def __pos__(self):
        return self

    def __str__(self):
        def func(value: float, unit: str):
            if value == 0:
                return ""
            elif value > 0:
                if value == 1:
                    return f"*{unit}"
                return f"*{unit}{superscipt(value)}"
            elif value < 0:
                if value == -1:
                    return f"/{unit}"
                return f"/{unit}{superscipt(-value)}"

        return "{} {}{}{}{}".format(self.find_dimension().__name__,
                                    self.value,
                                    func(self.mass, "m"),
                                    func(self.length, "l"),
                                    func(self.time, "t"))
        return f"{self.value} {self.mass}"

    def find_dimension(self):
        if type(self) != Quantity:
            return type(self)
        for sc in type(self).__subclasses__():
            if self.is_same_dimension(sc()):
                return sc

    @classmethod
    def is_dimension(cls, item):
        return cls()[1:] == item[1:]


# Mass = Quantity(mass=1)

# Time = Quantity(time=1)


class Mass(Quantity):
    "m"
    mass = 1

    def __new__(cls, value=1):
        return super().__new__(cls, value, mass=1)


class Length(Quantity):
    "l"
    length = 1

    def __new__(cls, value=1):
        return super().__new__(cls, value, length=1)


class Time(Quantity):
    "t"
    time = 1

    def __new__(cls, value=1):
        return super().__new__(cls, value, time=1)


class Unitless(Quantity):
    "1"
    def __new__(cls, value=1):
        return super().__new__(cls, value)


class Speed(Quantity):
    "l/t"
    length = 1
    time = -1

    def __new__(cls, value=1):
        return super().__new__(cls, value, length=1, time=-1)


class Acceleration(Quantity):
    "l/t²"
    length = 1
    time = -2

    def __new__(cls, value=1):
        return super().__new__(cls, value, length=1, time=-2)


class Force(Quantity):
    "m*l/t²"
    mass = 1
    length = 1
    time = -2

    def __new__(cls, value=1):
        return super().__new__(cls, value, mass=1, length=1, time=-2)


class Energy(Quantity):
    "m*l²/t²"
    mass = 1
    length = 2
    time = -2

    def __new__(cls, value=1):
        return super().__new__(cls, value, mass=1, length=2, time=-2)


class Power(Quantity):
    "m*l²/t³ energy over time, teho, watt"
    mass = 1
    length = 2
    time = -3

    def __new__(cls, value=1):
        return super().__new__(cls, value, mass=1, length=2, time=-3)


# A = Length(10)
# B = Time(1)
# D = Mass(10)
# print(D)
# C = (A / B)
# print(C)
# # print(A + B)
# print(Energy(1) / Mass(1))
