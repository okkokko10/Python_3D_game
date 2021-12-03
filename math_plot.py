import pygame
import numpy as np
import time
import math


class Plotter:
    def __init__(self, func: 'lambda x,y:x'):
        self.func = func
        pass

    def Graph(self, width: int, height: int, x0: float = 0, y0: float = 0):
        return pygame.surfarray.make_surface(np.fromfunction(self.func, (width, height), dtype=int))


dis = pygame.display.set_mode((1024 / 8, 1024 / 8))

for i in range(100):
    g = i / 100

    def f1(x, y):
        return (((x - 100)**2 + (y - 400)**2)) / (g)

    def f2(x, y):
        return (((y) + x - 800)) % (y)

    def f3(x, y):
        p = 16
        q = 1024 / p / 2
        x1 = (x // q)
        y1 = (y // q)
        return (x1) * 255

    def F2(x, y):
        # print('F2', int(x), type(x))
        return dis.map_rgb(pygame.Color(int(x) % 255, 0, 0))

    def F1(x, y):

        return list(map(F2, x, y))

    def f4(x: np.ndarray, y: np.ndarray):
        print(x)
        h = np.array(list(map(F1, x, y)))
        print(h)
        print(type(x))
        return h
    f = f4
    old = time.perf_counter()
    a = Plotter(f).Graph(*dis.get_size())
    print(time.perf_counter() - old)
    dis.blit(a, (0, 0))
    pygame.display.update()
    pygame.time.wait(1000)
    if pygame.event.get(pygame.QUIT):
        break
    pygame.event.get()
# x = b*1 + g*4
