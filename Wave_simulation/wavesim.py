import itertools
import os
import random
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import screenIO
import numpy as np
import pygame
import renderText


# ideas:
# other values a tile can have:
#   spread: how wide is the cone it can go?
#   change: how much of the tile is left behind and how much goes away. change_ratio, but local
#   destroys particles without this value
# some way to make small mass particles be attracted to each other, and large mass particles be split up.
# elastic collision
# 3d
# change the shape from 400,300,3 to 3,400,300


def pythagoras(a, b):
    return a**2 + b**2


def complex_mul(ax, ay, bx, by):
    return ax * bx - ay * by, ax * by + ay * bx


def sigmoid(a: np.ndarray):
    return 1.0 / (1.0 + np.exp(-a))


def color_map(a: np.ndarray):
    return 1.0 - 1.0 / (np.fabs(a) + 1.0)


def random_round_2d(a: np.ndarray, b: np.ndarray):
    "mean should be 1"
    # ra, rb = random.random(), random.random()
    ra, rb = np.random.rand(*a.shape), np.random.rand(*a.shape)
    # ra = rb
    sx, sy = complex_mul(ra, rb, 1, -1)
    # sx = ra + 0.5
    # sy = ra * (rb - 0.5)
    sy *= np.fabs(sy)
    # sx *= 1
    # sx *= 3  # the mean should be 1
    # w = 0.9
    # sx = sx * w + (1 - w)
    # sy = sy * w
    w = 1
    oa, ob = complex_mul(a, b, sx * w + (1 - w), sy)
    return np.round(oa).astype(int), np.round(ob).astype(int)


class WaveGrid:
    def __init__(self, size: tuple[int, int] = (400, 300)):
        self.size = size[0], size[1]
        self.grid = np.zeros((3, *self.size), float)
        "grid[0,x,y] and grid[1,x,y] is the velocity at x,y grid[2,x,y] is the mass"
        self.change_ratio = 0.05
        "how much one update changes the board"
        self.addboard: np.ndarray = np.zeros((3, *self.size), float)
        self.ind = np.indices(self.size)
        self.intensity = 16
        self.stickiness = 0.5

    def next_frame(self):

        self.addboard[...] = 0
        a1, b1 = random_round_2d(self.grid[0, :, :] / self.grid[2, :, :], self.grid[1, :, :] / self.grid[2, :, :])
        # toind = ((self.ind[:, :, :] + np.stack((a1, b1), 0)).astype(int) % np.array(self.size)[:, np.newaxis, np.newaxis])
        toind = ((self.ind[0, :, :] + a1).astype(int) % self.size[0],
                 (self.ind[1, :, :] + b1).astype(int) % self.size[1])

        # bo /= np.linalg.norm(bo, axis=0)
        # np.nan_to_num(bo, copy=False)

        # np.add.at(self.addboard[0], (*toind,), self.grid[0])
        # np.add.at(self.addboard[1], (*toind,), self.grid[1])
        # np.add.at(self.addboard[2], (*toind,), self.grid[2])
        values = (self.grid * np.array([1 + self.stickiness, 1 + self.stickiness, 1])[:, np.newaxis, np.newaxis] - self.stickiness *
                  self.grid[2, :, :] * np.stack((a1, b1, np.zeros(a1.shape, float)), axis=0))
        np.add.at(self.addboard.transpose(1, 2, 0), (*toind,), values.transpose(1, 2, 0))

        # e1 = 1 / (1 + 10 * self.addboard[:, :, 2][:, :, np.newaxis]) - 0.1
        # self.addboard[:, :, 0:2] += self.addboard[:, :, 1::-1] * np.array([1, -1]) * e1
        # self.addboard[:, :, 0:2] /= (e1**2 + 1)**0.5
        return self.addboard

    def apply(self, addboard: np.ndarray):

        decay_ratio = 1
        self.grid *= 1 - self.change_ratio
        self.grid[...] += addboard[...] * self.change_ratio
        self.grid[...] *= decay_ratio

    def Update(self):
        for i in range(1):
            addboard = self.next_frame()
            self.apply(addboard)

    def Draw(self):
        surface = pygame.surface.Surface(self.size)
        colors = pygame.surfarray.pixels3d(surface)
        lengths = np.sqrt(self.grid[0, :, :]**2 + self.grid[1, :, :]**2)
        colors[:, :, 0] = color_map(lengths * self.grid[2, :, :] * 0.1 * self.intensity) * 200
        colors[:, :, 1] = color_map(self.grid[2, :, :] * self.intensity) * 255
        colors[:, :, 2] = color_map(lengths * 0.1 * self.intensity) * 255

        return surface

    @property
    def gridT(self):
        return self.grid.transpose(1, 2, 0)


