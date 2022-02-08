
from screenIO import *

# Vector = np.ndarray
# class Vector2(np.ndarray):
#     def __new__(cls, x,y):
#         return np.array()
#         pass


class ContainerShape:
    def __init__(self, *args):
        "pos: 'Vector', size: 'Vector'"
        if len(args) == 1:
            pass
        if len(args) == 2:
            self.pos, self.size = args
        elif len(args) == 4:
            self.pos = vec(*args[0:2])
            self.size = vec(*args[2:4])
        self.container: 'Container' = None
        self.parent: 'ContainerShape' = None
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
        "returns a tuple containing the pos's position relative to the container, and whether it is inside the container"
        a = pos - self.true_pos
        if ((0, 0) <= a).all() and (a < self.size).all():
            return a, True
        else:
            return a, False

    def __iter__(self):
        return (x for x in (self.pos, self.size))

    def update(self, pos, size):
        self.pos = vec(*pos)
        self.size = vec(*size)


class Container:
    parent: 'Container|None' = None
    # func_OnClick: Callable[[Updater], None] = None

    def __init__(self, shape: "ContainerShape|tuple[Vector,Vector]|tuple[float,float,float,float]", children: 'list[Container]' = None):
        self.shape = ContainerShape(*shape)
        self.shape.container = self
        self.children = list(children or [])
        for child in self.children:
            child.parent = self
            child.shape.parent = self.shape
        self.canvas = Canvas(self.shape.size)
        # self.listening = listening  # whether the container should listen to inputs

    def _render(self) -> list[tuple[pygame.Surface, Vector]]:
        blit_sequence = (self.o_Render(), self.get_true_pos())  # , None, pygame.BLEND_RGB_SUB)
        a = [blit_sequence] if blit_sequence[0] else []
        for s in self.get_children():
            a += s._render()
        # [s._render() for s in self.children]
        return a

    def Update_position(self):
        self.get_true_pos()
        for s in self.children:
            s.Update_position()

    def o_Render(self) -> 'pygame.Surface|None':
        return self.canvas.surface
        pass

    def get_true_pos(self) -> Vector:
        return self.shape.Get_true_pos()
        pass

    def Top_Render(self, canvas: 'Canvas'):
        '''Renders the container and all children. Additionally has the same effect as Container.Update_position().\n
        All methods that operate on all children go through the list of children in order (except child_at_position, which does so in reverse)'''
        canvas.Blits(self._render())
        pass

    def Top_Update(self, updater: 'Updater'):
        'calls o_Update for self and all children'
        self.o_Update(updater)
        for s in self.children:
            s.Top_Update(updater)
        pass

    def o_Update(self, updater: 'Updater'):
        pass

    def Add_container(self, container: 'Container'):
        self.children.append(container)
        container.parent = self
        container.shape.parent = self.shape

    def posInside(self, pos: Vector) -> tuple[Vector, bool]:
        "returns a tuple containing the pos's position relative to the container, and whether it is inside the container"
        return self.shape.posInside(pos)

    def posInsideOnly(self, pos: Vector) -> tuple[Vector, 0 | 1 | 2]:
        'same as posInside, but returns 2 if the position is also not inside any child containers'
        a, b = self.posInside(pos)
        if b:
            for s in self.get_children():
                if s.posInside(pos)[1]:
                    break
            else:
                return a, 2
            return a, 1
        else:
            return a, 0

    def Top_Render_surface(self):
        "NYI: renders self and all children into a surface so they don't have to be rendered individually every time"
        raise NotImplementedError()

    def child_at_position(self, pos: Vector) -> "tuple[Vector,Container]":
        """returns the child the position is inside of, and the position relative to the child\n
        returns None and the position relative to self if the position is outside self\n
        (first position, then the container)"""
        a, b = self.posInside(pos)
        for s in reversed(self.get_children()):
            c = s.child_at_position(pos)
            if c[1]:
                return c
        if b:
            return a, self
        return a, None

    def __getitem__(self, key):
        return self.children[key]

    def get_children(self): return self.children


