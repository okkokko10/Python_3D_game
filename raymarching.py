import functools
from itertools import product
import math

import pygame
import orientation2 as oi
import numpy as np


# def rays(rotation: oi.Rotation, width: int, height: int):
#     def func(x, y):
#         return oi.rotate(rotation, np.array((x / width - 0.5, y / height - 0.5, 1)))
#     return np.transpose(np.array([*np.fromfunction(func, (width, height))]), (1, 2, 0))


def rays1(rotation: oi.Rotation, width: int, height: int, zoom: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    def func(x, y):
        return rotation @ np.array((x / zoom - 0.5 * width / zoom, y / zoom - 0.5 * height / zoom, 1), dtype=object)
    return np.fromfunction(func, (width, height))


def rays2(rotation: oi.Rotation, width: int, height: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    def func(x, y):
        return rotation @ np.array((x.flatten() / width - 0.5, y.flatten() / height - 0.5, 1), dtype=object)
    return np.fromfunction(func, (width, height))


# a = rays2(oi.IDENTITY, 8, 8)
# print(a)

class RayCamera:
    transform: oi.Transform

    def __init__(self, width: int, height: int, zoom: float) -> None:
        self.width = width
        self.height = height
        self.zoom = zoom
        self.transform = oi.Transform(oi.Vector3(0, 0, 0), oi.IDENTITY)
        pass

    def Draw(self, objects: 'Raymarch_list'):
        x, y, z = rays1(self.transform.rotation, self.width, self.height, self.zoom)
        lengths = np.zeros(shape=(self.width, self.height))
        for i in range(10):
            xl = x * lengths + self.transform.position[0]
            yl = y * lengths + self.transform.position[1]
            zl = z * lengths + self.transform.position[2]
            a = functools.reduce(np.fmin, (np.sqrt((xl - o.position[0])**2 + (yl - o.position[1]) **
                                 2 + (zl - o.position[2])**2) - o.radius for o in objects.spheres))
            lengths += a
        # lengths = np.asarray(lengths, dtype=int)
        # print(lengths)
        surface = pygame.Surface((self.width, self.height))
        # pxarray = pygame.PixelArray(surface)
        # lengths1 = np.fmin(lengths, 255)
        # print(lengths1)
        # pxarray[:, :] = lengths1
        # pxarray.close()
        a = pygame.surfarray.pixels_red(surface)
        a[:, :] = np.fmax(255 - lengths, 0).astype(np.uint8)
        return surface

    pass


class Raymarch_list:

    def __init__(self):
        self.spheres: list[Sphere] = []

    def prepare_for(self, camera: RayCamera):
        pass

    # def Localize_all(self, transform: oi.Transform):
    #     for o in self.objects:
    #         o.Localize(transform)

    def Add(self, obj: 'Raymarch_object'):
        self.spheres.append(obj)

    def least_distance(self, pos: oi.Vector3):
        return min(o.distance(pos) for o in self.spheres)


class Raymarch_object:
    position: oi.Vector3
    # localized_position: oi.Vector3
    color: tuple[int, int, int]

    # def Localize(self, transform: oi.Transform):
    #     self.localized_position = transform.LocalizePosition(self.position)
    def distance(self, pos: oi.Vector3):
        raise NotImplementedError()


class Sphere(Raymarch_object):
    def __init__(self, pos: oi.Vector3, radius: float, color: tuple[int, int, int]):
        self.position = pos
        self.radius = radius
        self.color = color
        # self.localized_position = None

    def distance(self, pos: oi.Vector3):
        return abs(math.dist(self.position - pos) - self.radius)
