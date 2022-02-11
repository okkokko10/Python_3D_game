# TODO: if you can't move something a certain way, it won't do anything

import math
from typing import Any, Callable, Iterable, Generic, TypeVar
import sympy
import screenIO
import pygame
from vector import Vector
import renderText
_VT = TypeVar('_VT')
_A = TypeVar('_A')


class Color(tuple):
    def __new__(cls, *args):
        return tuple.__new__(cls, args)
    pass


class Attribute(Generic[_VT]):
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


class AttributeMap(Attribute[_VT], Generic[_VT]):
    def __init__(self, *attributes: _A, getter: Callable[[_A], _VT], setter: Callable[[_A, _VT], None] = None, name=""):
        self.attributes = attributes
        self.name = name
        self.getter = getter
        self.setter = setter

    def Set(self, value: _VT):
        if self.setter is None:
            raise TypeError(f"{self}{' named ' if self.name else ''}{self.name} is read-only")
        self.setter(*self.attributes, value)

    def Get(self) -> _VT:
        return self.getter(*self.attributes)


class AttributeHolder(Attribute[_VT], Generic[_VT]):
    def __init__(self, attribute: Attribute[_VT] = None, name=""):
        self.attribute = attribute

    def SetAttribute(self, attribute: Attribute[_VT]):
        if self.attribute is not None:
            pass
        self.attribute = attribute

    def Set(self, value: _VT):
        self.attribute.Set(value)

    def Get(self):
        return self.attribute.Get()

    @property
    def value(self):
        return self.Get()

    @value.setter
    def value(self, value: _VT):
        self.Set(value)


class AttributeSet(Generic[_VT]):
    def __init__(self):
        self.attributes: set[Attribute[_VT]] = set()
        pass

    def Add(self, *attributes: Attribute):
        self.attributes.update(attributes)

    def Remove(self, *attributes: Attribute):
        self.attributes.difference_update(attributes)

    def Iterate(self):
        return self.attributes

# class AttributeList:
#     def __init__(self, parent, attributes: dict[Any, Any]) -> None:
#         self.parent = parent
#         self.attributes = dict((k, Attribute(self, v)) for k, v in attributes.items())


class Shape:
    def Draw(self, canvas: screenIO.Canvas):
        pass

    def get_equations(self, x, y) -> Iterable[sympy.Equality]:
        return ()
    pass


class Circle(Shape):
    def __init__(self, center: Attribute[Vector], edge: Attribute[Vector]):
        self.center = AttributeHolder(center, "center")
        self.edge = AttributeHolder(edge, "edge")

    @property
    def radiusSq(self):
        return (self.edge.Get() - self.center.Get()).lengthSq()

    @property
    def radius(self):
        return math.sqrt(self.radiusSq)

    def Draw(self, canvas: screenIO.Canvas):
        color = (255, 255, 255)
        canvas.Circle(self.center.Get(), self.radius, color, 1)

    def get_equations(self, x, y) -> Iterable[sympy.Equality]:
        cx, cy = self.center.Get()
        return sympy.Eq((x - cx)**2 + (y - cy)**2, self.radiusSq),


class Line(Shape):
    def __init__(self, a: Attribute[Vector], b: Attribute[Vector]):
        self.a = AttributeHolder(a)
        self.b = AttributeHolder(b)

    def Draw(self, canvas: screenIO.Canvas):
        color = (255, 255, 255)
        canvas.Line(self.a.Get(), self.b.Get(), color, 1)
        pass

    def get_equations(self, x, y) -> Iterable[sympy.Equality]:
        # return sympy.Eq((x - self.center.x)**2 + (y - self.center.y)**2, self.radius**2),
        ax, ay = self.a.Get()
        bx, by = self.b.Get()
        return sympy.Eq((x - bx) * (ay - by), (y - by) * (ax - bx)),


class GameObject:
    "editable by Editor"

    def Draw(self, canvas: screenIO.Canvas):
        pass

    def Glow(self, canvas: screenIO.Canvas, color: Attribute[Color]):
        pass

    def DistanceSq(self, pos: Attribute[Vector]) -> float:
        raise NotImplementedError()

    def get_editable(self) -> list[AttributeHolder]:
        return []


class GameObjectList:
    def __init__(self):
        self.gameObjects: set[GameObject] = set()

    def Add(self, *gameObjects: GameObject):
        self.gameObjects.update(gameObjects)

    def Remove(self, *gameObjects: GameObject):
        self.gameObjects.difference_update(gameObjects)

    def Draw(self, canvas: screenIO.Canvas):
        for go in self.gameObjects:
            go.Draw(canvas)

    def Iterator(self):
        return self.gameObjects


