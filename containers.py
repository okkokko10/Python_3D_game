
from screenIO import *

# Vector = np.ndarray
# class Vector2(np.ndarray):
#     def __new__(cls, x,y):
#         return np.array()
#         pass


class ContainerShape:
    def __init__(self, pos: 'Vector', size: 'Vector'):
        self.container: 'Container' = None
        self.parent: 'ContainerShape' = None
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
        "returns a tuple containing the pos's position relative to the container, and whether it is inside the container"
        a = pos - self.true_pos
        if ((0, 0) <= a).all() and (a < self.size).all():
            return a, True
        else:
            return a, False
    pass


class Container:
    parent: 'Container|None' = None
    # func_OnClick: Callable[[Updater], None] = None

    def __init__(self, shape: 'ContainerShape', children: 'list[Container]' = None, listening=False):
        self.shape = shape
        self.shape.container = self
        self.children = children or []
        for child in self.children:
            child.parent = self
            child.shape.parent = self.shape
        self.canvas = CanvasNoZoom(self.shape.size)
        self.listening = listening  # whether the container should listen to inputs

    def _render(self) -> list[tuple[pygame.Surface, Vector]]:
        blit_sequence = (self.o_Render(), self.get_true_pos())  # , None, pygame.BLEND_RGB_SUB)
        a = [blit_sequence] if blit_sequence[0] else []
        for s in self.children:
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
        'Renders the container and all children. Additionally has the same effect as Container.Update_position().'
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
            for s in self.children:
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

    Updater(A()).Play()
