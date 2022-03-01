import functools
from itertools import product
import math

import pygame
import orientation2 as oi
import numpy as np
import facecamera

# def rays(rotation: oi.Rotation, width: int, height: int):
#     def func(x, y):
#         return oi.rotate(rotation, np.array((x / width - 0.5, y / height - 0.5, 1)))
#     return np.transpose(np.array([*np.fromfunction(func, (width, height))]), (1, 2, 0))


def rays(rotation: oi.Rotation, width: int, height: int, zoom: float, dtype=None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    def func(x, y):
        return rotation @ np.array((x / zoom - 0.5 * width / zoom, y / zoom - 0.5 * height / zoom, 1), dtype=object)
    x, y, z = np.fromfunction(func, (width, height), dtype=dtype)
    l = np.sqrt(x**2 + y**2 + z**2, dtype=dtype)
    x /= l
    y /= l
    z /= l
    return x, y, z


# def rays2(rotation: oi.Rotation, width: int, height: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
#     def func(x, y):
#         return rotation @ np.array((x.flatten() / width - 0.5, y.flatten() / height - 0.5, 1), dtype=object)
#     return np.fromfunction(func, (width, height))


# a = rays2(oi.IDENTITY, 8, 8)
# print(a)

class RayCamera:
    transform: oi.Transform

    def __init__(self, width: int, height: int, zoom: float, iteration_amount: int = 20) -> None:
        "depth is how many iterations"
        self.width = width
        self.height = height
        self.zoom = zoom
        self.transform = oi.Transform(oi.Vector3(0, 0, 0), oi.IDENTITY)
        self.iteration_amount = iteration_amount
        pass

    def Draw(self, objects: 'Raymarch_list'):
        floot = None
        x, y, z = rays(self.transform.rotation, self.width, self.height, self.zoom, dtype=floot)
        lengths = np.zeros(shape=(self.width, self.height), dtype=floot)

        def spheres(xl, yl, zl):
            return [np.fabs(np.sqrt((xl - o.position[0])**2 + (yl - o.position[1]) ** 2
                            + (zl - o.position[2])**2, dtype=floot) - o.radius) for o in objects.spheres] + [np.fabs(zl - 5)]  # last part is not generally part of the function

        def distance(xl, yl, zl):
            return functools.reduce(np.fmin, spheres(xl, yl, zl))  # *spheres(xl - 8, yl, zl)))

        def closest(xl, yl, zl):
            sp = spheres(xl, yl, zl)
            m = functools.reduce(np.fmin, sp)
            a = np.zeros(shape=(self.width, self.height), dtype=np.int64)

            for i, s in enumerate(sp):
                # o += 1
                a += (i) * (s <= m)
            # a = sp[0] <= m
            return m, a

        def positions() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
            xl = x * lengths + self.transform.position[0]
            yl = y * lengths + self.transform.position[1]
            zl = z * lengths + self.transform.position[2]
            return xl, yl, zl

        for i in range(self.iteration_amount):
            a = distance(*positions())
            lengths += a
        # lengths = np.asarray(lengths, dtype=int)
        # print(lengths)
        surface = pygame.Surface((self.width, self.height))
        # pxarray = pygame.PixelArray(surface)
        # lengths1 = np.fmin(lengths, 255)
        # print(lengths1)
        # pxarray[:, :] = lengths1
        # pxarray.close()
        pos = positions()
        distance_to_closest, closest_object = closest(*pos)
        face = pygame.transform.flip(facecamera.GetPhotos(), 0, 1)
        face_colors = pygame.surfarray.pixels3d(face)
        colors = pygame.surfarray.pixels3d(surface)
        # red = pygame.surfarray.pixels_red(surface)
        # green = pygame.surfarray.pixels_green(surface)
        # blue = pygame.surfarray.pixels_blue(surface)
        # colors[:, :, 0] = np.clip(((100 * clo + 50)) * (1 - dis), 0, 255).astype(np.uint8)
        # colors[:, :, 1] = np.clip(127 + pos[1] * 10, 0, 256).astype(np.uint8)
        # colors[:, :, 2] = np.clip(255 - dis * 1000, 0, 256).astype(np.uint8)

        def triple(arr: np.ndarray):
            return np.array((arr, arr, arr)).transpose((1, 2, 0))
        poscol = (np.asarray(pos).transpose((1, 2, 0)) + 0.5) % 1 * 255

        isdis = triple((closest_object < 2))
        colors[:, :, :] = np.where(isdis, face_colors[(np.clip((pos[0] / 4 + 0.5) % 1, 0, 1) * (face.get_width() - 1)).astype(np.uint16),
                                                      (np.clip((pos[1] / 4 - 0.5) % 1, 0, 1) * (face.get_height() - 1)).astype(np.uint16)], poscol)
        center = self.width // 2, self.height // 2
        info = ["distance from camera: %s" % round(lengths[center], 5),
                "coordinates: %s" % [round(pos[i][center], 5) for i in range(3)],
                "color: %s" % colors[center],
                "closest object: %s" % closest_object[center],
                "distance to closest object: %s" % distance_to_closest[center],
                "size: %s %s" % (self.width, self.height),
                "zoom: %s" % self.zoom,
                "iterations: %s" % self.iteration_amount]
        return surface, info

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


# import timeit
# t = timeit.Timer(lambda: (rays(oi.elemental_rotation_y(2), 2000, 2000, 2000))).autorange()
# print(t)