if __name__ == '__main__':
    import renderText
    import Game1

    class A(Scene):

        def o_Init(self, updater: 'Updater'):
            self.w1 = Container(ContainerShape(vec(50, 50), vec(700, 700)))
            self.w1.canvas.Fill((0, 100, 100))
            self.w1.canvas.Line(vec(0, 0), vec(50, 25), 5, (100, 0, 0))

            self.w2 = Container(ContainerShape(vec(50, 50), vec(140, 140)))
            self.w2.canvas.Fill((0, 0, 100))
            self.w2.canvas.Line(vec(0, 0), vec(50, 25), 5, (100, 0, 0))
            self.w1.Add_container(self.w2)
            self.su = SubUpdater(Game1.init, Canvas(self.w1.canvas.surface), updater.get_inputs())
            # self.su.Init(updater)

        def o_Update(self, updater: 'Updater'):
            self.su.PlayOnce(updater)
            updater.get_canvas().Fill((200, 200, 200))
            self.w1.Update_position()
            a, b = self.w1.posInsideOnly(updater.get_inputs().get_mouse_position())
            if b == 2:
                if updater.get_inputs().keyPressed(pygame.K_s):
                    self.w1.canvas.Circle(a, 50, (0, 100, 200))
                if updater.get_inputs().keyPressed(pygame.K_d):
                    self.w1.canvas.Circle(a, 25, (0, 0, 200))
                self.w1.canvas.Circle(a, 5, (200, 200, 0))
            self.w1.Top_Render(updater.get_canvas())

    # Updater(A()).Play()
    class Dropdown(Container):
        is_open = True

        def __init__(self, shape: "ContainerShape|tuple[Vector,Vector]|tuple[float,float,float,float]", closeShape: "ContainerShape|tuple[Vector,Vector]|tuple[float,float,float,float]" = None, children: 'list[Container]' = None):
            super().__init__(shape, children=children)
            self.closeShape = ContainerShape(*(closeShape or self.shape))
            self.openShape = ContainerShape(*self.shape)
            self._canvases = [Canvas(self.closeShape.size), Canvas(self.openShape.size)]

        @property
        def canvas(self):
            return self._canvases[self.is_open]

        @canvas.setter
        def canvas(self, value):
            pass

        def get_children(self):
            if self.is_open:
                return super().get_children()
            else:
                return []

        def close(self):
            self.is_open = False
            self.shape.update(*self.closeShape)

        def open(self):
            self.is_open = True
            self.shape.update(*self.openShape)

    class B(Scene):
        def o_Init(self, updater: 'Updater'):
            self.w1 = Container((200, 100, 1200, 800), [
                Container((50, 50, 100, 100)),
                Dropdown((100, 100, 300, 500), (100, 100, 300, 100), [
                    Container((50, 50, 100, 100))
                ])
            ])
            self.w1.canvas.Fill((200, 200, 200))
            self.w1[1][0].canvas.Fill((200, 0, 200))

        def o_Update(self, updater: 'Updater'):
            mouse = updater.get_inputs().get_mouse_position()
            a, b = self.w1.child_at_position(mouse)
            if b:
                if updater.get_inputs().keyPressed(pygame.K_e):
                    b.canvas.Circle(a, 40, (100, 100, 100))
                if updater.get_inputs().keyPressed(pygame.K_q):
                    b.canvas.Circle(a, 40, (100, 00, 100))
                b.shape.pos += updater.get_inputs().WASD() * (1, -1)
                if isinstance(b, Dropdown):
                    if updater.get_inputs().keyDown(pygame.K_r):
                        b.close()
                    if updater.get_inputs().keyDown(pygame.K_f):
                        b.open()

            updater.get_canvas().Fill((100, 0, 100))
            self.w1.Top_Render(updater.get_canvas())
    Updater(B()).Play()
