from email.policy import default
import itertools
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


_VT = TypeVar("_VT")

Position = Vector


class GameObject:
    "editable by Editor"

    def Draw(self, canvas: screenIO.Canvas):
        pass

    def Glow(self, canvas: screenIO.Canvas, color: Color):
        pass

    def DistanceSq(self, pos: Position) -> float:
        raise NotImplementedError()

    def get_editable_positions(self) -> list[VariableHolder[Position]]:
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

    def get_editable_positions(self):
        return (itertools.chain(*(go.get_editable_positions() for go in self.gameObjects)))

    def get_closest_editable_position(self, position: Position, withinSq: float = None) -> tuple[VariableHolder[Position], float] | None:
        "returns a VariableHolder containing a position, and the square distance to it"
        var, disSq = min(((pos_var, position.distanceSq(pos_var.Get())) for pos_var in self.get_editable_positions()), key=lambda x: x[1], default=(None, None))

        return (None, None) if var is None or withinSq is not None and withinSq < disSq else (var, disSq)


class Shape:
    def Draw(self, canvas: screenIO.Canvas):
        pass

    def get_equations(self, x, y) -> Iterable[sympy.Equality]:
        return ()
    pass


class Circle(Shape):
    def __init__(self, center: Variable[Vector], edge: Variable[Vector]):
        self.center = VariableHolder(center, "center", self)
        self.edge = VariableHolder(edge, "edge", self)

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
        self.a = VariableHolder(a, parent=self)
        self.b = VariableHolder(b, parent=self)

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
    def __init__(self, pos: Variable[Position]):
        self.position = VariableHolder(pos, parent=self)
        self.color = VariableHolder(Variable(Color(255, 0, 100)), parent=self)

    def Draw(self, canvas: screenIO.Canvas):
        canvas.Circle(self.position.Get(), 2, self.color.Get())

    def Glow(self, canvas: screenIO.Canvas, color: Color):
        canvas.Circle(self.position.Get(), 3, color, 1)

    def DistanceSq(self, pos: Position) -> float:
        return self.position.Get().distanceSq(pos)

    def get_editable_positions(self):
        return [self.position]


import menus


class EditorAction(Generic[_VT]):
    def __init__(self, editor: 'Editor', variables: set[VariableHolder[_VT]]):
        self.editor = editor
        self.start_editor_pos = self.editor.picker_position.Get()
        self.start_values = dict((var, var.Get()) for var in variables)
        self.pivots = self.editor.pivot_positions.Get().copy()

    def Update(self):
        editor_pos = self.editor.picker_position.Get()
        for var, start_pos in self.start_values.items():
            self.UpdateVar(var, start_pos, self.start_editor_pos, editor_pos, self.pivots)

    def UpdateVar(self, var: VariableHolder[_VT], start_value: _VT, editor_start: Position, editor_stop: Position, pivots: list[Position]):
        pass

    pass


class EditorAction_move(EditorAction[Position]):
    def UpdateVar(self, var: VariableHolder[Position], start_value: Position, editor_start: Position, editor_stop: Position, pivots: list[Position]):
        var.Set(start_value + editor_stop - editor_start)


class EditorAction_rotate(EditorAction[Position]):
    def UpdateVar(self, var: VariableHolder[Position], start_value: Position, editor_start: Position, editor_stop: Position, pivots: list[Position]):
        p = pivots[-1]
        stop_value = p + (start_value - p).complexMul((editor_stop - p).complexDiv(editor_start - p))
        var.Set(stop_value)
    pass


