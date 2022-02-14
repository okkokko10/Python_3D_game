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

    def __init__(self, text: list[str], commands: dict[int, Callable[[], bool]], submenus: dict[int, 'ContextMenu'], width: int = None, render_text: renderText.RenderText = None):
        self.renderText = render_text or renderText.RenderText(25)
        self.open = False
        self.position = Vector(0, 0)
        self.text = text
        self.commands = commands
        self.submenus = submenus
        self.clicked: tuple = None
        self.width = (width or max(map(len, text))) * self.renderText.width
        self.line_amount = len(self.text)
        self.height = self.line_amount * self.renderText.height
        self.size = Vector(self.width, self.height)

    def ClickPath(self, path: list[int]):
        if len(path) > 1:
            return self.submenus[path[0]].ClickPath(path[1:])
        else:
            return self.ClickLine(path[0])

    def ClickLine(self, line: int):
        "returning False closes the menu"
        if line in self.submenus:
            self.submenus[line].Flip_openclose(self.Submenu_Pos(line))
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

    def Open(self, pos: Vector | None):
        self.open = True
        if pos is not None:
            self.position = pos

    def Close(self):
        self.open = False
        for i in self.submenus:
            self.Close_Submenu(i)

    def Get_clicked(self):
        if self.clicked is not None:
            return self.clicked
        return None

    def Create_Submenu(self, line: int, menu: 'ContextMenu'):
        self.submenus[line] = menu
        menu.Create(self.Submenu_Pos(line))

    def Open_Submenu(self, line: int):
        self.submenus[line].Open(self.Submenu_Pos(line))

    def Submenu_Pos(self, line: int):
        return self.position + Vector(self.width, line * self.renderText.height)

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
        "tries to click the menu. returns True if the menu was clicked"
        loc = self.Locate(position)
        if loc:
            if not self.ClickPath(loc):
                self.Close()
            return True
        else:
            self.Close()
            return False

    def Flip_openclose(self, pos: Vector = None):
        if self.open:
            self.Close()
        else:
            self.Open(pos)
