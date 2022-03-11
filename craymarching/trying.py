import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import raymarchingC2 as raymarchingC
import numpy as np
import screenIO
import pygame
import base3D
import renderText
import render3D


class MyScene(screenIO.Scene):
    def o_Init(self, updater: screenIO.Updater):
        self.player = base3D.Template_Player()
        self.camera = render3D.Camera(updater.canvas.height, updater.canvas.width, updater.canvas.height, self.player.transform)

        self.zoom = 0.5
        self.render_text = renderText.RenderText(25)
        self.max_iterations = 5
        self.resolution = 400
        self.close_enough = 0.01
        self.colorcycle = 127
        updater.inputs.LockMouse()

    def o_Update(self, updater: screenIO.Updater):
        self.player.Update(updater)
        inputs = updater.inputs
        if inputs.Pressed("1"):
            self.max_iterations += inputs.get_mousewheel()
        if inputs.Pressed("2"):
            raymarchingC.get_sdf_object().level += inputs.get_mousewheel()
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
                raymarchingC.get_sdf_object().set_mirrorer1_direction(*self.player.transform.GlobalizeDirection((0, 0, 1)))
            if inputs.Pressed("5"):
                raymarchingC.get_sdf_object().set_mirrorer2_direction(*self.player.transform.GlobalizeDirection((0, 0, 1)))
            if inputs.Pressed("e"):
                a, b, c = self.player.transform.GlobalizeDirection((0, 0, 1))
                raymarchingC.get_sdf_object().set_mirrorer1_direction(a, b, c)
                raymarchingC.get_sdf_object().set_mirrorer2_direction(a, c, b)
        if inputs.Pressed("r"):
            a, b, c = -0.5, 0.866, 0
            raymarchingC.get_sdf_object().set_mirrorer1_direction(a, b, c)
            raymarchingC.get_sdf_object().set_mirrorer2_direction(-0.5, 0.255, 0.8)
        if inputs.Pressed("c"):
            raymarchingC.get_light().set_position(*self.player.transform.position)
        if inputs.Down("v"):
            raymarchingC.get_light().enabled ^= 1
        self.width = self.height = int(self.resolution)
        raymarchingC.get_rules().max_iterations = self.max_iterations
        raymarchingC.get_rules().max_iterations_light = self.max_iterations * 2

        t0 = time.perf_counter()
        arr = (raymarchingC.Get_array(self.player.transform.rotation, self.player.transform.position,
               self.width, self.height, self.zoom * self.resolution))
        t1 = time.perf_counter()
        surface = pygame.surface.Surface(arr.shape[:2])
        colors = pygame.surfarray.pixels3d(surface)
        colors[:, :, :] = ((np.sin(arr[:, :, :3]) + 1) * 63
                           * (arr[:, :, 3][:, :, np.newaxis] != 0)
                           * ((arr[:, :, 4][:, :, np.newaxis] == 0) + 1)
                           ).astype(np.uint8)
        # colors[:, :, :] = (arr[:, :, :3] * np.broadcast_to(arr[:, :, 3], (*arr.shape[:2], 3)) * 256).astype(np.uint8)

        del colors

        pygame.transform.scale(pygame.transform.flip(surface, 0, 1), updater.canvas.surface.get_size(), updater.canvas.surface)
        t2 = time.perf_counter()

        self.camera.DrawDots(updater.canvas, [raymarchingC.get_light().get_position()], 0.1, pygame.Color(255, 255, 0))

        text = self.render_text.RenderEffects(renderText.TextEffects().Prepare([
            "dt: {:.3}".format(t1 - t0),
            "iterations: %s" % self.max_iterations,
            "triangle level: %s" % raymarchingC.get_sdf_object().level,
            "resolution: %i" % self.resolution,
            "mirrorer 1: {:.3} {:.3} {:.3}".format(*raymarchingC.get_sdf_object().mirrorer1_direction,),
            "mirrorer 2: {:.3} {:.3} {:.3}".format(*raymarchingC.get_sdf_object().mirrorer2_direction,)
        ]))
        updater.canvas.Blit(text)


screenIO.Updater(MyScene(), screenIO.Canvas(pygame.display.set_mode((800, 800))), framerate=60).Play()
