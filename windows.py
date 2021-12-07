
from screenIO import *

# Vector = np.ndarray
# class Vector2(np.ndarray):
#     def __new__(cls, x,y):
#         return np.array()
#         pass


class WindowShape:
    def __init__(self, pos: 'Vector', size: 'Vector'):
        self.window: 'Window' = None
        self.parent: 'WindowShape' = None
        self.pos = pos
        self.size = size
        self.true_pos = vec(0, 0)
        pass

    def Get_true_pos(self):
        if self.parent:
            par = self.parent.true_pos
        else:
            par = vec(0, 0)
        self.true_pos = par + self.pos

        return self.true_pos

    def posInside(self, pos):
        "returns a tuple containing the pos's position relative to the window, and whether it is inside the window"
        a = pos - self.true_pos
        if ((0, 0) <= a).all() and (a < self.size).all():
            return a, True
        else:
            return a, False
    pass


class Window:
    parent: 'Window|None' = None
    # func_OnClick: Callable[[Updater], None] = None

    def __init__(self, shape: 'WindowShape', sub: 'list[Window]' = None):
        self.shape = shape
        self.shape.window = self
        self.sub = sub or []
        for s in self.sub:
            s.parent = self
            s.shape.parent = self.shape
        self.canvas = CanvasNoZoom(pygame.Surface(self.shape.size))

    def _render(self) -> list[tuple[pygame.Surface, Vector]]:
        b = (self.o_Render(), self.get_true_pos())  # , None, pygame.BLEND_RGB_SUB)
        a = [b] if b[0] else []
        for s in self.sub:
            a += s._render()
        # [s._render() for s in self.sub]
        return a

    def Update_position(self):
        self.get_true_pos()
        for s in self.sub:
            s.Update_position()

    def o_Render(self) -> 'pygame.Surface|None':
        return self.canvas.surface
        pass

    def get_true_pos(self) -> Vector:
        return self.shape.Get_true_pos()
        pass

    def Top_Render(self, canvas: 'Canvas'):
        'Renders the window and all children. Additionally has the same effect as Window.Update_position().'
        canvas.Blits(self._render())
        pass

    def Top_Update(self, updater: 'Updater'):
        'calls o_Update for all children'
        self.o_Update()
        for s in self.sub:
            s.Top_Update(updater)
        pass

    def o_Update(self, updater: 'Updater'):
        pass

    def Add_window(self, window: 'Window'):
        self.sub.append(window)
        window.parent = self
        window.shape.parent = self.shape

    def posInside(self, pos: Vector) -> tuple[Vector, bool]:
        "returns a tuple containing the pos's position relative to the window, and whether it is inside the window"
        return self.shape.posInside(pos)

    def posInsideOnly(self, pos: Vector) -> tuple[Vector, 0 | 1 | 2]:
        'same as posInside, but returns 2 if the position is also not inside any child windows'
        a, b = self.posInside(pos)
        if b:
            for s in self.sub:
                if s.posInside(pos)[1]:
                    break
            else:
                return a, 2
            return a, 1
        else:
            return a, 0


w1 = Window(WindowShape(vec(50, 50), vec(700, 700)))
w1.canvas.Fill((0, 100, 100))
w1.canvas.Line(vec(0, 0), vec(50, 25), 5, (100, 0, 0))

w2 = Window(WindowShape(vec(50, 50), vec(140, 140)))
w2.canvas.Fill((0, 0, 100))
w2.canvas.Line(vec(0, 0), vec(50, 25), 5, (100, 0, 0))
w1.Add_window(w2)


def update(updater: 'Updater'):
    updater.get_canvas().Fill((200, 200, 200))
    w1.Update_position()
    a, b = w1.posInsideOnly(updater.get_inputs().get_mouse_position())
    if b == 2:
        if updater.get_inputs().keyPressed(pygame.K_s):
            w1.canvas.Circle(a, 50, (0, 100, 200))
        if updater.get_inputs().keyPressed(pygame.K_d):
            w1.canvas.Circle(a, 25, (0, 0, 200))
        w1.canvas.Circle(a, 5, (200, 200, 0))
    w1.Top_Render(updater.get_canvas())


Updater(update).Play()
