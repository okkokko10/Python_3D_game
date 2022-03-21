import math
from operator import add
import os
import sys
import time
from typing import Callable, TypeVar
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import raymarchingC2 as raymarchingC
import numpy as np
import screenIO
import pygame
import base3D
import renderText
import render3D


class Triangle_Shape:
    def __init__(self, A: np.ndarray, B: np.ndarray, C: np.ndarray, D: np.ndarray):
        self.A = A
        self.B = B
        self.C = C
        self.D = D

    # @classmethod
    # def from_points_and_direction(cls, A: np.ndarray, B: np.ndarray, direction: np.ndarray):
    #     cls(A, B)
    #     l = np.linalg.norm(A - B)
    #     direction /= np.linalg.norm(direction)
    #     A_B = (A + B) / 2
    #     C = A_B + direction * l
    @classmethod
    def default(cls):
        A = np.array((0, 0, 0))
        B = np.array((1, 0, 0))
        C = np.array((0.5, 0, math.sqrt(3) / 2))
        D = np.array((0.5, math.sqrt(2 / 3), math.sqrt(3) / 6))
        return cls(A, B, C, D)

    def points(self):
        return self.A, self.B, self.C, self.D


def Load_Image(name):
    return pygame.image.load(os.path.join('ignore_pictures', name))


def Save_Image(surface: pygame.Surface, name: str):
    pygame.image.save(surface, os.path.join('craymarching', 'ignore_pictures', name))


_V = TypeVar("_V")


# class Variable_Changer:
#     def __init__(self, variables: list[tuple[Callable[[], _V], Callable[[_V], None], Callable[[_V, int], _V], str]]) -> None:
#         """variables is a list of tuples containing three functions: get, set, change, text. \n
#         When mousewheel is rotated by m, set(change(get(),m)) is called. \n
#         text is a string that accepts get() as an argument for formatting"""

#         self.variables = variables
#         self.selected_index = 0
#         self.mode = 0

#     def update(self, inputs: screenIO.Inputs):
#         if self.mode == 0:
#             self.selected_index -= inputs.get_mousewheel()
#             self.selected_index %= len(self.variables)
#         elif self.mode == 1:
#             a = inputs.get_mousewheel()
#             if a:
#                 self.change(self.selected_index, a)
#         if inputs.Down("§"):
#             self.mode ^= 1

#     def get_text(self):
#         if self.mode == 1:
#             s1 = "<"
#             s2 = ">"
#         else:
#             s1 = "|"
#             s2 = "|"
#         a = [v[3].format(v[0]()) for v in self.variables]
#         a[self.selected_index] = s1 + a[self.selected_index] + s2
#         return a

#     def change(self, index: int, amount: int):
#         self.variables[index][1](self.variables[index][2](self.variables[index][0](), amount))


