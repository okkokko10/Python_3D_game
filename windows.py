
from screenIO import *


# class Vector2(np.ndarray):
#     def __new__(cls, x,y):
#         return np.array()
#         pass


class WindowShape:
    def __init__(self, x, y, sx, sy):
        self.window: 'Window' = None
        self.parent: 'WindowShape' = None
        self.pos = vec(x, y)
        self.size = vec(sx, sy)
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

    def __init__(self, shape: 'WindowShape', sub: 'list[Window]' = None):
        self.shape = shape
        self.shape.window = self
        self.sub = sub or []
        for s in self.sub:
            s.parent = self
            s.shape.parent = self.shape
        self.canvas = CanvasNoZoom(pygame.Surface(self.shape.size))

    def _render(self) -> 'list[Canvas]':
        b = (self.get_true_pos(), self.Render())
        a = [b] if b[1] else []
        for s in self.sub:
            # a.BlitCanvas(s._render(), (x, y))
            a += s._render()
            pass

        return a
        pass

    def Render(self) -> 'Canvas|None':
        return self.canvas
        pass

    def get_true_pos(self) -> 'tuple[int,int]':
        return self.shape.Get_true_pos()
        pass

    def TopRender(self, canvas: 'Canvas'):
        canvas.BlitCanvases(self._render())
        pass

    def Add_window(self, window: 'Window'):
        self.sub.append(window)
        window.parent = self
        window.shape.parent = self.shape

    def posInside(self, pos):
        "returns a tuple containing the pos's position relative to the window, and whether it is inside the window"
        return self.shape.posInside(pos)


w1 = Window(WindowShape(250, 350, 300, 400))
w1.canvas.Fill((0, 100, 100))
w1.canvas.Line(vec(0, 0), vec(50, 25), 5, (100, 0, 0))

w2 = Window(WindowShape(50, 50, 140, 140))
w2.canvas.Fill((0, 0, 100))
w2.canvas.Line(vec(0, 0), vec(50, 25), 5, (100, 0, 0))
w1.Add_window(w2)


def update(updater: 'Updater'):
    updater.get_canvas().Fill((200, 200, 200))
    w1.TopRender(updater.get_canvas())
    a, b = w2.posInside(updater.get_inputs().get_mouse_position())
    if b:
        print(a)
        w2.canvas.Circle(a, 5, (200, 200, 0))
    pass


Updater(update).Play()
