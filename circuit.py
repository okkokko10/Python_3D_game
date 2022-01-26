from collections import Counter
from itertools import product, chain
from vector import Vector, IntVec


class Board:
    pins: "dict[IntVec,Pin]"

    def __init__(self):
        self.pins = {}
        self.inputs = []
        self.outputs = []
        self.to_update = set()
        self.to_trash = set()

    def update(self):
        changes = Counter()
        for pos in self.to_update:
            pin = self.get_pin(pos)
            ac, de = pin.updateOut()
            changes.update(ac)
            changes.subtract(de)
            if not pin.notEmpty():
                del self.pins[pos]
        self.to_update.clear()
        for i, v in changes.items():
            if v:
                self.modify_pin(i).updateIn(v)

    def get_pin(self, pos):
        pos = IntVec(pos)
        if self.has_pin(pos):
            return self.pins[pos]
        else:
            return self.new_pin(pos)

    def new_pin(self, pos):
        pos = IntVec(pos)
        self.pins[pos] = Pin(pos)
        return self.pins[pos]

    def modify_pin(self, pos):
        pos = IntVec(pos)
        "gets the pin and automatically adds it to the update list"
        self.to_update.add(pos)
        temp = self.get_pin(pos)
        temp._to_be_updated = True
        return temp

    def has_pin(self, pos):
        pos = IntVec(pos)
        return pos in self.pins

    def get_default_pin(self, pos):
        pos = IntVec(pos)
        return self.pins[pos] if self.has_pin(pos) else None


class Pin:
    def __init__(self, pos):
        self.pos = pos
        self._directions = Directions()
        self._new_directions = Directions()
        self._power = 0
        self._new_power = 0
        self._default = 0
        self._new_default = 0
        self._activate_buffer = []
        self._deactivate_buffer = []
        self._to_be_updated = True

    def updateIn(self, power_change):
        self._new_power += power_change
        pass

    def updateOut(self):
        "updates and returns places to activate and places to deactivate, as absolute positions"
        if self._directions != self._new_directions:
            removed = self._directions.difference(self._new_directions)  # removed directions
            for pos in removed.iterate(self._power):
                self.deactivate(pos)
            added = self._new_directions.difference(self._directions)  # added directions
            for pos in added.iterate(self._power):
                self.activate(pos)
            self._directions.Become(self._new_directions)

        if self._default != self._new_default:
            self._new_power += self._new_default - self._default
            self._default = self._new_default

        if self._power != self._new_power:
            for pos in self._directions.iterate(self._power):
                self.deactivate(pos)
            self._power = self._new_power
            for pos in self._directions.iterate(self._new_power):
                self.activate(pos)
        temp = self._activate_buffer, self._deactivate_buffer
        self._activate_buffer = []
        self._deactivate_buffer = []
        self._to_be_updated = False
        return temp

    def deactivate(self, pos):
        "pos is relative to the pin"
        self._deactivate_buffer.append(self.pos + pos)

    def activate(self, pos):
        self._activate_buffer.append(self.pos + pos)

    @property
    def directions(self):
        return self._new_directions

    @property
    def default(self):
        return self._new_default

    @default.setter
    def default(self, value):
        self._new_default = value

    @property
    def power(self):
        return self._power

    def notEmpty(self):
        return bool(self._directions.notEmpty() or self._new_directions.notEmpty() or self._default or self._new_default or self._power or self._new_power)


class Directions:
    UP = 1 << 0
    DOWN = 1 << 1
    LEFT = 1 << 2
    RIGHT = 1 << 3

    def __init__(self, value=0):  # up,down,left,right
        self._value = value

    def iterate(self, distance):
        if distance:
            if self.up:  # up
                yield IntVec(0, -distance)
            if self.down:  # down
                yield IntVec(0, distance)
            if self.left:  # left
                yield IntVec(-distance, 0)
            if self.right:  # right
                yield IntVec(distance, 0)

    def difference(self, other: "Directions"):
        "what this has but the other doesn't"
        return Directions(self._value & ~other._value)

    def __eq__(self, other):
        if isinstance(other, Directions):
            return self._value == other._value
        else:
            return False

    def add(self, other: "Directions"):
        self._value |= other._value

    def remove(self, other: "Directions"):
        self._value &= ~other._value

    def set(self, other: "Directions"):
        self._value = other._value

    def flip(self, other: "Directions"):
        self._value ^= other._value

    @property
    def up(self):
        return self._value & Directions.UP

    @property
    def down(self):
        return self._value & Directions.DOWN

    @property
    def left(self):
        return self._value & Directions.LEFT

    @property
    def right(self):
        return self._value & Directions.RIGHT

    @classmethod
    def fromVector(cls, v):
        x, y = v
        if abs(x) < abs(y):
            if y < 0:
                return cls(Directions.UP)
            else:
                return cls(Directions.DOWN)
        else:
            if x < 0:
                return cls(Directions.LEFT)
            else:
                return cls(Directions.RIGHT)

    @classmethod
    def fromTile(cls, v):
        "what quadrant of a unit tile is this vector in"
        return cls.fromVector(v - Vector(0.5, 0.5))

    def notEmpty(self):
        return bool(self._value)

    def Become(self, other: "Directions"):
        self._value = other._value


import screenIO
import renderText


