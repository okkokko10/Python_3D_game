
from screenIO import *


class Menu:
    def __init__(self, submenus: 'list[tuple[tuple[int,int],Menu]]'):
        self.submenus = submenus

    def _render(self) -> 'Canvas':
        a = self.Render()
        for (x, y), sm in self.submenus:
            sm._render()
        pass

    def Render(self) -> 'Canvas': return
