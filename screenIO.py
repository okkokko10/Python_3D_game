"A module for using pygame. by Okko Heiniö"
from collections import Counter
import itertools
from typing import Callable
import pygame
import pygame.gfxdraw
# import numpy as np
from vector import *

pygame.init()


DEFAULT_FRAMERATE = 40

# Vector = np.ndarray


def vec(*args: 'float'):
    # return np.array(args)
    return Vector(*args)


# TODO: an info attribute to updater, that tells things like age. or just an age attribute
# Actually, maybe add that to scene


class Updater:
    "Updater.Play() to start"
    # "use Updater().Setup() to quickly initialize an updater, and updater.Play() to start"
    canvas: 'Canvas' = None
    inputs: 'Inputs' = None
    # updateFunction: 'Callable[[Updater],None]|None' = None
    scene: 'Scene|None' = None
    framerate = DEFAULT_FRAMERATE

    _clock: 'pygame.time.Clock' = None
    _running: 'bool' = None
    deltaTime: 'int' = None
    screenshotter: 'Screenshotter' = None

    def __init__(self, scene: 'Scene|None' = None, canvas: 'Canvas|bool' = True, inputs: 'Inputs|bool' = True, framerate: 'int' = DEFAULT_FRAMERATE):
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
        if scene:
            self.scene = scene
        self.screenshotter = Screenshotter()
        self._init()

    def Play(self):
        'func(self)'
        self._clock = pygame.time.Clock()
        self._running = True
        while self._running:
            self.deltaTime = self._clock.tick(self.framerate)
            if pygame.event.get(pygame.QUIT):
                self.Stop()
                break
            self.events = pygame.event.get()
            if self.inputs:
                self._Update_inputs()
            if self.scene:
                self.scene.o_Update(self)

            pygame.display.update()
            self.screenshotter.update(self)
        if self.scene:
            self.scene.o_Quit(self)
        if self.canvas and self.canvas.surface is pygame.display.get_surface():
            pygame.display.quit()

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

    def get_canvas(self):
        return self.canvas

    def get_framerate(self):
        return self.framerate

    def get_inputs(self):
        return self.inputs

    def get_deltaTime(self):
        "time since last frame, in milliseconds"
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

    def __init__(self, scene: 'Callable[[Updater],None]|None' = None, canvas: 'Canvas|bool' = False, inputs: 'Inputs|bool' = False):
        'not ready yet'
        if canvas:
            self.canvas = Canvas(vec(800, 800)) if canvas == True else canvas
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
        self.zoom = 1
        self.ratio = self.width / self.height
        # self.default_font = pygame.font.Font(None, 20)

    def Line(self, pos1, pos2, width, color):
        try:
            pygame.draw.line(self.surface, color, self.convert(
                pos1), self.convert(pos2), int(width))
        except TypeError as e:
            print("line 163 in screenIO")
            print(e)
            print(pos1, pos2)
            print(self.convert(pos1), self.convert(pos2))

    def Lines(self, poslist, width, color):
        closed = False
        pygame.draw.lines(self.surface, color, closed, self.convertList(poslist), int(width))

    def Circle(self, pos, radius, color, width=0):
        pygame.draw.circle(self.surface, color, self.convert(pos), radius, int(width))

    def convert(self, pos):
        return int(pos[0]), int(pos[1])

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
        "does not use zoom, instead uses pixels"
        # try:
        self.surface.blit(source, tuple(dest))
        # except TypeError:
        #     if all(isinstance(i, int) for i in dest) and len(dest) == 2:
        #         pass
        #     else:
        #         raise TypeError(f"{dest} is not a valid destination position")
        #     pass

    def BlitCanvas(self, source: 'Canvas', dest: 'tuple[int,int]' = (0, 0)):
        self.surface.blit(source.surface, tuple(dest))

    def Blits(self, sources: 'list[tuple[pygame.Surface,Vector]]'):
        self.surface.blits(sources)  # [(s, p) for p, s in sources])

    def GroupLines(self, positions: Iterable, width, color):
        "draw lines from every point to every other point"
        for a, b in itertools.combinations(positions, 2):
            self.Line(a, b, width, color)

    @property
    def size(self):
        return Vector(self.width, self.height)

    @property
    def center(self):
        "center pixel"
        return Vector(self.width // 2, self.height // 2)


class CanvasZoom(Canvas):
    def __init__(self, surface: pygame.Surface | Vector):
        super().__init__(surface)
        self.zoom = self.height

    def convert(self, pos):
        return (int(pos[0] * self.zoom) + self.width // 2, -int(pos[1] * self.zoom) + self.height // 2)

    # def convertList(self, poslist):
    #     return [pos.f for pos in poslist]

# TODO: a class for specific inputs up and down, that can do or and and, that can be fed to Inputs instead of pygame.K_{key}
# make it so down and up always correspond with the start and end of pressed


class Inp:
    def __init__(self, name: str, *, _key: int = None):
        """name is either a valid input to pygame.key.key_code()
        or a string with two words, the first being mouse, and the second being one of these:
            left, middle, right, up, down, side lower, side upper
        or a number corresponding to them.

        # inp>inputs tells if inp is down
        # inp<inputs tells if inp is up
        # inp==inputs tells if inp is pressed
        inp|inp combines two inps
        """
        name = name.lower()
        self.name = name
        mousewords = [None, "left", "middle", "right", "up", "down", "side lower", "side upper"]
        m = name.split(maxsplit=1)
        if m[0] in {"mouse"}:
            self.is_mouse = True
            self.key = mousewords.index(m[1])
        else:
            self.is_mouse = False
            self.key = _key or pygame.key.key_code(name)

    def fits(self, inputs: 'Inputs', press: int) -> bool:
        """
        match press: 
            case 0: pressed
            case 1: down
            case 2: up
        """
        match press:
            case 0:
                if self.is_mouse:
                    return inputs.mousePressed(self.key)
                else:
                    return inputs.keyPressed(self.key)
            case 1:
                if self.is_mouse:
                    return inputs.mouseDown(self.key)
                else:
                    return inputs.keyDown(self.key)
            case 2:
                if self.is_mouse:
                    return inputs.mouseUp(self.key)
                else:
                    return inputs.keyUp(self.key)

    def __or__(self, other: 'Inp'):
        if isinstance(other, Inp):
            return InpOr(self, other)

    # def __mul__(self, inputs: 'Inputs'):
    #     if isinstance(inputs, Inputs):
    #         return self.fits(inputs, 0)

    # def __add__(self, inputs: 'Inputs'):
    #     if isinstance(inputs, Inputs):
    #         return self.fits(inputs, 1)

    # def __sub__(self, inputs: 'Inputs'):
    #     if isinstance(inputs, Inputs):
    #         return self.fits(inputs, 2)


class InpOr(Inp):
    def __init__(self, *inps: Inp):
        self.inps = inps

    def states(self, inputs: 'Inputs', press: int):
        return [i for i in self.inps if i.fits(inputs, press)]

    def fits(self, inputs: 'Inputs', press: int) -> bool:
        match press:
            case 0:
                return bool(self.states(inputs, 0))
            case 1:
                # if there are inps that are pressed but not down, that means they were already pressed
                a = self.states(inputs, 1)
                return bool(a and self.states(inputs, 0) == a)
            case 2:
                a = self.states(inputs, 2)
                return bool(a and self.states(inputs, 0) == a)


# class InpInverse(Inp):
#     def __init__(self, inp: Inp):
#         self.inp = inp

#     def fits(self, inputs: 'Inputs'):
#         return not self.inp.fits(inputs)


class Inputs:
    """ up and down are true right away. 
    pressed is true on the frames up or down is true, 
    and between, but not after or before.
    up and down can be both true at the same time, if a key is tapped quickly enough"""
    # TODO: make it so every mouse movement event is recorded to create a path, not just the last one of the frame.
    #       make it so you can click or press a key multiple times per frame, and that they have a mouse position associated with them.
    #       An option for staggering inputs that have been pressed multiple times in one frame. Useful for the mouse wheel

    def __init__(self):
        self._ups = Counter()
        self._downs = Counter()
        self._pressed = {}
        self.mouse_movement = Vector(0, 0)
        self._mouse_ups = Counter()
        self._mouse_downs = Counter()
        self._mouse_pressed = {}
        self._mouse_path: list[Vector] = [Vector(0, 0)]  # TODO: make it possible to see whether mouse buttons are pressed at a point in the path
        pass

    def _set_keyDown(self, key):
        self._downs.update((key,))
        self._pressed[key] = 0
        return

    def _set_keyUp(self, key):
        self._ups.update((key,))
        return

    def _set_mouseDown(self, button):
        self._mouse_downs.update((button,))
        self._mouse_pressed[button] = 0
        return

    def _set_mouseUp(self, button):
        self._mouse_ups.update((button,))
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
        self.mouse_movement = Vector(0, 0)
        self._mouse_path = [self._mouse_path[-1]]
        for e in events:
            if e.type == pygame.KEYDOWN:
                self._set_keyDown(e.key)
            elif e.type == pygame.KEYUP:
                self._set_keyUp(e.key)
            elif e.type == pygame.MOUSEMOTION:
                self._mouse_path.append(Vector(*e.pos))
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
    def get_mouse_position(self): return self._mouse_path[-1]
    def get_mouse_path(self): return self._mouse_path

    def get_mousewheel(self):
        return self._mouse_downs[4] - self._mouse_downs[5] + self.pseudo_get_mousewheel()

    def pseudo_get_mousewheel(self):
        "keypad 7 and 1"
        return self._downs[pygame.K_KP7] - self._downs[pygame.K_KP1]

    def from_names(self, names: tuple[str], press: int):
        return InpOr(*(Inp(n) for n in names)).fits(self, press)

    def Pressed(self, *names: str):
        return self.from_names(names, 0)

    def Down(self, *names: str):
        return self.from_names(names, 1)

    def Up(self, *names: str):
        return self.from_names(names, 2)

    def arrow_WASD_vector(self):
        return Vector(self.Pressed("right", "d") - self.Pressed("left", "a"), self.Pressed("up", "w") - self.Pressed("down", "s"))

    def arrows_vector(self):
        return Vector(self.Pressed("right") - self.Pressed("left"), self.Pressed("up") - self.Pressed("down"))

    def WASD_vector(self):
        return Vector(self.keyPressed(pygame.K_d) - self.keyPressed(pygame.K_a),
                      self.keyPressed(pygame.K_w) - self.keyPressed(pygame.K_s))
    WASD = WASD_vector
    "old name"


class screenIO:
    "this is so my IDE won't say the below typehints are wrong"
    Updater: type[Updater]


del screenIO


class Scene:
    def __call__(self, updater: 'screenIO.Updater'):
        'leave as is'
        self.o_Init(updater)
        return self.o_Update

    def __init__(self, *args, **kvargs):
        pass

    def o_Init(self, updater: 'screenIO.Updater'):
        'runs when updater starts playing'
        pass

    def o_Update(self, updater: 'screenIO.Updater'):
        'runs every frame'
        pass

    def o_Quit(self, updater: 'screenIO.Updater'):
        'runs when quitting'
        pass


class Screenshotter:
    def __init__(self, key="return"):
        self.key = key

    def update(self, updater: Updater):
        if updater.inputs.Down(self.key):
            self.take(updater)

    def take(self, updater: Updater):
        try:
            if not pygame.scrap.get_init():
                pygame.scrap.init()
        except pygame.error:
            print("screenshot failed: can't initialize clipboard")
        else:
            imagename = "ignore_saved_image.bmp"
            pygame.image.save(pygame.display.get_surface(), imagename)
            with open(imagename, "rb") as fp:
                pygame.scrap.put(pygame.SCRAP_BMP, fp.read())

            # bytes(pygame.image.tostring(pygame.display.get_surface(), "RGB")))
