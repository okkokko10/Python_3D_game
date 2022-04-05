

from operator import add
from typing import Final, Generic, Literal, TypeVar, overload

_V = TypeVar("_V")

_m = TypeVar("_m")
_l = TypeVar("_l")
_t = TypeVar("_t")


class Quantity:
    value: float
    mass: int
    length: int
    time: int

    def __init__(self, value: float) -> None:
        self.value = value

    def __mul__(self, other: "Quantity"):
        # map(add, self.get_dimensions())
        return new_quantity(self.value * other.value, self.mass + other.mass, self.length + other.length, self. time + other. time)

    @classmethod
    def get_dimensions(cls):
        return cls.mass, cls.length, cls.time


class Mass(Quantity):
    mass: Final[int] = 1
    length: Final[int] = 0
    time: Final[int] = 0

    @classmethod
    def get_dimensions(cls):
        return 1, 0, 0
    ...


class Length(Quantity):
    mass: Final[int] = 0
    length: Final[int] = 1
    time: Final[int] = 0

    @classmethod
    def get_dimensions(cls):
        return 0, 1, 0
    ...


class Time(Quantity):
    mass: Final[int] = 0
    length: Final[int] = 0
    time: Final[int] = 1

    @classmethod
    def get_dimensions(cls):
        return 0, 0, 1
    ...


class Speed(Quantity):
    mass: Final[int] = 0
    length: Final[int] = 1
    time: Final[int] = -1

    @classmethod
    def get_dimensions(cls):
        return 0, 1, -1
    ...


class LengTime(Quantity):
    mass: Final[int] = 0
    length: Final[int] = 1
    time: Final[int] = 1

    @classmethod
    def get_dimensions(cls):
        return 0, 1, 1
    ...


# @overload
# def new_quantity(value: _V, mass: Literal[0], length: Literal[1], time: Literal[1]) -> LengTime:
#     ...


def new_quantity(value: _V, mass, length, time):
    if mass == 0 and length == 1 and time == 0:
        return LengTime(value)
    # match (mass, length, time):
    #     case (1, 0, 0):
    #         return Mass(value)
    #     case (0, 1, 0):
    #         return Length(value)
    #     case (0, 0, 1):
    #         return Time(value)
    #     case (0, 1, 1):
    #         return LengTime(value)
    return


# def ff(t):
#     return float


# def fff(t: ff(float)) -> ff(2):
#     pass


# b = new_quantity(1.1, 0, 1, 0)

# a = Length(1)
# e = Mass.get_dimensions()
# print(type(a).mass)

# @overload
# def foo(a: A[_T], b: A[_T1]) -> A[_T1]: ...
# @overload
# def foo(a: A[_T], b: B[_T1]) -> A[_T1]: ...
# @overload
# def foo(a: A[_T], b: C[_T1]) -> A[_T1]: ...


# @overload
# def foo(a: B[_T], b: A[_T1]) -> B[_T1]: ...
# @overload
# def foo(a: B[_T], b: B[_T1]) -> B[_T1]: ...
# @overload
# def foo(a: B[_T], b: C[_T1]) -> B[_T1]: ...


# @overload
# def foo(a: C[_T], b: A[_T1]) -> C[_T1]: ...
# @overload
# def foo(a: C[_T], b: B[_T1]) -> C[_T1]: ...
# @overload
# def foo(a: C[_T], b: C[_T1]) -> C[_T1]: ...


_T = TypeVar("_T")
_T1 = TypeVar("_T1")


class A(Generic[_T]):
    t: _T

    def __init__(self, t: _T) -> None:
        self.t = t


class B(A[_T]):
    ...


class C(A[_T]):
    ...


_A = TypeVar("_A", bound=A, covariant=True)


def foo(a: A[_T], b: A[_T1]) -> A[_T1]:
    return type(a)(b.t)


a = B(1)
b = C(1.1)
c = foo(a, b)
d = type(a)(b.t)
