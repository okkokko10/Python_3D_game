from variables import *
import sympy
import screenIO
import pygame
from vector import Vector
import renderText
import math
from typing import Iterable


class Color(tuple):
    def __new__(cls, *args):
        return tuple.__new__(cls, args)
    pass


class GameObject:
    "editable by Editor"

    def Draw(self, canvas: screenIO.Canvas):
        pass

    def Glow(self, canvas: screenIO.Canvas, color: Variable[Color]):
        pass

    def DistanceSq(self, pos: Variable[Vector]) -> float:
        raise NotImplementedError()

    def get_editable(self) -> list[VariableHolder]:
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


class Shape:
    def Draw(self, canvas: screenIO.Canvas):
        pass

    def get_equations(self, x, y) -> Iterable[sympy.Equality]:
        return ()
    pass


class Circle(Shape):
    def __init__(self, center: Variable[Vector], edge: Variable[Vector]):
        self.center = VariableHolder(center, "center")
        self.edge = VariableHolder(edge, "edge")

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
    def __init__(self, a: Variable[Vector], b: Variable[Vector]):
        self.a = VariableHolder(a)
        self.b = VariableHolder(b)

    def Draw(self, canvas: screenIO.Canvas):
        color = (255, 255, 255)
        canvas.Line(self.a.Get(), self.b.Get(), color, 1)
        pass

    def get_equations(self, x, y) -> Iterable[sympy.Equality]:
        # return sympy.Eq((x - self.center.x)**2 + (y - self.center.y)**2, self.radius**2),
        ax, ay = self.a.Get()
        bx, by = self.b.Get()
        return sympy.Eq((x - bx) * (ay - by), (y - by) * (ax - bx)),


class Point(GameObject):
    def __init__(self, pos: Variable[Vector]):
        self.position = VariableHolder(pos)
        self.color = VariableHolder(Variable(Color(255, 0, 100)))

    def Draw(self, canvas: screenIO.Canvas):
        canvas.Circle(self.position.Get(), 2, self.color.Get())

    def Glow(self, canvas: screenIO.Canvas, color: Variable[Color]):
        canvas.Circle(self.position.Get(), 3, color.Get(), 1)

    def DistanceSq(self, pos: Variable[Vector]) -> float:
        return (self.position.Get() - pos.Get()).lengthSq()

    def get_editable(self) -> list[VariableHolder]:
        return [self.position]


import menus


class Editor:
    def __init__(self):
        self.selected: list[GameObject] = []
        self.hold = VariableHolder(Variable(False))
        self.color = VariableHolder(Variable((100, 255, 100)))
        self.picker_position = VariableHolder(Variable(Vector(0, 0)))
        self.max_pick_range = VariableHolder(Variable(50))
        self.mode = VariableHolder(Variable(0))
        # TODO: create, destroy,
        "0: pick, 1: move, 2: rotate around pivot, 3: scale around pivot, 4: rotate/scale around pivot, 5: stretch normal to two pivots, 6: link selected variables"
        self.pivot_max_amount = VariableHolder(
            VariableMap(
                self.mode,
                getter=lambda mode: [0, 0, 1, 1, 1, 2, 0][mode.value],
                setter=None,
                name="pivot max count"
            ))
        # defining a VariableMap for a list that discards all but the topmost max_amount items

        def getter(pos_list: Variable[list[Vector]], max_amount: Variable[int]) -> list[Vector]:
            if len(pos_list.value) > max_amount.value:
                pos_list.value = pos_list.value[len(pos_list.value) - max_amount.value:]
            return pos_list.value

        def setter(value: list[Vector], pos_list: Variable[list[Vector]], max_amount: Variable[int]):
            pos_list.value = value
            getter(pos_list, max_amount)
        self.pivot_positions = VariableHolder(
            VariableMap(
                Variable([], name="pivot position list"), self.pivot_max_amount,
                getter=getter,
                setter=setter,
                name="pivot positions"
            ))

        self.renderText = renderText.RenderText(50, self.color)

        self.menu = menus.ContextMenu(
            [
                "set to 3",
                "open submenu"
            ],
            {0: lambda: self.mode.Set(3)},
            {1: menus.ContextMenu(
                [
                    "nothing",
                    "set to 4"
                ],
                {1: lambda: self.mode.Set(4)},
                {},
                10
            )},
            15
        )

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
        self.menu.Draw(canvas)

    def Do_Select(self, choices: list[GameObject]):
        closest = min(choices, key=lambda g: g.DistanceSq(self.picker_position), default=None)
        if closest is not None and closest.DistanceSq(self.picker_position) <= self.max_pick_range.value**2:
            self.Select(closest, hold=self.hold.Get())

    def Do_Left_Click(self, choices: list[GameObject]):
        if not self.menu.ClickAt(self.picker_position.Get()):
            if self.mode.value == 0:
                self.Do_Select(choices)

    def Do_Right_Click(self, choices: list[GameObject]):
        self.menu.Flip_openclose(self.picker_position.Get())

    def Do_CreatePivot(self):
        self.pivot_positions.value += [self.picker_position.value]

    def Do_ChangeMode(self, amount: int):
        self.mode.value = (self.mode.value + amount) % 7

    def Do_Update(self):
        pass

    def Do_Left_Hold(self, choices: list[GameObject]):
        pass


def main():
    class A(screenIO.Scene):
        def o_Init(self, updater: screenIO.Updater):
            self.variables = {"mpos": VariableHolder(Variable(Vector(0, 0), "mouse_position"))}
            self.gameObjects = GameObjectList()
            self.editor = Editor()
            self.editor.picker_position.SetVariable(self.variables["mpos"].variable)
            pass

        def o_Update(self, updater: screenIO.Updater):
            inputs = updater.get_inputs()
            canvas = updater.get_canvas()
            mpos = inputs.get_mouse_position()
            self.variables["mpos"].Set(mpos)
            self.editor.hold.Set(inputs.keyPressed(pygame.K_LSHIFT))
            if inputs.keyPressed(pygame.K_w):
                self.gameObjects.Add(Point(Variable(mpos)))
            if inputs.keyDown(pygame.K_s) or inputs.mouseDown(1):
                self.editor.Do_Left_Click(self.gameObjects.Iterator())
            if inputs.keyDown(pygame.K_s) or inputs.mouseDown(3):
                self.editor.Do_Right_Click(self.gameObjects.Iterator())
            if inputs.keyDown(pygame.K_d):
                self.editor.Do_CreatePivot()
            if inputs.mouseDown(4):
                self.editor.Do_ChangeMode(1)
            if inputs.mouseDown(5):
                self.editor.Do_ChangeMode(-1)
            self.editor.Do_Update()
            canvas.Fill((100, 100, 255))
            self.gameObjects.Draw(canvas)
            self.editor.Draw(canvas)
            pass
    screenIO.Updater(A(), screenIO.Canvas(pygame.display.set_mode())).Play()


if __name__ == '__main__':
    main()