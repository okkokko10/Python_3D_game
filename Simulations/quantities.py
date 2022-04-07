"""a module for physical quantities made up of mass, length and time.\n
call either enable_CHECK() or disable_CHECK() to set the value of CHECK before initializing any quantities. 
 Do not change the value after initializing quantities\n
initialize a quantity by calling a subclass of quantity with a value (leave value empty for 1.0), or call Quantity(value=1.0,mass=0,length=0,time=0)\n
multiplication, division, addition and subtraction are defined for quantities, and will be applied to the held values.\n
if CHECK is True, quantities will keep track of their quantity dimensions, and raise an error if an incorrect operation 
(addition of values with different quantity dimensions, such as speed plus mass) occurs.
 It's basically type checking.\n
if CHECK is False, Quantity(x) and its subclasses will return x instead of a Quantity object\n
use get_value(quantity) to get the value stored in the quantity\n
use cast(value,quantity) to get a new quantity with a value of value and same quantity dimensions as quantity

quantities are generic. Quantity(1.0) is of the type Quantity[float]\n
Mass(2) * Time(2.0) is annotated times[Mass[int],Time[float]] but is internally Quantity(4.0,1,0,1)
Mass(2) / Time(2.0) is annotated times[Mass[int],inverse[Time[float]]] but is internally Quantity(1.0,1,0,-1)
"""

from collections import namedtuple
from itertools import chain
from operator import add, neg, sub
from typing import TYPE_CHECKING, Any, Final, Generic, Literal, Type, TypeGuard, TypeVar, overload
from typing_extensions import Self


def superscipt(num: int):
    string = str(num)
    return string.translate(string.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))


_V = TypeVar("_V")
_V1 = TypeVar("_V1")