class MyScene(screenIO.Scene):
    def o_Init(self, updater: screenIO.Updater):
        self.player = base3D.Template_Player()
        self.player.speed = 0.001
        self.camera = render3D.Camera(updater.canvas.height, updater.canvas.width, updater.canvas.height, self.player.transform)

        self.zoom = 0.5
        self.render_text = renderText.RenderText(25)
        self.render_smaller = renderText.RenderText(10)
        self.max_iterations = 20
        self.resolution = 200
        self.colorcycle = math.pi * (1 << 0)
        self.triangle = Triangle_Shape.default()
        updater.inputs.LockMouse()

        # def g1(): return raymarchingC.get_rules().max_iterations
        # def s1(x): raymarchingC.get_rules().max_iterations = x
        # def c1(x, i): return x + i
        # t1 = "max iterations: {}"
        # def g2(): return raymarchingC.get_rules().max_iterations_light
        # def s2(x): raymarchingC.get_rules().max_iterations_light = x
        # def c2(x, i): return x + i
        # t2 = "max iterations light: {}"
        # def g3(): return raymarchingC.get_sdf_object().level
        # def s3(x): raymarchingC.get_sdf_object().level = x
        # def c3(x, i): return x + i
        # t3 = "triangle level: {}"
        # def g4(): return self.resolution
        # def s4(x): self.resolution = x
        # def c4(x, i): return x * (2**(i / 4))
        # t4 = "resolution: {}"

        # self.variable_changer = Variable_Changer([
        #     (g1, s1, c1, t1),
        #     (g2, s2, c2, t2),
        #     (g3, s3, c3, t3),
        #     (g4, s4, c4, t4),
        # ])

    def o_Update(self, updater: screenIO.Updater):
        self.player.Update(updater)
        inputs = updater.inputs
        if inputs.Pressed("1"):
            if inputs.Down("p"):
                self.max_iterations = 1000
            self.max_iterations += inputs.get_mousewheel()
            raymarchingC.get_rules().max_iterations = self.max_iterations
            raymarchingC.get_rules().max_iterations_light = self.max_iterations * 2
        if inputs.Pressed("2"):
            raymarchingC.get_sdf_object().level += inputs.get_mousewheel()
        if inputs.Pressed("3"):
            if inputs.Down("p"):
                self.resolution = 200
            self.resolution *= 2**(inputs.get_mousewheel() / 4)
        if inputs.Pressed("4"):
            raymarchingC.get_rules().close_enough *= 2**inputs.get_mousewheel()
        if inputs.Pressed("5"):
            raymarchingC.get_rules().close_enough_light *= 2**inputs.get_mousewheel()
        if inputs.Down("mouse right", "keypad 5"):
            self.player.speed /= 2
            self.resolution /= 2
        if inputs.Up("mouse right", "keypad 5"):
            self.player.speed *= 2
            self.resolution *= 2
        # if inputs.Pressed("mouse left"):
        #     if inputs.Pressed("4"):
        #         raymarchingC.get_sdf_object().set_mirrorer1_direction(*self.player.transform.GlobalizeDirection((0, 0, 1)))
        #     if inputs.Pressed("5"):
        #         raymarchingC.get_sdf_object().set_mirrorer2_direction(*self.player.transform.GlobalizeDirection((0, 0, 1)))
        if inputs.Pressed("r"):
            raymarchingC.get_sdf_object().set_mirrorer1_direction(*-(self.triangle.B - self.triangle.C))
            raymarchingC.get_sdf_object().set_mirrorer2_direction(*-(self.triangle.B - self.triangle.D))
        if inputs.Pressed("c"):
            raymarchingC.get_light().set_position(*self.player.transform.position)
        if inputs.Down("v"):
            raymarchingC.get_light().enabled ^= 1

        take_picture = inputs.Down("j")
        if take_picture:
            self.resolution *= 8

        # self.variable_changer.update(inputs)

        self.width = self.height = round(self.resolution)

        t0 = time.perf_counter()
        arr = (raymarchingC.Get_array(self.player.transform.rotation, self.player.transform.position,
               self.width, self.height, self.zoom * self.resolution))
        t1 = time.perf_counter()
        surface = pygame.surface.Surface(arr.shape[:2])
        colors = pygame.surfarray.pixels3d(surface)
        colors[:, :, :] = ((np.sin(arr[:, :, :3] * self.colorcycle) + 1) * 63
                           * (arr[:, :, 3][:, :, np.newaxis] != 0)
                           * ((arr[:, :, 4][:, :, np.newaxis] != 0) + 1)
                           ).astype(np.uint8)
        # colors[:, :, :] = (arr[:, :, :3] * np.broadcast_to(arr[:, :, 3], (*arr.shape[:2], 3)) * 256).astype(np.uint8)

        del colors
        if take_picture:
            Save_Image(pygame.transform.flip(surface, 0, 1), "triangle.bmp")
            self.resolution /= 8

        pygame.transform.scale(pygame.transform.flip(surface, 0, 1), updater.canvas.surface.get_size(), updater.canvas.surface)
        t2 = time.perf_counter()

        self.camera.DrawDots(updater.canvas, [raymarchingC.get_light().get_position()], 0.1, pygame.Color(255, 255, 0))
        # self.camera.DrawDots(updater.canvas, self.triangle.points(), 0.1, pygame.Color(255, 0, 255))
        # self.camera.Draw_Wireframe(updater.canvas, self.triangle.points(), 0.05, pygame.Color(255, 0, 255))

        text = self.render_text.RenderEffects(renderText.TextEffects().Prepare([
            "dt: {:.3}".format(t1 - t0),
            "iterations: %s" % self.max_iterations,
            "triangle level: %s" % raymarchingC.get_sdf_object().level,
            "resolution: %i" % self.resolution,
            "close enough: %s" % raymarchingC.get_rules().close_enough,
            "close enough light: %s" % raymarchingC.get_rules().close_enough_light,
            # "mirrorer 1: {:.3} {:.3} {:.3}".format(*raymarchingC.get_sdf_object().mirrorer1_direction,),
            # "mirrorer 2: {:.3} {:.3} {:.3}".format(*raymarchingC.get_sdf_object().mirrorer2_direction,)
        ]))
        # text = self.render_text.RenderEffects(renderText.TextEffects().Prepare(["dt: {:.3}".format(t1 - t0)] + self.variable_changer.get_text()))
        text_smaller = self.render_smaller.RenderEffects(renderText.TextEffects().Prepare([str(e) for e in updater.get_events()]))
        updater.canvas.Blit(text)
        updater.canvas.Blit(text_smaller, (0, text.get_height()))


screenIO.Updater(MyScene(), screenIO.Canvas(pygame.display.set_mode((800, 800))), framerate=60).Play()
