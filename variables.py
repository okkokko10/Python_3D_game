# TODO: if you can't move something a certain way, it won't do anything

from typing import Callable, Generic, TypeVar
_VT = TypeVar('_VT')
_A = TypeVar('_A')


class Variable(Generic[_VT]):
    def __init__(self, value: _VT, name=""):
        self._value = value
        self.name = name

    def Set(self, value: _VT):
        self._value = value

    def Get(self) -> _VT:
        return self._value

    @property
    def value(self):
        return self.Get()

    @value.setter
    def value(self, value: _VT):
        self.Set(value)


class VariableMap(Variable[_VT], Generic[_VT]):
    def __init__(self, *variables: _A, getter: Callable[[_A], _VT], setter: Callable[[_VT, _A], None] = None, name=""):
        """getter is a function that takes variables as input (in unpacked form), and outputs the return value of Get()
        setter ís a function that takes as input the input value of Set(), and  then variables
        name does nothing except make things more clear
        It is currently impossible to typehint Callables with arbitrarily many arguments, TypeVarTuple is coming out in Python 3.11"""
        self.variables = variables
        self.name = name
        self.getter = getter
        self.setter = setter

    def Set(self, value: _VT):
        if self.setter is None:
            raise TypeError(f"{self}{' named ' if self.name else ''}{self.name} is read-only")
        self.setter(value, *self.variables)

    def Get(self) -> _VT:
        return self.getter(*self.variables)


class VariableHolder(Variable[_VT], Generic[_VT]):
    def __init__(self, variable: Variable[_VT] = None, name="", parent=None):
        self.variable = variable
        self.parent = parent

    def SetVariable(self, variable: Variable[_VT]):
        if self.variable is not None:
            pass
        self.variable = variable

    def Set(self, value: _VT):
        self.variable.Set(value)

    def Get(self):
        return self.variable.Get()

    @property
    def value(self):
        return self.Get()

    @value.setter
    def value(self, value: _VT):
        self.Set(value)

    def Deattach(self):
        "deattaches the held variable. The new held variable is a new variable that has the same value as the old one had when deattaching"
        self.SetVariable(Variable(self.Get()))
