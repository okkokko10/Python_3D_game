# import sys
# sys.path.append("..")

# from orientation import *
from screenIO import *
from render3D import *
import pygame
import renderText
import vector
import orientation2 as oi
# import random


class TriDimObject:
    def __init__(self, transform: oi.Transform = None, vertices: list[oi.Vector3] = None) -> None:
        self.transform = transform or oi.Transform(oi.Vector3(0, 0, 0), oi.IDENTITY)
        self.vertices = vertices or []

    def global_vertices(self):
        return [self.transform.GlobalizePosition(v) for v in self.vertices]


class RotationController:
    def __init__(self):
        self.x = 0.
        self.y = 0.
        self.z = 0.

    def rotX(self):
        # rotationX = oi.rotation_around((0, 1, 0), (self.x * math.pi / 180))
        # return rotationX
        return oi.elemental_rotation_y(self.x * math.pi / 180)

    def rotY(self):
        # rotationY = oi.rotation_around((1, 0, 0), (self.y * math.pi / 180))
        # return rotationY
        return oi.elemental_rotation_x(-self.y * math.pi / 180)

    def rot(self):
        return oi.chain_rotation(self.rotX(), self.rotY())

    def take_mouse(self, inputs: screenIO.Inputs, speed):
        mdx, mdy = inputs.get_mouse_movement().complexConjugate() * speed + inputs.arrows_vector() * 0.1
        self.x += mdx
        self.y += mdy


def cubegrid(x, y, z):
    return [oi.Vector3(a, b, c) for a in range(x) for b in range(y) for c in range(z)]


if __name__ == '__main__':
    class MyScene(Scene):
        def o_Init(self, updater: 'Updater'):
            updater.get_inputs().LockMouse()

            self.camera = Camera(updater.canvas.height, updater.canvas.width, updater.canvas.height)
            self.camera.transform.position = oi.Vector3(-1, 0, -1)
            self.camera_rotation = RotationController()
            a = [
                *cubegrid(3, 2, 3),
                oi.Vector3(1, 2, 1),
                oi.Vector3(1, 2, 2),
                oi.Vector3(2, 2, 2)
            ]
            self.test_object = TriDimObject(None, a)

        def o_Update(self, updater: 'Updater'):
            canvas = updater.get_canvas()
            canvas.Fill((0, 0, 100))
            inputs = updater.get_inputs()
            deltaTime = updater.get_deltaTime()
            WASDvector = oi.xy_to_x0y(inputs.WASD())

            if inputs.Pressed("mouse left", "x"):
                deltaTime /= 5
            if inputs.Pressed("mouse right", "c"):
                deltaTime *= 5

            self.camera_rotation.take_mouse(inputs, 0.25)

            self.camera.transform.rotation = self.camera_rotation.rot()
            self.camera.transform.position += oi.rotate(self.camera.transform.rotation, WASDvector) * deltaTime * 0.001
            self.camera.transform.position += oi.Vector3(0, inputs.Pressed("space") - inputs.Pressed("left shift"), 0) * deltaTime / 1000

            if inputs.Pressed("q"):
                self.camera.zoom *= 1.1
            if inputs.Pressed("e"):
                self.camera.zoom /= 1.1
            if inputs.keyDown(pygame.K_t):
                inputs.LockMouse()
            if inputs.keyDown(pygame.K_y):
                inputs.UnlockMouse()

            self.camera.DrawDots(canvas, self.test_object.global_vertices(), 0.1, pygame.Color(255, 255, 0))
            self.camera.Draw_Wireframe(canvas, self.test_object.global_vertices(), 0.05, pygame.Color(255, 255, 0))
            canvas.Circle(canvas.center, 2, (255, 255, 255))  # reticle

    Upd = Updater(MyScene(), framerate=60, canvas=Canvas(pygame.display.set_mode()))

    Upd.Play()
