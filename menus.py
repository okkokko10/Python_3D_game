from typing import Callable
import renderText
from vector import Vector
import screenIO


class Menu:
    pass


class TextMenu(Menu):
    # position: Vector
    # "top-left corner"
    # open: bool

    # def ClickLine(self, line: int):
    #     pass

    # def Render(self, position: Vector):
    #     return

    # def Open(self, pos: Vector):
    #     self.open = True
    #     self.position = pos

    # def Close(self):
    #     # for i, menu in self.submenus:
    #     #     menu.Close()
    #     self.open = False
    pass


class ContextMenu(TextMenu):
    submenus: dict[int, 'ContextMenu']

    def __init__(self, text: list[str], commands: dict[int, Callable[[], bool]], width: int, render_text: renderText.RenderText = None):
        self.renderText = render_text or renderText.RenderText(25)
        self.open = False
        self.position = Vector(0, 0)
        self.text = text
        self.commands = commands
        self.submenus = {}
        self.clicked: tuple = None
        self.width = width * self.renderText.width
        self.line_amount = self.text.height()
        self.height = self.line_amount * self.renderText.height
        self.size = Vector(self.width, self.height)

    def ClickPath(self, path: list[int]):
        if len(path) > 1:
            return self.submenus[path[0]].ClickLine(path[1:])
        else:
            return self.ClickLine(path[0])

    def ClickLine(self, line: int):
        "returning False closes the menu"
        if line in self.submenus:
            self.submenus[line].Flip_openclose()
            return True
        if line in self.commands:
            self.commands[line]()
            return False
        return True

    def Draw(self, canvas: screenIO.Canvas):
        canvas.Blits(self.Render())

    def Render(self):
        if not self.open:
            return []
        out = [(self.renderText.RenderLines(self.text), self.position.f)]
        for i, menu in self.submenus.items():
            out.extend(menu.Render())
        return out

    def Create(self, pos: Vector):
        self.position = pos

    def Open(self):
        self.open = True

    def Close(self):
        self.open = False
        for i in self.submenus:
            self.Close_Submenu(i)

    def Get_clicked(self):
        if self.clicked is not None:
            return self.clicked
        return None

    def Create_Submenu(self, line: int, menu: 'ContextMenu'):
        pos = Vector(line * self.renderText.height, self.width)
        self.submenus[line] = menu
        menu.Create(pos)

    def Open_Submenu(self, line: int):
        self.submenus[line].Open()

    def Close_Submenu(self, line: int):
        self.submenus[line].Close()
        # self.submenus.pop(line)

    def Get_Submenu(self, line: int):
        return self.submenus[line]

    def Locate(self, position: Vector) -> list[int] | None:
        """returns a list like this: [a,b,i]
        which means that the position is at line a's submenu's line b's submenu's line i
        or it returns None, which means the position is not on the menu"""
        if not self.open:
            return None
        if position.x < self.position.x:
            # to the left
            return None
        elif position.x < self.position.x + self.width:
            # at the same level
            _, line = self.renderText.Locate(position - self.position)
            if 0 <= line <= self.line_amount:
                return [line]
            else:
                return None
        else:
            # to the right / at the next level
            for i in self.submenus:
                a = self.submenus[i].Locate(position)
                if a is not None:
                    return [i] + a
            else:
                return None

    def ClickAt(self, position: Vector):
        loc = self.Locate(position)
        if loc:
            if not self.ClickPath(loc):
                self.Close()
        else:
            self.Close()

    def Flip_openclose(self):
        if self.open:
            self.Close()
        else:
            self.Open()
