from typing import Callable
import pygame
import pygame.gfxdraw
import numpy as np
from vector import *

pygame.init()


DEFAULT_FRAMERATE = 40

# Vector = np.ndarray


def vec(*args: 'float'):
    # return np.array(args)
    return Vector(*args)


class ObjectStorage:
    'Empty object for storing objects'
    pass


class Updater:
    "Updater.Play() to start"
    # "use Updater().Setup() to quickly initialize an updater, and updater.Play() to start"
    canvas: 'Canvas' = None
    inputs: 'Inputs' = None
    # updateFunction: 'Callable[[Updater],None]|None' = None
    scene: 'Scene|None' = None
    framerate = DEFAULT_FRAMERATE
    objects: 'ObjectStorage' = None

    _clock: 'pygame.time.Clock' = None
    _running: 'bool' = None
    deltaTime: 'int' = None

    def __init__(self, scene: 'Scene|None' = None, canvas: 'Canvas|bool' = True, inputs: 'Inputs|bool' = True, framerate: 'int' = DEFAULT_FRAMERATE, objectStorage=None):
        """setting canvas and inputs to True uses the default, and False disables them.\n
        init is a function that takes the updater as argument and is called once when updater.Play() is called\n
        init should return a function func\n
        func is a function that takes the updater as argument and is called every frame after updater.Play() is called\n
        func can be left as None. This can be useful if you want to just display a single image"""
        if canvas:
            self.canvas = Canvas(pygame.display.set_mode()) if canvas is True else canvas
        if inputs:
            self.inputs = Inputs() if inputs is True else inputs
        self.SetFramerate(framerate or DEFAULT_FRAMERATE)
        self.objects = objectStorage or ObjectStorage()
        if scene:
            self.scene = scene
        self._init()

    def Play(self):
        'func(self)'
        self._clock = pygame.time.Clock()
        self._running = True
        while self._running:
            self.deltaTime = self._clock.tick(self.framerate)
            if pygame.event.get(pygame.QUIT):
                self.Stop()
            self.events = pygame.event.get()
            if self.inputs:
                self._Update_inputs()
            if self.scene:
                self.scene.o_Update(self)

            pygame.display.update()
        return self

    def _Update_inputs(self):
        self.inputs.UpdateInputs(self.events, self.deltaTime)

    # def InitDisplayCanvas(self, canvas: 'Canvas' = None):
    #     self.canvas = canvas or Canvas(pygame.display.set_mode((800, 800)))
    #     return self.canvas

    # def InitInputs(self, inputs: 'Inputs' = None):
    #     self.inputs = inputs or Inputs()
    #     return self.inputs

    # def SetFunc(self, func):
    #     self.updateFunction = func

    def SetFramerate(self, framerate):
        self.framerate = framerate

    # def InitObjectStorage(self, objectStorage: 'ObjectStorage' = None):
    #     self.objects = objectStorage or ObjectStorage()

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

    def _init(self):
        if self.scene:
            self.scene.o_Init(self)


class SubUpdater(Updater):

    def __init__(self, scene: 'Callable[[Updater],None]|None' = None, canvas: 'Canvas|bool' = False, inputs: 'Inputs|bool' = False, objectStorage=None):
        'not ready yet'
        if canvas:
            self.canvas = Canvas(vec(800, 800)) if canvas == True else canvas
        self.objects = objectStorage or ObjectStorage()
        self.scene = scene
        if inputs:
            self.inputs = Inputs() if inputs == True else inputs
        self._init()

    # def Init(self, master):
    #     self.inputs = master.inputs

    def PlayOnce(self, master: 'Updater'):
        'func(self)'
        self.deltaTime = master.deltaTime
        self.events = master.events
        self.inputs = master.inputs
        if self.scene:
            self.scene.o_Update(self)
    pass