class Quantity(namedtuple("Quantity", "value mass length time", defaults=(1., 0, 0, 0)), Generic[_V]):
    __slots__ = ()
    value: _V
    mass: int
    length: int
    time: int

    # @overload
    # def __new__(cls: type["_Q"], value: _V, mass: Literal[0], length: Literal[1], time: Literal[-1]) -> "Speed[_V]":
    #     return super().__new__(cls, value, mass=mass, length=length, time=time)

    def __new__(cls: type["_Q"], value: _V = 1., mass=0, length=0, time=0) -> "_Q":
        return super().__new__(cls, value, mass=mass, length=length, time=time)

    # def __init__(self, value=1, mass=0, length=0, time=0):...
    @overload
    def __mul__(self: "_Q1", other: "Unitless") -> "_Q1": ...
    @overload
    def __mul__(self: "Unitless", other: "_Q1") -> "_Q1": ...
    @overload
    def __mul__(self: "inverse[_Q1]", other: "_Q1") -> "Unitless": ...
    @overload
    def __mul__(self: "_Q1", other: "inverse[_Q1]") -> "Unitless": ...

    @overload
    def __mul__(self: "times[_Q1,_Q2]", other: "inverse[_Q1]") -> "_Q2": ...
    @overload
    def __mul__(self: "times[_Q1,_Q2]", other: "inverse[_Q2]") -> "_Q1": ...
    @overload
    def __mul__(self: "inverse[_Q1]", other: "times[_Q1,_Q2]") -> "_Q2": ...
    @overload
    def __mul__(self: "inverse[_Q2]", other: "times[_Q1,_Q2]") -> "_Q1": ...

    # @overload
    # def __mul__(self: "times[_Q3,times[_Q1,_Q2]]", other: "_Q4"):
    #     return _times(self.first, self.second * other)

    @overload
    def __mul__(self: "times[_Q2,_Q3]", other: "_Q1"):
        return self.first * (self.second * other)

    @overload
    def __mul__(self: "_Q1", other: "_Q2") -> "times[_Q1,_Q2]": ...
    @overload
    def __mul__(self, other: "TypeError") -> "TypeError": ...
    @overload
    def __mul__(self, other: "Any") -> "Self": ...

    def __mul__(self, other):
        if isinstance(other, Quantity):
            return Quantity(self.value * other.value, *map(add, self[1:], other[1:]))
        else:
            return self._replace(value=self.value * other)

    def __rmul__(self, other):
        return self._replace(value=other * self.value)

    # @overload
    # def __truediv__(self: "Length", other: "Time") -> "Speed": ...
    @overload
    def __truediv__(self: "_Q1", other: "_Q1") -> "Unitless": ...
    @overload
    def __truediv__(self: "_Q1", other: "Unitless") -> "_Q1": ...
    @overload
    def __truediv__(self: "times[_Q1,_Q2]", other: "_Q2") -> "_Q1": ...
    @overload
    def __truediv__(self: "times[_Q1,_Q2]", other: "_Q1") -> "_Q2": ...

    @overload
    def __truediv__(self: "_Q1", other: "_Q2"):
        return self * other._inverse()

    @overload
    def __truediv__(self: "_Q1", other: "Any") -> "_Q1": ...

    def __truediv__(self, other):
        if isinstance(other, Quantity):
            return Quantity(self.value / other.value, *map(sub, self[1:], other[1:]))
        else:
            return self._replace(value=self.value / other)

    def __rtruediv__(self, other):
        return Quantity(other / self.value, *map(neg, self[1:]))

    def _is_same_dimension(self, other) -> TypeGuard[Self]:
        if isinstance(other, Quantity):
            return self[1:] == other[1:]
        else:
            # return not any(self[1:])
            return False

    def _assert_same_dimension(self, other):
        if not self._is_same_dimension(other):
            raise TypeError(f"dimension mismatch between quantities {self} and {other}")
            #  + ("\none of them is zero" if (self.value ==
            #                 0 or (other.value if isinstance(other, Quantity) else other) == 0) else ""))

    @overload
    def __add__(self, other: Self) -> Self: ...
    @overload
    def __add__(self, other) -> TypeError: ...

    def __add__(self, other):
        self._assert_same_dimension(other)
        if isinstance(other, Quantity):
            return self._replace(value=self.value + other.value)
        else:
            return self._replace(value=self.value + other)

    def __radd__(self, other):
        if other == 0:  # sum default
            return self
        self._assert_same_dimension(other)
        return self._replace(value=other + self.value)

    @overload
    def __sub__(self: "_Q1", other: "_Q1") -> "_Q1": ...
    @overload
    def __sub__(self, other) -> TypeError: ...
    @overload
    def __sub__(self: Self, other) -> Self: ...

    def __sub__(self, other):
        self._assert_same_dimension(other)
        if isinstance(other, Quantity):
            return self._replace(value=self.value - other.value)
        else:
            return self._replace(value=self.value - other)

    def __rsub__(self, other):
        self._assert_same_dimension(other)
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

        return "{} {}{}{}{}".format(self._find_dimension().__name__,
                                    self.value,
                                    func(self.mass, "m"),
                                    func(self.length, "l"),
                                    func(self.time, "t"))
        return f"{self.value} {self.mass}"

    def _find_dimension(self):
        if type(self) != Quantity:
            return type(self)
        for sc in type(self).__subclasses__():
            # if not issubclass(sc, _operation):
            if sc._is_dimension(self):
                return sc
        return Quantity

    @classmethod
    def _is_dimension(cls, quantity):
        return cls()[1:] == quantity[1:]

    @overload
    def _cast(self: Self, value: _V1):
        return type(self)(value)

    def _cast(self, value: _V1) -> "Quantity[_V1]":
        "returns a quantity with same dimensions as self and value as value"
        # typehint is meant to say -> Self[_V1]
        return self._replace(value=value)

    def _inverse(self: "_Q1") -> "inverse[_Q1]":
        "for type checking."
        ...


_Q = TypeVar("_Q", bound=Quantity)
_Q1 = TypeVar("_Q1", bound=Quantity)
_Q2 = TypeVar("_Q2", bound=Quantity)
_Q3 = TypeVar("_Q3", bound=Quantity)
_Q4 = TypeVar("_Q4", bound=Quantity)


def _checking_get_value(quantity: Quantity[_V]) -> _V:
    return quantity.value


def _checking_cast(value: _V, quantity: _Q1):
    return quantity._cast(value)


def _not_checking_get_value(quantity: Quantity):
    return quantity


def _not_checking_cast(value: _V, quantity: _Q1) -> _Q1:
    return value


CHECK: bool = True
"""are quantities being checked?\n
get only. use set_CHECK(True), set_CHECK(False), enable_CHECK() or disable_CHECK() to set\n
Note that changing the value is not retroactive, so quantities initialized before
and quantities initialized after are most likely going to be incompatible. 
"""


def is_check():
    "returns CHECK"
    return CHECK


def set_CHECK(value: bool):
    if value:
        enable_CHECK()
    else:
        disable_CHECK()


if TYPE_CHECKING:
    def get_value(quantity: Quantity[_V]) -> _V: ...

    def cast(value: _V, quantity: _Q1) -> _Q1: ...


def _update_check(check: bool):
    global get_value
    global cast
    if check:
        get_value = _checking_get_value
        cast = _checking_cast
    else:
        get_value = _not_checking_get_value
        cast = _not_checking_cast


