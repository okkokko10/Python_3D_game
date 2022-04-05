

from collections import namedtuple
from operator import add, neg, sub
from typing import Any, Generic, Literal, Type, TypeVar, overload
from typing_extensions import Self


def superscipt(num: int):
    string = str(num)
    return string.translate(string.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))


_V = TypeVar("_V")
_V1 = TypeVar("_V1")


class Quantity(namedtuple("Quantity", "value mass length time", defaults=(1, 0, 0, 0)), Generic[_V]):
    __slots__ = ()
    value: _V
    mass: float
    length: float
    time: float

    def __new__(cls: type["_Q"], value: _V = 1, mass=0, length=0, time=0) -> "_Q":
        return super().__new__(cls, value, mass=mass, length=length, time=time)

    # def __init__(self, value=1, mass=0, length=0, time=0):...
    @overload
    def __mul__(self: "over[_Q1,_Q2]", other: "_Q2") -> "_Q1": ...
    @overload
    def __mul__(self: "over[_Q1,_Q2]", other: "_Q3") -> "over[times[_Q1,_Q3],_Q2]": ...
    @overload
    def __mul__(self, other: "_Q1") -> "times[Self,_Q1]": ...
    @overload
    def __mul__(self, other: "Any") -> "Self": ...

    def __mul__(self, other):
        if isinstance(other, Quantity):
            return Quantity(self.value * other.value, *map(add, self[1:], other[1:]))
        else:
            return self._replace(value=self.value * other)

    def __rmul__(self, other):
        return self._replace(value=other * self.value)

    @overload
    def __truediv__(self: "times[_Q1,_Q2]", other: "_Q2") -> "_Q1": ...
    @overload
    def __truediv__(self: "times[_Q1,_Q2]", other: "_Q1") -> "_Q2": ...
    @overload
    def __truediv__(self, other: "_Q1") -> "over[Self,_Q1]": ...
    @overload
    def __truediv__(self, other: "Any") -> "Self": ...

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
            raise TypeError(f"dimension mismatch between quantities {self} and {other}")
            #  + ("\none of them is zero" if (self.value ==
            #                 0 or (other.value if isinstance(other, Quantity) else other) == 0) else ""))

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
        return Quantity

    @classmethod
    def is_dimension(cls, item):
        return cls()[1:] == item[1:]

    @overload
    def cast(self: Self, value: _V1):
        return type(self)(value)

    def cast(self, value: _V1) -> "Quantity[_V1]":
        "returns a quantity with same dimensions as self and value as value"
        # typehint is meant to say -> Self[_V1]
        return self._replace(value=value)


_Q = TypeVar("_Q", bound=Quantity)
_Q1 = TypeVar("_Q1", bound=Quantity)
_Q2 = TypeVar("_Q2", bound=Quantity)
_Q3 = TypeVar("_Q3", bound=Quantity)


"change the boolean in the if statement to enable/disable checks"
if True:
    CHECK = True

    def get_value(quantity: Quantity):
        return quantity.value

    def cast(value: _V, fromtype: _Q1):
        return fromtype.cast(value)
else:
    CHECK = False

    class Quantity(Generic[_V]):
        def __new__(cls: type[Self], value: _V, *args, **kwargs) -> "Self[_V]":
            return value

    def get_value(quantity: Quantity):
        return quantity

    def cast(value: _V, fromtype: _Q1) -> _Q1:
        return value


class over(Quantity, Generic[_Q1, _Q2, _V]):
    ...


class times(Quantity, Generic[_Q1, _Q2, _V]):
    ...


# Mass = Quantity(mass=1)

# Time = Quantity(time=1)


class Mass(Quantity[_V]):
    "m"
    mass = 1

    def __new__(cls, value: _V = 1):
        return super().__new__(cls, value, mass=1)


class Length(Quantity[_V]):
    "l"
    length = 1

    def __new__(cls, value: _V = 1):
        return super().__new__(cls, value, length=1)


class Time(Quantity[_V]):
    "t"
    time = 1

    def __new__(cls, value: _V = 1):
        return super().__new__(cls, value, time=1)


class Unitless(Quantity[_V]):
    "1"
    def __new__(cls, value: _V = 1):
        return super().__new__(cls, value)


class Speed(Quantity[_V]):
    "l/t"
    length = 1
    time = -1

    def __new__(cls, value: _V = 1):
        return super().__new__(cls, value, length=1, time=-1)


class Acceleration(Quantity[_V]):
    "l/t²"
    length = 1
    time = -2

    def __new__(cls, value: _V = 1):
        return super().__new__(cls, value, length=1, time=-2)


class Force(Quantity[_V]):
    "m*l/t²"
    mass = 1
    length = 1
    time = -2

    def __new__(cls, value: _V = 1):
        return super().__new__(cls, value, mass=1, length=1, time=-2)


class Energy(Quantity[_V]):
    "m*l²/t²"
    mass = 1
    length = 2
    time = -2

    def __new__(cls, value: _V = 1):
        return super().__new__(cls, value, mass=1, length=2, time=-2)


class Power(Quantity[_V]):
    "m*l²/t³ energy over time, teho, watt"
    mass = 1
    length = 2
    time = -3

    def __new__(cls, value: _V = 1):
        return super().__new__(cls, value, mass=1, length=2, time=-3)


class Momentum(Quantity[_V]):
    "m*l/t Force times Time"
    mass = 1
    length = 1
    time = -1

    def __new__(cls, value: _V = 1):
        return super().__new__(cls, value, mass=1, length=1, time=-1)