class Editor:
    def __init__(self, gameObjectList: GameObjectList):
        self.game_object_list = gameObjectList
        self.selected_gameObjects: set[GameObject] = set()
        self.selected_posVars: set[VariableHolder[Position]] = set()
        self.hold = VariableHolder(Variable(False))
        self.color = VariableHolder(Variable(Color(100, 255, 100)))
        self.picker_position = VariableHolder(Variable(Position(0, 0)))
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

        def getter(pos_list: Variable[list[Position]], max_amount: Variable[int]) -> list[Position]:
            if len(pos_list.value) > max_amount.value:
                pos_list.value = pos_list.value[len(pos_list.value) - max_amount.value:]
            return pos_list.value

        def setter(value: list[Position], pos_list: Variable[list[Position]], max_amount: Variable[int]):
            pos_list.value = value
            getter(pos_list, max_amount)
        self.pivot_positions: VariableHolder[list[Position]] = VariableHolder(
            VariableMap(
                Variable([], name="pivot position list"), self.pivot_max_amount,
                getter=getter,
                setter=setter,
                name="pivot positions"
            ))

        self.renderText = renderText.RenderText(25, self.color.Get())

        self.menu = menus.ContextMenu(
            [
                "set to 3",
                "set mode >"
            ],
            {0: lambda: self.mode.Set(3)},
            {1: menus.ContextMenu(
                [
                    "pick",
                    "move",
                    "rotate around pivot",
                    "scale around pivot",
                    "rotate/scale around pivot",
                    "stretch normal to two pivots",
                    "link selected variables"
                ],
                dict((i, (lambda j: lambda: self.mode.Set(j))(i)) for i in range(7)),
                {},
                10
            )},
            15
        )

        self.action = None

    def Select(self, *selected: GameObject, hold=False):
        if hold:
            self.selected_gameObjects.update(selected)
        else:
            self.selected_gameObjects = set(selected)

    def Select_posVar(self, *selected: VariableHolder[Position], hold=False):
        if hold:
            self.selected_posVars.update(selected)
        else:
            self.selected_posVars = set(selected)
        pass

    def Draw(self, canvas: screenIO.Canvas):
        canvas.Circle(self.picker_position.value, self.max_pick_range.value, self.color.value, 1)
        for s in self.selected_gameObjects:
            s.Glow(canvas, self.color.Get())
        for s in self.selected_posVars:
            canvas.Circle(s.Get(), 5, self.color.value, 1)

        text = self.renderText.RenderLines(renderText.Text(f"mode: {self.mode.value}"), self.color.value)
        canvas.Blit(text, self.picker_position.value)
        for p in self.pivot_positions.value:
            canvas.Circle(p, 3, self.color.value, 1)
            pass
        self.menu.Draw(canvas)

    def closest_posVar(self):
        closest, disSq = self.game_object_list.get_closest_editable_position(self.picker_position.Get(), withinSq=self.max_pick_range.Get()**2)
        return closest

    def Do_Select_closest_posVar(self):
        closest = self.closest_posVar()
        if closest is not None:
            self.Select_posVar(closest, hold=self.hold.Get())
        else:
            self.Select_posVar(hold=self.hold.Get())

    def Do_Left_Click(self):
        if self.action:
            return
        if self.menu.ClickAt(self.picker_position.Get()):
            return
        match self.mode.value:
            case 0:
                self.Do_Select_closest_posVar()
            case 1:
                self.action = EditorAction_move(self, self.selected_posVars)
            case 2:
                self.action = EditorAction_rotate(self, self.selected_posVars)

    def Do_Right_Click(self):
        if self.action:
            return
        self.menu.Flip_openclose(self.picker_position.Get())

    def Do_CreatePivot(self):
        if self.action:
            return
        self.pivot_positions.value += [self.picker_position.value]

    def Do_Mousewheel(self, amount: int):
        if self.action:
            return
        self.mode.value = (self.mode.value + amount) % 7

    def Do_Update(self):
        if self.action:
            self.action.Update()
        pass

    def Do_Left_Hold(self):
        pass

    def Do_Left_Up(self):
        if self.action:
            self.action = None


def main():
    class A(screenIO.Scene):
        def o_Init(self, updater: screenIO.Updater):
            self.variables = {"mpos": VariableHolder(Variable(Vector(0, 0), "mouse_position"))}
            self.gameObjects = GameObjectList()
            self.editor = Editor(self.gameObjects)
            self.editor.picker_position.SetVariable(self.variables["mpos"].variable)
            pass

        def o_Update(self, updater: screenIO.Updater):
            inputs = updater.get_inputs()
            canvas = updater.get_canvas()
            mpos = inputs.get_mouse_position()
            self.variables["mpos"].Set(mpos)
            # self.editor.hold.Set(inputs.keyPressed(pygame.K_LSHIFT) or inputs.keyPressed(pygame.K_RSHIFT))
            self.editor.hold.Set(inputs.Pressed("left shift", "right shift"))

            if inputs.Pressed("up", "w"):
                self.gameObjects.Add(Point(Variable(mpos)))
            if inputs.Down("left", "mouse left"):
                self.editor.Do_Left_Click()
            if inputs.Up("left", "mouse left"):
                self.editor.Do_Left_Up()
            if inputs.Down("right", "mouse right"):
                self.editor.Do_Right_Click()
            if inputs.Down("d", "down"):
                self.editor.Do_CreatePivot()
            self.editor.Do_Mousewheel(inputs.get_mousewheel())
            self.editor.Do_Update()
            canvas.Fill((100, 100, 255))
            self.gameObjects.Draw(canvas)
            self.editor.Draw(canvas)
            pass
    screenIO.Updater(A(), screenIO.Canvas(pygame.display.set_mode())).Play()


if __name__ == '__main__':
    main()