class Scene_1(screenIO.Scene):
    def o_Init(self, updater: 'screenIO.Updater'):
        a = 8
        self.waves = WaveGrid(
            np.array(updater.canvas.surface.get_size()) // a)

        self.brush_size = 60

        def func(x, y):
            a = (x - self.brush_size / 2)**2 + (y - self.brush_size / 2)**2
            return 10 / ((a) + 1) * (a < self.brush_size**2 / 4)
        self.brush = np.fromfunction(func, (self.brush_size, self.brush_size))
        self.render_text = renderText.RenderText(15)

    def o_Update(self, updater: 'screenIO.Updater'):
        mouse_position = np.array(updater.inputs.get_mouse_position())
        mouse_movement = np.array(updater.inputs.get_mouse_movement())
        if updater.inputs.Pressed("w"):
            mouse_position %= self.waves.size
            # mouse_movement %= self.waves.size
        else:
            mouse_position = mouse_position * self.waves.size / updater.canvas.surface.get_size()
            mouse_movement = mouse_movement * self.waves.size / updater.canvas.surface.get_size()

        # print(mouse_position, mouse_movement)

        def get_brush():
            if updater.inputs.Pressed("q"):
                return self.brush != 0
            else:
                return self.brush

        try:
            if updater.inputs.Down("t"):
                self.waves.gridT[...] = 0
            if updater.inputs.Down("y"):
                self.waves.gridT[..., 0:2] = 0
            if updater.inputs.Up("r"):
                start_mass = 1
                self.waves.gridT[:, :] += np.append(mouse_movement, start_mass)
            if updater.inputs.Up("mouse left") or updater.inputs.Pressed("d"):
                start_mass = 1
                start_motion = 1
                if updater.inputs.Pressed("a"):
                    start_motion *= 5
                mx, my = np.round(mouse_position - self.brush_size / 2).astype(int)
                self.waves.gridT[mx:mx + self.brush_size, my:my + self.brush_size] += 1 * \
                    np.append(mouse_movement * start_motion, start_mass)[np.newaxis, np.newaxis, :] * get_brush()[:, :, np.newaxis]
            if updater.inputs.Pressed("f"):
                start_mass = 1
                start_motion = 0
                mx, my = np.round(mouse_position - self.brush_size / 2).astype(int)
                self.waves.grid[:, mx:mx + self.brush_size, my:my + self.brush_size] += 1 * \
                    np.append(mouse_movement * start_motion, start_mass)[:, np.newaxis, np.newaxis] * get_brush()[np.newaxis, :, :]
            if updater.inputs.Pressed("s") or updater.inputs.Down("x"):
                start_mass = 10
                start_motion = 10
                if updater.inputs.Pressed("a"):
                    start_motion *= 5
                # for mpos in updater.inputs.get_mouse_path():
                #     mx, my = np.round(np.array(mpos) / size * self.waves.size).astype(int)
                mx, my = np.round(mouse_position).astype(int)
                self.waves.grid[:, mx, my] += np.append(mouse_movement * start_motion, start_mass)
            if updater.inputs.Pressed("g"):
                # delete
                start_mass = 10
                mx, my = np.round(mouse_position - self.brush_size / 2).astype(int)
                self.waves.gridT[mx:mx + self.brush_size, my:my + self.brush_size] *= \
                    1 / (1 + start_mass * np.array([1, 1, 1])[np.newaxis, np.newaxis, :] * get_brush()[:, :, np.newaxis])

        except ValueError:
            pass
        self.waves.Update()
        surface = self.waves.Draw()

        # updater.canvas.Blit(surface)
        if updater.inputs.Pressed("w"):
            wi, he = surface.get_size()
            wu, hu = updater.canvas.surface.get_size()
            updater.canvas.surface.blits((surface, (i * wi, j * he)) for i, j in itertools.product(range(wu // wi), range(hu // he)))
            # pygame.transform.scale(surface, updater.canvas.surface.get_size(), updater.canvas.surface)
            pass
        else:
            pygame.transform.scale(surface, updater.canvas.surface.get_size(), updater.canvas.surface)
        text = self.render_text.RenderLines(
            [f"dt:{updater.deltaTime}",
             f"mouse points: {len(updater.inputs.get_mouse_path())}",
             f"color intensity: {self.waves.intensity}",
             f"stickiness: {self.waves.stickiness}",
             f"change ratio: {self.waves.change_ratio}",
             ])
        updater.canvas.Blit(text)
        spot = updater.inputs.get_mouse_position()[0] / updater.canvas.surface.get_width()
        if updater.inputs.Pressed("1"):
            self.waves.intensity = spot**2 * 25
        if updater.inputs.Pressed("2"):
            self.waves.stickiness = spot * 4
        if updater.inputs.Pressed("3"):
            self.waves.change_ratio = spot


size = (1600, 1200)

if __name__ == "__main__":
    screenIO.Updater(Scene_1(), screenIO.Canvas(pygame.display.set_mode()), framerate=60).Play()
