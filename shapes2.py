# TODO: if you can't move something a certain way, it won't do anything

import math
from typing import Any, Iterable, Generic, TypeVar
import sympy
import screenIO
import pygame
from vector import Vector
import renderText
_VT = TypeVar('_VT')


class Attribute(Generic[_VT]):
    def __init__(self, value: _VT, name=""):
        self.value = value
        self.name = name

    def Set(self, value: _VT):
        self.value = value

    def Get(self) -> _VT:
        return self.value


class AttributeHolder(Generic[_VT]):
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

    def Glow(self, canvas: screenIO.Canvas, color):
        pass

    def DistanceSq(self, pos: Attribute[Vector]) -> float:
        raise NotImplementedError()

    def get_editable(self) -> list[Attribute]:
        raise NotImplementedError()


class Points:
    def __init__(self):
        self.points: AttributeSet[Vector] = AttributeSet()

    def Closest(self, pos: Attribute[Vector]):
        p = pos.Get()

        def key(a: Attribute[Vector]):
            return (a.Get() - p).lengthSq()
        return min(self.points.Iterate(), key=key, default=None)

    def Sorted_by_distance(self, pos: Attribute[Vector]):
        p = pos.Get()

        def key(a: Attribute[Vector]):
            return (a.Get() - p).lengthSq()
        return sorted(self.points.Iterate(), key=key)

    def Draw(self, canvas: screenIO.Canvas):
        color = (255, 125, 255)
        for pa in self.points.Iterate():
            v = pa.Get()
            canvas.Circle(v, 1, color)

    def Create(self, pos: Vector):
        a = Attribute(pos)
        self.points.Add(a)
        return a


class Editor:
    def __init__(self):
        self.selected: list[GameObject] = []
        self.hold = AttributeHolder(Attribute(False))
        self.color = AttributeHolder(Attribute((100, 255, 100)))
        self.position = AttributeHolder(Attribute(Vector(0, 0)))
        self.renderText = renderText.RenderText(50, self.color)

    def Select(self, *selected: GameObject, hold=False):
        if hold:
            self.selected.extend(selected)
        else:
            self.selected = list(selected)

    def Set_position(self, pos: Vector):
        self.position.Set(pos)

    def Draw(self, canvas: screenIO.Canvas):
        for s in self.selected:
            s.Glow(canvas, self.color)
        # self.renderText.RenderLines(renderText.Text(), self.color)

    def Pressed_Select(self, choices: list[GameObject]):
        closest = min(choices, key=lambda g: g.DistanceSq(self.position))
        self.Select(closest, hold=self.hold.Get())


def main():
    class A(screenIO.Scene):
        def o_Init(self, updater: screenIO.Updater):
            self.attributes = {"mpos": AttributeHolder(Attribute(Vector(0, 0), "mouse_position"))}
            self.points = Points()
            self.editor = Editor()
            self.editor.position.SetAttribute(self.attributes["mpos"].attribute)
            pass

        def o_Update(self, updater: screenIO.Updater):
            inputs = updater.get_inputs()
            canvas = updater.get_canvas()
            mpos = inputs.get_mouse_position()
            self.attributes["mpos"].Set(mpos)
            if inputs.keyPressed(pygame.K_w):
                self.points.Create(mpos)
            canvas.Fill((100, 100, 255))
            self.points.Draw(canvas)
            pass
    screenIO.Updater(A(), screenIO.Canvas(pygame.display.set_mode())).Play()


if __name__ == '__main__':
    main()
