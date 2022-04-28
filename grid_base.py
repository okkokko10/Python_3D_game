import screenIO
import pygame
import renderText

from typing import Callable, TypeVar
from typing_extensions import Self

_V1 = TypeVar("_V1")
_V2 = TypeVar("_V2")


def array_from_function(width: int, height: int, func):
    return [[func(i, j) for i in range(width)] for j in range(height)]


def map_array(arr: list[list[_V1]], func: Callable[[_V1, int, int], _V2]) -> list[list[_V2]]:
    return [[func(value, i, j) for i, value in enumerate(row)] for j, row in enumerate(arr)]


# def buffer_array(arr: list[list[_V1]]) -> list[list[_V1]]:
#     return [[make_buffer(value) for value in row] for row in arr]


class deep_copiable:
    def _deep_copy(self) -> Self: ...


def deep_copy(obj):
    if isinstance(obj, deep_copiable):
        return obj._deep_copy()
    elif isinstance(obj, list):
        return [deep_copy(value) for value in obj]
    else:
        return obj


class Grid(deep_copiable):
    def _deep_copy(self) -> Self:
        return type(self)(self.width, self.height, deep_copy(self.grid))

    def __init__(self, width: int, height: int, grid=None):
        self.width = width
        self.height = height
        self.grid = array_from_function(width, height, lambda x, y: 0) if grid is None else grid

    def get(self, x: int, y: int):
        return self.grid[y][x]

    def set(self, x: int, y: int, value):
        self.grid[y][x] = value

    def __getitem__(self, args):
        return self.get(*args)

    def __setitem__(self, args, value):
        return self.set(*args, value=value)


class Grid_IO:
    def __init__(self, width: int, height: int, scale: pygame.Vector2):
        self.width = width
        self.height = height
        self.scale = scale
        self.size = (scale[0] * width, scale[1] * height)
        self.surface = pygame.Surface(self.size)
        self.grid = Grid(5, 5)
        super().__init__(width, height, scale)

    def update(self, updater: screenIO.Updater):
        global_mouse = updater.inputs.get_mouse_position()
        mouse_x = global_mouse[0] / self.scale[0]
        mouse_y = global_mouse[1] / self.scale[1]
        mouse_offset = pygame.Vector2(mouse_x % 1, mouse_y % 1)
        mouse_x = int(mouse_x)
        mouse_y = int(mouse_y)
        if updater.inputs.Down("mouse 1"):
            self.o_TileClicked(mouse_x, mouse_y, mouse_offset)
        updater.canvas.Blit(self.surface)

    def Draw(self):
        self.o_Draw_Background()
        for x, y in zip(range(self.width), range(self.height)):
            self.o_DrawTile(x, y)
        self.o_Draw_Foreground()

    def o_TileClicked(self, x: int, y: int, offset: pygame.Vector2):
        pass

    def o_DrawTile(self, x, y): ...
    def o_Draw_Background(self): ...
    def o_Draw_Foreground(self): ...


class MineSweeper(Grid_IO):
    pass


class scene_1(screenIO.Scene):
    def o_Init(self, updater: 'screenIO.Updater'):
        self.grid_io = Grid_IO(10, 10, pygame.Vector2(50, 50))
        self.grid = Grid(10, 10)
        return super().o_Init(updater)

    def o_Update(self, updater: 'screenIO.Updater'):
        self.grid_io.update(updater)
        return super().o_Update(updater)
