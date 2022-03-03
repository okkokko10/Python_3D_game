import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import raymarchingC
import numpy as np
import screenIO
import pygame
import base3D


class MyScene(screenIO.Scene):
    def o_Init(self, updater: screenIO.Updater):
        self.player = base3D.Template_Player()

    def o_Update(self, updater: screenIO.Updater):
        self.player.Update(updater)

        arr = (raymarchingC.Get_array(self.player.transform.rotation, *self.player.transform.position))
        surface = pygame.surface.Surface(arr.shape)
        red = pygame.surfarray.pixels_red(surface)
        red[:, :] = arr * 100
        del red

        pygame.transform.scale(pygame.transform.flip(surface, 0, 1), updater.canvas.surface.get_size(), updater.canvas.surface)


screenIO.Updater(MyScene()).Play()
