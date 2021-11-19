import random
import pygame

from orientation import *


class ObjectStorage:
    'Empty object for storing objects'
    pass


class Updater:
    "use Updater().Setup() to quickly initialize an updater"
    canvas: 'Canvas' = None
    inputs: 'Inputs' = None
    func = None
    framerate = None
    objects: 'ObjectStorage' = None

    _clock: 'pygame.time.Clock' = None
    _running: 'bool' = None
    deltaTime: 'int' = None

    def Setup(self, func=None, canvas=None, inputs=None, framerate=None, objectStorage=None):
        "func is a function that takes the updater as argument and is called every frame after updater.Play() is called"
        if canvas or not self.canvas:
            self.InitDisplayCanvas(canvas)
        if inputs or not self.inputs:
            self.InitInputs(inputs)
        if func:
            self.SetFunc(func)
        if framerate or not self.framerate:
            DEFAULT_FRAMERATE = 40
            self.SetFramerate(framerate or DEFAULT_FRAMERATE)
        if objectStorage or not self.objects:
            self.InitObjectStorage(objectStorage)
        return self

    def Play(self):
        'func(self)'
        self._clock = pygame.time.Clock()
        self._running = True
        while self._running:
            self.deltaTime = self._clock.tick(self.framerate)
            if pygame.event.get(pygame.QUIT):
                self.Stop()
            self.events = pygame.event.get()
            self._Update_inputs()
            self.func(self)

            pygame.display.update()
        return self

    def _Update_inputs(self):
        self.inputs.UpdateInputs(self.events, self.deltaTime)

    def InitDisplayCanvas(self, canvas: 'Canvas' = None):
        self.canvas = canvas or Canvas(pygame.display.set_mode((800, 800)))
        return self.canvas

    def InitInputs(self, inputs: 'Inputs' = None):
        self.inputs = inputs or Inputs()
        return self.inputs

    def SetFunc(self, func):
        self.func = func

    def SetFramerate(self, framerate):
        self.framerate = framerate

    def InitObjectStorage(self, objectStorage: 'ObjectStorage' = None):
        self.objects = objectStorage or ObjectStorage()

    def get_canvas(self):
        return self.canvas

    def get_framerate(self):
        return self.framerate

    def get_inputs(self):
        return self.inputs

    def get_objects(self):
        return self.objects

    def get_deltaTime(self):
        return self.deltaTime

    def get_events(self):
        return self.events

    def Stop(self):
        self._running = False
        return


class Canvas:
    def __init__(self, surface: pygame.surface.Surface):
        self.surface = surface
        self.height = surface.get_height()
        self.width = surface.get_width()

    def Line(self, pos1, pos2, width, color):
        pygame.draw.line(self.surface, color, self.convert(
            pos1), self.convert(pos2), width)

    def Lines(self, poslist, width, color):
        closed = False
        pygame.draw.lines(self.surface, color, closed, [
                          self.convert(pos) for pos in poslist], width)

    def Circle(self, pos, radius, color):
        pygame.draw.circle(self.surface, color, self.convert(pos), radius)

    def convert(self, pos):
        return (int(pos[0]*self.width)+self.width//2, -int(pos[1]*self.height)+self.height//2)

    def Fill(self, color):
        self.surface.fill(color)

    def LockSurface(self):
        self.surface.lock()

    def UnlockSurface(self):
        self.surface.unlock()


class Camera:
    def __init__(self):
        self.transform = Transform(Vector(0, 0, 0), Quaternion(1))
        self.height = 1
        self.width = 1

    def ProjectPosition(self, other: 'Vector'):
        p = self.transform.LocalizePosition(other)
        if p.k <= 0:
            return None
        if abs(p.i)*2 > self.width*p.k or abs(p.j)*2 > self.height*p.k:
            return None
        x, y = p.i/p.k, p.j/p.k
        return x, y

    def DrawLines(self, canvas: 'Canvas', vectors, width, color):
        poslist = [p for p in (self.ProjectPosition(v) for v in vectors) if p]
        if len(poslist) >= 2:
            canvas.Lines(poslist, width, color)

    def DrawDots(self, canvas: 'Canvas', vectors, radius, color):
        for v in vectors:
            p = self.ProjectPosition(v)
            if p:
                canvas.Circle(p, radius, color)
            pass


class Inputs:
    def __init__(self):
        self.ups = set()
        self.downs = set()
        self.helds = {}
        pass

    def _setDown(self, key):
        self.downs.add(key)
        self.helds[key] = 0
        return

    def _setUp(self, key):
        self.ups.add(key)
        return

    def UpdateInputs(self, events, deltaTime):
        for k in self.ups:
            del self.helds[k]
        for k in self.helds:
            self.helds[k] += deltaTime
        self.ups.clear()
        self.downs.clear()
        for e in events:
            if e.type == pygame.KEYDOWN:
                self._setDown(e.key)
            elif e.type == pygame.KEYUP:
                self._setUp(e.key)

    def IsHeld(self, key):
        return key in self.helds

    def IsUp(self, key):
        return key in self.ups

    def IsDown(self, key):
        return key in self.downs

    def LockMouse(self):
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def UnlockMouse(self):
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)


if __name__ == '__main__':

    C = Camera()
    C.transform.position = Vector(0, 0, 0)

    # den = 5
    # points = [Vector(i, j, k)/den for i in range(3*den) for j in range(3*den) for k in range(3*den)]
    # points += [Vector(i/den, 0, k/den) for i in range(-3*den, 6*den) for k in range(-3*den, 6*den)]

    points = [Vector(random.random()*2-1,  random.random()*2-1, random.random()*0.1+2) for _ in range(500)]

    mx, my = 0, 0

    def update(updater: 'Updater'):
        canvas = updater.get_canvas()
        inputs = updater.get_inputs()
        events = updater.get_events()
        deltaTime = updater.get_deltaTime()
        canvas.Fill((0, 0, 100))
        canvas.LockSurface()
        # C.DrawLines(canvas, points, 5, (100, 0, 100))
        C.DrawDots(canvas, points, 5, (100, 0, 000))
        canvas.UnlockSurface()
        # for e in events:
        #     print(e)
        global mx, my
        mdx, mdy = pygame.mouse.get_rel()
        mx += mdx
        my += mdy
        # C.transform.rotation *= Vector(1,0,0).RotationAround(-mdy/400)*(Vector(0,1,0).RotationAround(-mdx/400))
        rotationX = Vector(0, 1, 0).RotationAround(mx/200)
        rotationY = Vector(1, 0, 0).RotationAround(my/200)
        WASDvector = Vector(inputs.IsHeld(pygame.K_d)-inputs.IsHeld(pygame.K_a), 0,
                            inputs.IsHeld(pygame.K_w)-inputs.IsHeld(pygame.K_s))

        C.transform.rotation = rotationX * rotationY
        C.transform.position += rotationX.Rotate(WASDvector*deltaTime*0.001)

        if inputs.IsDown(pygame.K_t):
            inputs.LockMouse()
        if inputs.IsDown(pygame.K_y):
            inputs.UnlockMouse()

        return

    Upd = Updater().Setup(func=update, framerate=40)

    Upd.get_inputs().LockMouse()

    Upd.Play()
