import os
import random
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import screenIO
import numpy as np
import pygame

size = (800, 600)


class Scene_1(screenIO.Scene):
    def o_Init(self, updater: 'screenIO.Updater'):
        self.size = (400, 300)
        self.board = np.zeros((*self.size, 3), float)
        "board[x,y,0] and board[x,y,1] is the velocity at x,y board[x,y,2] is the mass"
        updater.canvas.Fill((10, 20, 0))
        self.brush_size = 60

        def func(x, y):
            return (x - self.brush_size / 2)**2 + (y - self.brush_size / 2)**2 < self.brush_size**2 / 4
        self.brush = np.fromfunction(func, (self.brush_size, self.brush_size))
        self.movement_treshold = 0
        self.movement_treshold_max = 10

    def o_Update(self, updater: 'screenIO.Updater'):
        mouse_position = np.array(updater.inputs.get_mouse_position()) / size * self.size
        mouse_movement = np.array(updater.inputs.get_mouse_movement()) / size * self.size
        # print(mouse_position, mouse_movement)
        movement_chance = 0.1
        self.movement_treshold += 1
        self.movement_treshold %= self.movement_treshold_max

        def random_round(a: np.ndarray):
            return np.copysign(np.fabs(a) > self.movement_treshold, a)

            return np.copysign(np.fabs(a) * movement_chance > random.random(), a)

            return np.copysign(np.fabs(a) * movement_chance > np.random.rand(*a.shape), a)
            return np.round(a).astype(int)
            return a.astype(int) + (a % 1 > np.random.rand(*a.shape))
        if updater.inputs.Up("mouse left"):
            start_mass = 1
            mx, my = np.round(mouse_position - self.brush_size / 2).astype(int)
            self.board[mx:mx + self.brush_size, my:my + self.brush_size] += 1 * \
                np.append(mouse_movement, start_mass)[np.newaxis, np.newaxis, :] * self.brush[:, :, np.newaxis]
        if updater.inputs.Up("mouse right"):
            start_mass = 1
            self.board[:, :] += np.append(mouse_movement, start_mass)

        addboard: np.ndarray = np.zeros((*self.size, 3), float)
        ind = np.indices(self.size)  # .transpose(1, 2, 0)
        # addboard[(self.board[:, :].astype(int) + np.indices(self.size).transpose(1, 2, 0)) % self.size] = 1
        toind = ((ind[0] + random_round(self.board[ind[0], ind[1], 0] / self.board[ind[0], ind[1], 2])).astype(int) % self.size[0],
                 (ind[1] + random_round(self.board[ind[0], ind[1], 1] / self.board[ind[0], ind[1], 2])).astype(int) % self.size[1])
        bo = self.board[ind[0], ind[1]]
        # bo[:, :, 0] /= bo[:, :, 2]
        # bo[:, :, 1] /= bo[:, :, 2]

        # bo /= np.linalg.norm(bo, axis=0)
        np.nan_to_num(bo, copy=False)
        np.add.at(addboard, toind, bo)
        self.board[...] = addboard[...]

        def sigmoid(a: np.ndarray):
            return 1.0 / (1.0 + np.exp(-a))

        def color_map(a: np.ndarray):
            return 1.0 - 1.0 / (np.fabs(a) + 1.0)

        surface = pygame.surface.Surface(self.size)
        colors = pygame.surfarray.pixels3d(surface)
        # colors[:, :, 0] = color_map(self.board[:, :, 0] * 1000) * 200
        # colors[:, :, 2] = color_map(self.board[:, :, 1] * 1000) * 200
        # colors[:, :, 0] = (self.board[:, :, 0] != 0) * 255
        # colors[:, :, 2] = (self.board[:, :, 1] != 0) * 255
        colors[:, :, 1] = color_map(self.board[:, :, 2]) * 255

        del colors

        # updater.canvas.Blit(surface)
        pygame.transform.scale(surface, updater.canvas.surface.get_size(), updater.canvas.surface)


if __name__ == "__main__":
    screenIO.Updater(Scene_1(), screenIO.Canvas(pygame.display.set_mode(size)), framerate=60).Play()