class Canvas:
    def __init__(self, surface: pygame.Surface | Vector):

        self.surface = surface if isinstance(surface, pygame.Surface) else pygame.Surface(tuple(surface))
        self.height = self.surface.get_height()
        self.width = self.surface.get_width()
        self.zoom = self.height
        self.ratio = self.width / self.height
        # self.default_font = pygame.font.Font(None, 20)

    def Line(self, pos1, pos2, width, color):
        pygame.draw.line(self.surface, color, self.convert(
            pos1), self.convert(pos2), int(width))

    def Lines(self, poslist, width, color):
        closed = False
        pygame.draw.lines(self.surface, color, closed, self.convertList(poslist), int(width))

    def Circle(self, pos, radius, color, width=0):
        pygame.draw.circle(self.surface, color, self.convert(pos), radius, int(width))

    def convert(self, pos):
        return (int(pos[0] * self.zoom) + self.width // 2, -int(pos[1] * self.zoom) + self.height // 2)

    def convertList(self, poslist):
        return [self.convert(pos) for pos in poslist]

    def Fill(self, color):
        self.surface.fill(color)

    def LockSurface(self):
        self.surface.lock()

    def UnlockSurface(self):
        self.surface.unlock()

    def TexturedPolygon(self, poslist, image):
        tx, ty = 0, 0
        if len(poslist) >= 3:
            pygame.gfxdraw.textured_polygon(self.surface, self.convertList(poslist), image, tx, ty)

    def StretchTexture(self, poslist, image):
        ''' The corners are in this order:\n
        3  4\n
        2  1'''
        xdensity = 4
        ydensity = 4
        xden = 4
        yden = 4
        pixellist = self.convertList(poslist)
        if len(pixellist) != 4:
            # print('wrong amount')
            return
        pxImage = pygame.PixelArray(image)
        # out = pygame.Surface((800, 800))
        out = self.surface
        xsurf, ysurf = out.get_size()
        pxOut = pygame.PixelArray(out)
        # a, b, d, c = pixellist
        d, b, a, c = pixellist
        ax, ay = a
        bx, by = b
        cx, cy = c
        dx, dy = d
        x = 0
        y = 0
        # (a*(1-y) + b*y)*(1-x)+(c*(1-y)+d*y)*x
        # a*(1-y) + b*y + ((c-a)*(1-y) + (d-b)*y)*x
        # a + y * (b-a) + x*(c-a+y*(d+a-c-b))
        hx = (dx + ax - cx - bx)
        hy = (dy + ay - cy - by)
        xsize, ysize = image.get_size()
        for y in range(0, ysize - yden, ydensity):
            row = pxImage[y]
            yd = y / ysize
            xa = ax + yd * (bx - ax)
            xk = cx - ax + yd * hx
            ya = ay + yd * (by - ay)
            yk = cy - ay + yd * hy
            for x in range(0, xsize - xden, xdensity):
                xd = x / xsize
                X = int(xa + xd * xk)
                Y = int(ya + xd * yk)
                if 0 < X < xsurf - xden and 0 < Y < ysurf - yden:
                    # u = row[x]
                    # try:

                    pxOut[X:X + xden, Y:Y + yden] = pxImage[x:x + xden, y:y + yden]
                    # pxOut[X, Y] = pxImage[x, y]
                    # except:
                    #     print(y, x, xsize, ysize)
                    #     pass

                pass
        pxOut.close()
        pxImage.close()
        return out

    # def Text(self, text, pos, color=(255, 255, 255), font=None):
    #     if not font:
    #         font = self.default_font
    #     t = font.render(text, False, color)
    #     self.surface.blit(t, pos)
    #     pass

    def Blit(self, source: 'pygame.Surface', dest: 'tuple[int,int]' = (0, 0)):
        self.surface.blit(source, tuple(dest))

    def BlitCanvas(self, source: 'Canvas', dest: 'tuple[int,int]' = (0, 0)):
        self.surface.blit(source.surface, tuple(dest))

    def Blits(self, sources: 'list[tuple[pygame.Surface,Vector]]'):
        self.surface.blits(sources)  # [(s, p) for p, s in sources])


class CanvasNoZoom(Canvas):
    def convert(self, pos):
        return int(pos[0]), int(pos[1])

    # def convertList(self, poslist):
    #     return [pos.f for pos in poslist]


class Inputs:
    # TODO: make it so every mouse movement event is recorded to create a path, not just the last one of the frame.
    #       make it so you can click or press a key multiple times per frame, and that they have a mouse position associated with them.
    #       An option for staggering inputs that have been pressed multiple times in one frame. Useful for the mouse wheel
    def __init__(self):
        self._ups = set()
        self._downs = set()
        self._pressed = {}
        self.mouse_movement = IntVec(0, 0)
        self.mouse_position = IntVec(0, 0)
        self._mouse_ups = set()
        self._mouse_downs = set()
        self._mouse_pressed = {}
        pass

    def _set_keyDown(self, key):
        self._downs.add(key)
        self._pressed[key] = 0
        return

    def _set_keyUp(self, key):
        self._ups.add(key)
        return

    def _set_mouseDown(self, button):
        self._mouse_downs.add(button)
        self._mouse_pressed[button] = 0
        return

    def _set_mouseUp(self, button):
        self._mouse_ups.add(button)
        return

    def UpdateInputs(self, events, deltaTime):
        for k in self._ups:
            if k in self._pressed:
                del self._pressed[k]
        for k in self._pressed:
            self._pressed[k] += deltaTime
        for k in self._mouse_ups:
            if k in self._mouse_pressed:
                del self._mouse_pressed[k]
        for k in self._mouse_pressed:
            self._mouse_pressed[k] += deltaTime
        self._ups.clear()
        self._downs.clear()
        self._mouse_ups.clear()
        self._mouse_downs.clear()
        self.mouse_movement = IntVec(0, 0)
        for e in events:
            if e.type == pygame.KEYDOWN:
                self._set_keyDown(e.key)
            elif e.type == pygame.KEYUP:
                self._set_keyUp(e.key)
            elif e.type == pygame.MOUSEMOTION:
                self.mouse_position = IntVec(*e.pos)
                self.mouse_movement += e.rel
            elif e.type == pygame.MOUSEBUTTONDOWN:
                self._set_mouseDown(e.button)
            elif e.type == pygame.MOUSEBUTTONUP:
                self._set_mouseUp(e.button)

    def keyPressed(self, key):
        return key in self._pressed

    def keyUp(self, key):
        return key in self._ups

    def keyDown(self, key):
        return key in self._downs

    def mousePressed(self, button):
        "1 left 2 middle 3 right 4 up 5 down 6 side lower 7 side upper"
        return button in self._mouse_pressed

    def mouseUp(self, button):
        "1 left 2 middle 3 right 4 up 5 down 6 side lower 7 side upper"
        return button in self._mouse_ups

    def mouseDown(self, button):
        "1 left 2 middle 3 right 4 up 5 down 6 side lower 7 side upper"
        return button in self._mouse_downs

    def LockMouse(self):
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def UnlockMouse(self):
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    def get_display(self):
        return pygame.display.get_surface()

    def get_mouse_movement(self): return self.mouse_movement
    def get_mouse_position(self): return self.mouse_position

    def WASD(self):
        return vec(self.keyPressed(pygame.K_d) - self.keyPressed(pygame.K_a),
                   self.keyPressed(pygame.K_w) - self.keyPressed(pygame.K_s))


class Scene:
    def __call__(self, updater: 'Updater'):
        'leave as is'
        self.o_Init(updater)
        return self.o_Update

    def __init__(self, *args, **kvargs):
        pass

    def o_Init(self, updater: 'Updater'):
        'runs when updater starts playing'
        pass

    def o_Update(self, updater: 'Updater'):
        'runs every frame'
        pass
