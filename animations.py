import math
import pygame
import screenIO
from vector import Vector

# TODO: effects like flicker, glow, fade in/out


class Animation:
    def Draw(self, canvas: screenIO.Canvas, position: Vector, direction: Vector, age: int):
        "age represents how long the animation has gone for in milliseconds."


class Stab(Animation):
    def __init__(self, color_line, color_wave, color_shash):
        self.color_line = color_line
        self.color_wave = color_wave
        self.color_shash = color_shash

    def Draw(self, canvas: screenIO.Canvas, position: Vector, direction: Vector, age: int):
        if age < 250:
            l = age / 200
            l = math.sqrt(l)
            w = 1
            canvas.Line(position, position + direction * l, w, self.color_line)
        if 100 < age < 300:
            # l = 1
            l = age / 200
            # l = math.sqrt(l)
            w = 1
            o = (age - 100) / 600
            for i in 1, -1:
                offset1 = direction.normal() * o * i
                offset2 = direction.normal() * (o) * i * 0
                canvas.Line(position + offset1, position + l * direction + offset2, w, self.color_wave)


class main_scene(screenIO.Scene):
    def o_Init(self, updater: screenIO.Updater):
        self.age = 0
        self.stab = Stab((250, 250, 250), (50, 200, 50), (0, 250, 0))
        self.pos_to = Vector(100, 100)
        self.pos_from = Vector(0, 0)
        pass

    def o_Update(self, updater: screenIO.Updater):
        self.age += updater.deltaTime / 5
        if updater.inputs.mouseDown(1):
            self.pos_from = updater.inputs.get_mouse_position()
            self.age = 0
        if updater.inputs.mouseDown(3):
            self.pos_to = updater.inputs.get_mouse_position()
            self.age = 0
        if updater.inputs.mouseDown(2):
            self.age = 0
        updater.canvas.Fill((0, 0, 0))
        self.stab.Draw(updater.canvas, self.pos_from, self.pos_to - self.pos_from, self.age)

        pass


if __name__ == '__main__':
    screenIO.Updater(main_scene()).Play()