def disable_CHECK():
    global CHECK
    if not CHECK:
        return
    for c in Quantity.__subclasses__():
        c._old_new = c.__new__
        c.__new__ = lambda x, y=1.0: y
    Quantity._old_new = Quantity.__new__
    Quantity.__new__ = lambda x, y=1.0, *args, **kwargs: y
    CHECK = False
    _update_check(False)


def enable_CHECK():
    global CHECK
    if CHECK:
        return
    for c in Quantity.__subclasses__():
        c.__new__ = c._old_new
    Quantity.__new__ = Quantity._old_new
    _update_check(True)


_update_check(CHECK)


class _operation:
    "is an operation for typing and not an actual quantity"
    ...


class times(Quantity, Generic[_Q1, _Q2], _operation):
    first: _Q1
    second: _Q2

    def _inverse(self):
        return _times(self.first._inverse(), self.second._inverse())

    @classmethod
    def _is_dimension(cls, quantity):
        return False
        # return cls()[1:] == quantity[1:]

    def __new__(cls):
        raise TypeError("times is meant for typing")


def _times(a: _Q1, b: _Q2) -> times[_Q1, _Q2]: ...


class inverse(Quantity, Generic[_Q1], _operation):
    reciprocal: _Q1

    def _inverse(self):
        "for type checking."
        return self.reciprocal

    @classmethod
    def _is_dimension(cls, quantity):
        return False

    def __new__(cls):
        raise TypeError("inverse is meant for typing")


def _invert(q: _Q1):
    return q._inverse()

# Mass = Quantity(mass=1)

# Time = Quantity(time=1)


class Mass(Quantity[_V]):
    "m"
    mass = 1
    length = 0
    time = 0

    def __new__(cls, value: _V = 1.):
        return super().__new__(cls, value, mass=1)


class Length(Quantity[_V]):
    "l"
    mass = 0
    length = 1
    time = 0

    def __new__(cls, value: _V = 1.):
        return super().__new__(cls, value, length=1)


class Time(Quantity[_V]):
    "t"
    mass = 0
    length = 0
    time = 1

    def __new__(cls, value: _V = 1.):
        return super().__new__(cls, value, time=1)


class Unitless(Quantity[_V]):
    "1"
    mass = 0
    length = 0
    time = 0

    def __new__(cls, value: _V = 1.):
        return super().__new__(cls, value)

    def inverse(self: _Q1) -> _Q1: ...


class Speed(Quantity[_V]):
    "l/t"
    mass = 0
    length = 1
    time = -1

    def __new__(cls, value: _V = 1.):
        return super().__new__(cls, value, length=1, time=-1)


class Acceleration(Quantity[_V]):
    "l/t²"
    mass = 0
    length = 1
    time = -2

    def __new__(cls, value: _V = 1.):
        return super().__new__(cls, value, length=1, time=-2)


class Force(Quantity[_V]):
    "m*l/t²"
    mass = 1
    length = 1
    time = -2

    def __new__(cls, value: _V = 1.):
        return super().__new__(cls, value, mass=1, length=1, time=-2)


class Energy(Quantity[_V]):
    "m*l²/t²"
    mass = 1
    length = 2
    time = -2

    def __new__(cls, value: _V = 1.):
        return super().__new__(cls, value, mass=1, length=2, time=-2)


class Power(Quantity[_V]):
    "m*l²/t³ energy over time, teho, watt"
    mass = 1
    length = 2
    time = -3

    def __new__(cls, value: _V = 1.):
        return super().__new__(cls, value, mass=1, length=2, time=-3)


class Momentum(Quantity[_V]):
    "m*l/t Force times Time"
    mass = 1
    length = 1
    time = -1

    def __new__(cls, value: _V = 1.):
        return super().__new__(cls, value, mass=1, length=1, time=-1)


disable_CHECK()
if __name__ == "__main__":
    disable_CHECK()
    a = Length() * Mass() / Time() / Mass()
    c = Length() * Mass()  # 1 2
    c = Length() * Mass() * Time()  # 1 2 3
    c = Length() * Mass() * Time() * Power()  # 1 2 4 3
    c = Length() * Mass() * Time() * Power() * Speed()  # 1 2 4 5 3
    c = Length() * Mass() * Time() * Power() * Length()
    c = Length() * Mass() * Time() * Power() / Length()  # this should be identical to the one above, but it isn't.
    c = Length() * Mass() / Length()
    d = Length() * Mass() * Time() * Power()
    e = d / Mass()
    e = d * Mass()
    print(e)
    # print(e)
    # print(Length(1))
    # a = Quantity(0)
    # print(Quantity(0))
    # print(times[Speed, Time].is_dimension(Length()))
    # print(gener[float].__origin__)
    # print(type(gener[float]))
    # gener[float].a()
    # gener[float].b(gener[float])
    # print(times[Speed, Time](a, e))
