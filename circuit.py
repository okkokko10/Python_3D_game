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

    def update(self):
        changes = Counter()
        for pos in self.to_update:
            ac, de = self.get_pin(pos).updateOut()
            changes.update(ac)
            changes.subtract(de)
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
        return self.get_pin(pos)

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
            self._directions = self._new_directions

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
                return Directions(Directions.UP)
            else:
                return Directions(Directions.DOWN)
        else:
            if x < 0:
                return Directions(Directions.LEFT)
            else:
                return Directions(Directions.RIGHT)


import screenIO
import renderText


class View:
    def __init__(self, board, canvas=None):
        self.boards: list[list[Board, IntVec]] = [[board, IntVec(0, 0)]]
        self.width = 30
        self.height = 20
        self.zoom = 50
        if canvas is None:
            self.canvas = screenIO.CanvasNoZoom(IntVec(self.width * self.zoom, self.height * self.zoom))
        else:
            self.canvas = canvas
        self.textRender = renderText.RenderText()

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
        return [board.get_default_pin(IntVec(x, y)) for x in range(ox, ox + self.width) for y in range(oy, oy + self.height)]

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
        return map((lambda x: IntVec(*x) * self.zoom), product(range(self.width), range(self.height)))

    def Draw(self):
        board, topPos = self.boards[-1]
        to_draw = self.to_draw(board, topPos)
        self.canvas.Fill((100, 100, 100))
        for pin, pos in zip(to_draw, self.GridPoints()):
            if pin is not None:
                color1 = (0, 100, 0)
                size = 1 / 5
                self.canvas.Circle(pos, self.zoom * size, color1)
                for v in pin.directions.iterate(self.zoom / 2):
                    self.canvas.Line(pos, pos + v, self.zoom / 5, color1)
                self.canvas.Blit(self.textRender.Render(str(pin.power)), pos)
        return self.canvas

    def local(self, pos: IntVec):
        mod = pos - pos.round((self.zoom, self.zoom))
        return IntVec(pos / self.zoom) + self.get_pos(), Directions.fromVector(mod)


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
        self.board.modify_pin(IntVec(1, 1)).directions.set(Directions(Directions.RIGHT))
        self.board.modify_pin(IntVec(1, 1)).default = 1
        self.board.update()
        self.view.text(self.board, IntVec(0, 0))

    def o_Update(self, updater: 'screenIO.Updater'):
        pos = updater.inputs.get_mouse_position()
        l, d = self.view.local(pos)
        if updater.inputs.mouseDown(1):
            pin = self.view.get_board().modify_pin(l)
            pin.directions.flip(d)
        if updater.inputs.mouseDown(3):
            pin = self.view.get_board().modify_pin(l)
            pin.default = 1 - pin.default
        updater.canvas.BlitCanvas(self.view.Draw())
        self.board.update()


screenIO.Updater(sceneA()).Play()