class Grid:
    def __init__(self, size: "Vector", offset: "Vector" = Vector(0, 0), tile: "Vector" = Vector(1, 1)):
        "size must be composed of integers"
        self.size = size
        self.offset = offset
        self.tile = tile

    def area(self):
        sx, sy = self.size
        ox, oy = self.offset
        tx, ty = self.tile
        return [Vector(x * tx + ox, y * ty + oy) for x in range(sx) for y in range(sy)]

    def locate(self, vector: "Vector"):
        "returns the tile the vector is on, and where on the tile it is"
        fl = Vector(*((v - o) // t for v, t, o in zip(vector, self.tile, self.offset)))
        mod = Vector(*((v - o) / t % 1 for v, t, o in zip(vector, self.tile, self.offset)))
        return fl, mod

    def snap(self, vector: "Vector"):
        return Vector(*((v - o) // t * t + o for v, t, o in zip(vector, self.tile, self.offset)))


class View:
    def __init__(self, board, canvas=None):
        self.boards: list[list[Board, Vector]] = [[board, Vector(0, 0)]]
        self.width = 30
        self.height = 20
        self.area = Vector(self.width, self.height)
        "vector of width and height"
        self.zoom = 150
        self.tile = Vector.ONE * self.zoom
        self.offset = self.tile / 2
        if canvas is None:
            self.canvas = screenIO.CanvasNoZoom(self.area * self.zoom)
        else:
            self.canvas = canvas
        self.textRender = renderText.RenderText(color=(200, 200, 200, 200))

    def get_pos(self):
        return self.boards[-1][1]

    def get_board(self):
        return self.boards[-1][0]

    def Show(self):
        print(self)

    def _old_to_draw(self, board: Board, pos):
        ox, oy = pos
        return [[board.get_default_pin(IntVec(x, y)) for x in range(ox, ox + self.width)] for y in range(oy, oy + self.height)]

    def to_draw(self, board: Board, pos):
        ox, oy = pos
        # return [board.get_default_pin(IntVec(x, y)) for x in range(ox, ox + self.width) for y in range(oy, oy + self.height)]
        return map(board.get_default_pin, Grid(self.area, pos).area())

    def text(self, board: Board, pos):
        toDraw = self._old_to_draw(board, pos)
        ms = MultiString(3)
        for row in toDraw:
            ms.createRow()
            for point in row:
                if point:
                    ms.addString(
                        [". || ." if point.directions.up else ".    .",
                         ("<" if point.directions.left else " ") + (str(point.power).center(4)
                                                                    if point.power else "    ") + (">" if point.directions.right else " "),
                         ". || ." if point.directions.down else ".    ."
                         ])
                else:
                    ms.addString(["      ", "      ", "      "])
        print(ms.view())

    def GridPoints(self):
        return Grid(self.area, tile=self.tile).area()
        # return map((lambda x: IntVec(*x) * self.zoom), product(range(self.width), range(self.height)))

    def locate(self, pos: IntVec):
        grid = Grid(self.area, tile=self.tile)
        i, mod = grid.locate(pos)
        return i + self.get_pos(), Directions.fromTile(mod)

    def Draw(self):
        board, topPos = self.boards[-1]
        to_draw = self.to_draw(board, topPos)
        self.canvas.Fill((60, 50, 50))
        for pin, pos in zip(to_draw, self.GridPoints()):
            if pin is not None:
                self.DrawPin(pin, pos)
        return self.canvas

    def DrawPin(self, pin: Pin, pos):
        center = pos + self.offset
        color1 = 90, 50, 50
        color2 = 100, 100, 150
        color3 = 50, 80, 120
        size = 1 / 5
        for v in pin.directions.iterate(self.zoom / 2):
            self.canvas.Line(center, center + v, self.zoom / 5, color2)
        self.canvas.Circle(center, self.zoom * size, color2)
        # self.canvas.Blit(self.textRender.Render(str(pin.power), color=color3), pos)
        r = Vector(0, 1) * self.zoom * (1 / 5)
        rotator = Vector.Rotation(1 / max(8, pin.power))
        for i in range(pin.power):
            color = color1 if i < pin.default else color3
            self.canvas.Circle(center + r, self.zoom / 10, color)
            r = rotator.complexMul(r)


class MultiString:
    def __init__(self, row_width):
        self.row_width = row_width
        self.rows: list[list[str]] = []

    def createRow(self):
        self.rows.append(["" for _ in range(self.row_width)])

    def addString(self, value: list[str]):
        for i, v in zip(range(self.row_width), value):
            self.rows[-1][i] += v

    def view(self):
        return "\n".join("\n".join(row) for row in self.rows)


# B = Board()
# V = View(B)

# B.modify_pin((1, 1)).directions.set(Directions(Directions.RIGHT))
# B.modify_pin((1, 1)).default = 1
# B.update()
# B.update()

# V.text(B, (0, 0))
# V.Draw()


class sceneA(screenIO.Scene):
    def __init__(self, *args, **kvargs):
        pass

    def o_Init(self, updater: 'screenIO.Updater'):
        self.board = Board()
        self.view = View(self.board)
        # self.board.modify_pin(IntVec(1, 1)).directions.set(Directions(Directions.RIGHT))
        # self.board.modify_pin(IntVec(1, 1)).default = 1
        # self.board.update()
        # self.view.text(self.board, IntVec(0, 0))

    def o_Update(self, updater: 'screenIO.Updater'):
        self.board.update()
        pos = updater.inputs.get_mouse_position()
        l, d = self.view.locate(pos)
        pin = self.view.get_board().modify_pin(l)
        if updater.inputs.mouseDown(1):
            pin.directions.flip(d)
        if updater.inputs.mouseDown(4):
            pin.default += 1
        if updater.inputs.mouseDown(5):
            if pin.default > 0:
                pin.default -= 1
        updater.canvas.BlitCanvas(self.view.Draw())


screenIO.Updater(sceneA()).Play()
