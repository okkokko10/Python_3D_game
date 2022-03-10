import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import raymarchingC
import numpy as np
import screenIO
import pygame
import base3D
import renderText


class MyScene(screenIO.Scene):
    def o_Init(self, updater: screenIO.Updater):
        self.player = base3D.Template_Player()
        self.zoom = 0.5
        self.render_text = renderText.RenderText(25)
        self.max_iterations = 5
        self.resolution = 400
        self.close_enough = 0.001
        self.colorcycle = 100
        updater.inputs.LockMouse()

    def o_Update(self, updater: screenIO.Updater):
        self.player.Update(updater)
        inputs = updater.inputs
        if inputs.Pressed("1"):
            self.max_iterations += inputs.get_mousewheel()
        if inputs.Pressed("2"):
            raymarchingC.get_scene().level += inputs.get_mousewheel()
        if inputs.Pressed("3"):
            self.resolution *= 1.1**inputs.get_mousewheel()
        if inputs.Down("mouse right"):
            self.player.speed /= 2
            self.resolution /= 2
        if inputs.Up("mouse right"):
            self.player.speed *= 2
            self.resolution *= 2
        if inputs.Pressed("mouse left"):
            if inputs.Pressed("4"):
                raymarchingC.get_scene().set_mirrorer1_direction(*self.player.transform.GlobalizeDirection((0, 0, 1)))
            if inputs.Pressed("5"):
                raymarchingC.get_scene().set_mirrorer2_direction(*self.player.transform.GlobalizeDirection((0, 0, 1)))
            if inputs.Pressed("e"):
                a, b, c = self.player.transform.GlobalizeDirection((0, 0, 1))
                raymarchingC.get_scene().set_mirrorer1_direction(a, b, c)
                raymarchingC.get_scene().set_mirrorer2_direction(a, c, b)
        if inputs.Pressed("r"):
            a, b, c = -0.5, 0.8, 0.1
            raymarchingC.get_scene().set_mirrorer1_direction(a, b, c)
            raymarchingC.get_scene().set_mirrorer2_direction(a, c, b)
        self.width = self.height = int(self.resolution)

        arr = (raymarchingC.Get_array(self.player.transform.rotation, self.player.transform.position,
               self.width, self.height, self.zoom * self.resolution, self.max_iterations, self.close_enough))
        surface = pygame.surface.Surface(arr.shape[:2])
        colors = pygame.surfarray.pixels3d(surface)
        colors[:, :, :] = (arr[:, :, :3] * arr[:, :, 3][:, :, np.newaxis] * (self.colorcycle)).astype(np.uint8)
        # colors[:, :, :] = (arr[:, :, :3] * np.broadcast_to(arr[:, :, 3], (*arr.shape[:2], 3)) * 256).astype(np.uint8)

        del colors

        pygame.transform.scale(pygame.transform.flip(surface, 0, 1), updater.canvas.surface.get_size(), updater.canvas.surface)

        text = self.render_text.RenderEffects(renderText.TextEffects().Prepare([
            "dt: %s" % updater.deltaTime,
            "iterations: %s" % self.max_iterations,
            "triangle level: %s" % raymarchingC.get_scene().level,
            "resolution: %i" % self.resolution,
            "mirrorer 1: %s" % raymarchingC.get_scene().mirrorer1_direction,
            "mirrorer 2: %s" % raymarchingC.get_scene().mirrorer2_direction
        ]))
        updater.canvas.Blit(text)


screenIO.Updater(MyScene(), screenIO.Canvas(pygame.display.set_mode((800, 800))), framerate=60).Play()
