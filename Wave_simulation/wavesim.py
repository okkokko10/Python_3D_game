import itertools
import os
import random
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import screenIO
import numpy as np
import pygame

size = (800, 600)

# ideas:
# other values a tile can have:
#   spread: how wide is the cone it can go?
#   change: how much of the tile is left behind and how much goes away. change_ratio, but local


def pythagoras(a, b):
    return a**2 + b**2


def complex_mul(ax, ay, bx, by):
    return ax * bx - ay * by, ax * by + ay * bx


class Scene_1(screenIO.Scene):
    def o_Init(self, updater: 'screenIO.Updater'):
        self.size = (400, 300)
        self.board = np.zeros((*self.size, 3), float)
        "board[x,y,0] and board[x,y,1] is the velocity at x,y board[x,y,2] is the mass"
        updater.canvas.Fill((10, 20, 0))
        self.brush_size = 60

        def func(x, y):
            a = (x - self.brush_size / 2)**2 + (y - self.brush_size / 2)**2
            return 10 / ((a) + 1) * (a < self.brush_size**2 / 4)
        self.brush = np.fromfunction(func, (self.brush_size, self.brush_size))
        self.change_ratio = 0.5
        "how much one update changes the board"

    def o_Update(self, updater: 'screenIO.Updater'):
        mouse_position = np.array(updater.inputs.get_mouse_position()) / size * self.size
        mouse_movement = np.array(updater.inputs.get_mouse_movement()) / size * self.size
        # print(mouse_position, mouse_movement)

        def get_brush():
            if updater.inputs.Pressed("q"):
                return self.brush != 0
            else:
                return self.brush

        def random_round_2d(a: np.ndarray, b: np.ndarray):
            ra, rb = random.random(), random.random()
            ra, rb = np.random.rand(*a.shape), np.random.rand(*a.shape)
            # ra = rb
            sx, sy = complex_mul(ra, rb, 0.5, -0.5)
            sy *= np.fabs(sy)
            # sx **= 2
            # sx *= 3  # the mean should be 1
            w = 0.9
            sx = sx * w + (1 - w)
            sy = sy * w
            oa, ob = complex_mul(a, b, sx, sy)
            return np.round(oa).astype(int), np.round(ob).astype(int)

        def random_round(a: np.ndarray):
            return np.round(np.random.rand(*a.shape) * a).astype(int)
            # return np.copysign(np.fabs(a) > self.movement_treshold, a)

            # return np.copysign(np.fabs(a) * movement_chance > random.random(), a)

            return np.copysign(np.fabs(a) * movement_chance > np.random.rand(*a.shape), a)
            return np.round(a).astype(int)
            return a.astype(int) + (a % 1 > np.random.rand(*a.shape))
        try:
            if updater.inputs.Down("t"):
                self.board[...] = 0
            if updater.inputs.Down("y"):
                self.board[..., 0:2] = 0
            if updater.inputs.Up("r"):
                start_mass = 1
                self.board[:, :] += np.append(mouse_movement, start_mass)
            if updater.inputs.Up("mouse left") or updater.inputs.Pressed("d"):
                start_mass = 1
                start_motion = 1
                if updater.inputs.Pressed("a"):
                    start_motion *= 5
                mx, my = np.round(mouse_position - self.brush_size / 2).astype(int)
                self.board[mx:mx + self.brush_size, my:my + self.brush_size] += 1 * \
                    np.append(mouse_movement * start_motion, start_mass)[np.newaxis, np.newaxis, :] * get_brush()[:, :, np.newaxis]
            if updater.inputs.Pressed("f"):
                start_mass = 1
                start_motion = 0
                mx, my = np.round(mouse_position - self.brush_size / 2).astype(int)
                self.board[mx:mx + self.brush_size, my:my + self.brush_size] += 1 * \
                    np.append(mouse_movement * start_motion, start_mass)[np.newaxis, np.newaxis, :] * get_brush()[:, :, np.newaxis]
            if updater.inputs.Pressed("s"):
                start_mass = 10
                start_motion = 10
                if updater.inputs.Pressed("a"):
                    start_motion *= 5
                mx, my = np.round(mouse_position).astype(int)
                self.board[mx, my] += np.append(mouse_movement * start_motion, start_mass)

        except ValueError:
            pass

        addboard: np.ndarray = np.zeros((*self.size, 3), float)
        ind = np.indices(self.size)  # .transpose(1, 2, 0)
        # addboard[(self.board[:, :].astype(int) + np.indices(self.size).transpose(1, 2, 0)) % self.size] = 1
        # toind = ((ind[0] + random_round(self.board[ind[0], ind[1], 0] / self.board[ind[0], ind[1], 2])).astype(int) % self.size[0],
        #          (ind[1] + random_round(self.board[ind[0], ind[1], 1] / self.board[ind[0], ind[1], 2])).astype(int) % self.size[1])
        # bo = self.board[ind[0], ind[1]]
        # uu = 10
        # a1, b1 = random_round_2d(self.board[:, :, 0] * uu / (self.board[:, :, 2] + uu), self.board[:, :, 1] * uu / (self.board[:, :, 2] + uu))
        a1, b1 = random_round_2d(self.board[:, :, 0] / self.board[:, :, 2], self.board[:, :, 1] / self.board[:, :, 2])
        # toind = ((ind[0, :, :] + a1).astype(int) % self.size[0],
        #          (ind[1, :, :] + b1).astype(int) % self.size[1])
        toind = ((ind[:, :, :] + np.stack((a1, b1), 0)).astype(int) % np.array(self.size)[:, np.newaxis, np.newaxis])
        bo = self.board[:, :]

        # bo /= np.linalg.norm(bo, axis=0)
        np.nan_to_num(bo, copy=False)
        np.add.at(addboard, (*toind,), bo)
        # addboard[:, 0, 1] = -np.fabs(addboard[:, 0, 1])
        # addboard[:, 0, 1] *= -1
        decay_ratio = 1
        self.board *= 1 - self.change_ratio
        self.board[...] += addboard[...] * self.change_ratio
        self.board[...] *= decay_ratio
        # self.board[..., 2] *= decay_ratio
        # self.board[100:150, 100:150, 0] += -0.1 * self.board[100:150, 100:150, 2]
        # a2, b2 = complex_mul(ind[0], ind[1], 1, 0) * self.board[:, :, 2]
        # pyt2 = pythagoras(a2, b2) * 100
        # self.board[:, :, 0] += a2 / pyt2
        # self.board[:, :, 1] += b2 / pyt2

        def sigmoid(a: np.ndarray):
            return 1.0 / (1.0 + np.exp(-a))

        def color_map(a: np.ndarray):
            return 1.0 - 1.0 / (np.fabs(a) + 1.0)

        surface = pygame.surface.Surface(self.size)
        colors = pygame.surfarray.pixels3d(surface)
        # colors[:, :, 0] = color_map(self.board[:, :, 0] * 1000) * 200
        # colors[:, :, 2] = color_map(self.board[:, :, 1] * 1000) * 200
        lengths = np.sqrt(self.board[:, :, 0]**2 + self.board[:, :, 1]**2)
        colors[:, :, 0] = color_map(lengths * self.board[:, :, 2] * 0.1) * 200
        colors[:, :, 1] = color_map(self.board[:, :, 2]) * 255
        colors[:, :, 2] = color_map(lengths * 0.1) * 255

        del colors

        # updater.canvas.Blit(surface)
        if updater.inputs.Pressed("w"):
            updater.canvas.surface.blits((surface, (i, j)) for i, j in itertools.product((0, surface.get_width()), (0, surface.get_height())))
            # pygame.transform.scale(surface, updater.canvas.surface.get_size(), updater.canvas.surface)
            pass
        else:
            pygame.transform.scale(surface, updater.canvas.surface.get_size(), updater.canvas.surface)
        # print(updater.deltaTime)


if __name__ == "__main__":
    screenIO.Updater(Scene_1(), screenIO.Canvas(pygame.display.set_mode(size)), framerate=60).Play()