class Point(GameObject):
    def __init__(self, pos: Attribute[Vector]):
        self.position = AttributeHolder(pos)
        self.color = AttributeHolder(Attribute(Color(255, 0, 100)))

    def Draw(self, canvas: screenIO.Canvas):
        canvas.Circle(self.position.Get(), 2, self.color.Get())

    def Glow(self, canvas: screenIO.Canvas, color: Attribute[Color]):
        canvas.Circle(self.position.Get(), 3, color.Get(), 1)

    def DistanceSq(self, pos: Attribute[Vector]) -> float:
        return (self.position.Get() - pos.Get()).lengthSq()

    def get_editable(self) -> list[AttributeHolder]:
        return [self.position]


class Editor:
    def __init__(self):
        self.selected: list[GameObject] = []
        self.hold = AttributeHolder(Attribute(False))
        self.color = AttributeHolder(Attribute((100, 255, 100)))
        self.picker_position = AttributeHolder(Attribute(Vector(0, 0)))
        self.max_pick_range = AttributeHolder(Attribute(50))
        self.mode = AttributeHolder(Attribute(0))
        # TODO: create, destroy,
        "0: pick, 1: move, 2: rotate around pivot, 3: scale around pivot, 4: rotate/scale around pivot, 5: stretch normal to two pivots, 6: link selected attributes"
        self.pivot_max_amount = AttributeHolder(
            AttributeMap(
                self.mode,
                getter=lambda mode: [0, 0, 1, 1, 1, 2, 0][mode.value],
                setter=None,
                name="pivot max count"
            ))
        # defining an AttributeMap for a list that discards all but the topmost max_amount items

        def getter(pos_list: Attribute[list[Vector]], max_amount: Attribute[int]) -> list[Vector]:
            if len(pos_list.value) > max_amount.value:
                pos_list.value = pos_list.value[len(pos_list.value) - max_amount.value:]
            return pos_list.value

        def setter(pos_list: Attribute[list[Vector]], max_amount: Attribute[int], value: list[Vector]):
            pos_list.value = value
            getter(pos_list, max_amount)
        self.pivot_positions = AttributeHolder(
            AttributeMap(
                Attribute([], name="pivot position list"), self.pivot_max_amount,
                getter=getter,
                setter=setter,
                name="pivot positions"
            ))

        self.renderText = renderText.RenderText(50, self.color)

    def Select(self, *selected: GameObject, hold=False):
        if hold:
            self.selected.extend(selected)
        else:
            self.selected = list(selected)

    # def Set_position(self, pos: Vector):
    #     self.position.Set(pos)

    def Draw(self, canvas: screenIO.Canvas):
        canvas.Circle(self.picker_position.value, self.max_pick_range.value, self.color.value, 1)
        for s in self.selected:
            s.Glow(canvas, self.color)
        text = self.renderText.RenderLines(renderText.Text(f"mode: {self.mode.value}"), self.color.value)
        canvas.Blit(text, self.picker_position.value)
        for p in self.pivot_positions.value:
            canvas.Circle(p, 3, self.color.value, 1)
            pass

    def Do_Select(self, choices: list[GameObject]):
        closest = min(choices, key=lambda g: g.DistanceSq(self.picker_position), default=None)
        if closest is not None and closest.DistanceSq(self.picker_position) <= self.max_pick_range.value**2:
            self.Select(closest, hold=self.hold.Get())

    def Do_CreatePivot(self):
        self.pivot_positions.value += [self.picker_position.value]

    def Do_ChangeMode(self, amount: int):
        self.mode.value = (self.mode.value + amount) % 7


def main():
    class A(screenIO.Scene):
        def o_Init(self, updater: screenIO.Updater):
            self.attributes = {"mpos": AttributeHolder(Attribute(Vector(0, 0), "mouse_position"))}
            self.gameObjects = GameObjectList()
            self.editor = Editor()
            self.editor.picker_position.SetAttribute(self.attributes["mpos"].attribute)
            pass

        def o_Update(self, updater: screenIO.Updater):
            inputs = updater.get_inputs()
            canvas = updater.get_canvas()
            mpos = inputs.get_mouse_position()
            self.attributes["mpos"].Set(mpos)
            if inputs.keyPressed(pygame.K_w):
                self.gameObjects.Add(Point(Attribute(mpos)))
            if inputs.keyDown(pygame.K_s) or inputs.mouseDown(1):
                self.editor.Do_Select(self.gameObjects.Iterator())
            if inputs.keyDown(pygame.K_d):
                self.editor.Do_CreatePivot()
            if inputs.mouseDown(4):
                self.editor.Do_ChangeMode(1)
            if inputs.mouseDown(5):
                self.editor.Do_ChangeMode(-1)
            canvas.Fill((100, 100, 255))
            self.gameObjects.Draw(canvas)
            self.editor.Draw(canvas)
            pass
    screenIO.Updater(A(), screenIO.Canvas(pygame.display.set_mode())).Play()


if __name__ == '__main__':
    main()
