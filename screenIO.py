import pygame
import pygame.gfxdraw


class ObjectStorage:
    'Empty object for storing objects'
    pass


class Updater:
    "use Updater().Setup() to quickly initialize an updater, and updater.Play() to start"
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
        self.zoom = self.height
        self.ratio = self.width / self.height

    def Line(self, pos1, pos2, width, color):
        pygame.draw.line(self.surface, color, self.convert(
            pos1), self.convert(pos2), width)

    def Lines(self, poslist, width, color):
        closed = False
        pygame.draw.lines(self.surface, color, closed, self.convertList(poslist), width)

    def Circle(self, pos, radius, color):
        pygame.draw.circle(self.surface, color, self.convert(pos), radius)

    def convert(self, pos):
        return (int(pos[0]*self.zoom)+self.width//2, -int(pos[1]*self.zoom)+self.height//2)

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
        hx = (dx+ax-cx-bx)
        hy = (dy+ay-cy-by)
        xsize, ysize = image.get_size()
        for y in range(0, ysize-yden, ydensity):
            row = pxImage[y]
            yd = y/ysize
            xa = ax + yd * (bx-ax)
            xk = cx - ax + yd*hx
            ya = ay + yd * (by-ay)
            yk = cy - ay + yd*hy
            for x in range(0, xsize-xden, xdensity):
                xd = x / xsize
                X = int(xa+xd*xk)
                Y = int(ya+xd*yk)
                if 0 < X < xsurf-xden and 0 < Y < ysurf-yden:
                    # u = row[x]
                    # try:

                    pxOut[X:X+xden, Y:Y+yden] = pxImage[x:x+xden, y:y+yden]
                    # except:
                    #     print(y, x, xsize, ysize)
                    #     pass

                pass
        pxOut.close()
        pxImage.close()
        return out


class Inputs:
    def __init__(self):
        self.ups = set()
        self.downs = set()
        self.pressed = {}
        self.mouse_movement = [0, 0]
        self.mouse_position = 0, 0
        pass

    def _set_keyDown(self, key):
        self.downs.add(key)
        self.pressed[key] = 0
        return

    def _set_keyUp(self, key):
        self.ups.add(key)
        return

    def UpdateInputs(self, events, deltaTime):
        for k in self.ups:
            del self.pressed[k]
        for k in self.pressed:
            self.pressed[k] += deltaTime
        self.ups.clear()
        self.downs.clear()
        self.mouse_movement = [0, 0]
        for e in events:
            if e.type == pygame.KEYDOWN:
                self._set_keyDown(e.key)
            elif e.type == pygame.KEYUP:
                self._set_keyUp(e.key)
            elif e.type == pygame.MOUSEMOTION:
                self.mouse_position = e.pos
                self.mouse_movement[0] += e.rel[0]
                self.mouse_movement[1] += e.rel[1]

    def keyPressed(self, key):
        return key in self.pressed

    def keyUp(self, key):
        return key in self.ups

    def keyDown(self, key):
        return key in self.downs

    def LockMouse(self):
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def UnlockMouse(self):
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    def get_display(self):
        return pygame.display.get_surface()

    def get_mouse_movement(self): return self.mouse_movement
