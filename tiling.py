
from typing import Generic, Iterable, TypeVar
from typing_extensions import Self
import screenIO
from vector import Vector

# Should be applicable to 3 dimensions, a hexagonal grid, and any arbitrary tiling, which might not even be regular
# Try making a sphere, or hyperbolic tilings
# Make it possible to have the same tile be in multiple tilings at the same time
# Tiles should be able to be Tilings themselves
# Tiles should know what other Tiles they are touching and from which angle

T_Tiling = TypeVar("T_Tiling")


class TilePosition(Generic[T_Tiling]):
    tiling: T_Tiling
    "The tiling the position is local to"

    def __init__(self, tiling: T_Tiling):
        self.tiling = tiling

    pass


class Tiling(Generic[T_Tiling]):
    parent: T_Tiling
    "The tiling the tile belongs to"
    position: TilePosition[T_Tiling]
    "the position this tile is in the tiling"

    def __init__(self, tiling: T_Tiling = None, position: TilePosition[T_Tiling] = None):
        self.parent = tiling
        self.position = position

    def ClosestTile(self, vector: Iterable) -> tuple[TilePosition[Self], "Tiling[Self]"]:
        return


a = Tiling()
b, c = a.ClosestTile((1, 1))
b.tiling
