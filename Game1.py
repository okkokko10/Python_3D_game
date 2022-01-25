from orientation import *
from screenIO import *
from render3D import *
import pygame
import random
import facecamera


class A(Scene):

    def o_Init(self, updater: 'Updater'):
        self.C = Camera()
        self.C.transform.position = Vector3(0, 0, 0)

        # den = 5
        # points = [Vector(i, j, k)/den for i in range(3*den) for j in range(3*den) for k in range(3*den)]
        # points += [Vector(i/den, 0, k/den) for i in range(-3*den, 6*den) for k in range(-3*den, 6*den)]

        self.points = [Vector3(random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 0.1 + 2) for _ in range(500)]
        self.picturePoints = Vector3(0, 0, 0), Vector3(1, 0, 0), Vector3(1, 1, 0), Vector3(0, 1, 0)

        self.mouse = vec(0, 0)
        updater.get_inputs().LockMouse()
        self.C.width = updater.canvas.ratio

    def o_Update(self, updater: 'Updater'):
        canvas = updater.get_canvas()
        inputs = updater.get_inputs()
        events = updater.get_events()
        deltaTime = updater.get_deltaTime()
        # C.DrawLines(canvas, points, 5, (100, 0, 100))
        # for e in events:
        #     print(e)
        self.mouse += inputs.get_mouse_movement()
        mx, my = self.mouse
        # C.transform.rotation *= Vector(1,0,0).RotationAround(-mdy/400)*(Vector(0,1,0).RotationAround(-mdx/400))
        rotationX = Vector3(0, 1, 0).RotationAround(mx / 200)
        rotationY = Vector3(1, 0, 0).RotationAround(my / 200)
        wasdX, wasdY = updater.get_inputs().WASD()
        WASDvector = Vector3(wasdX, 0, wasdY)
        self.C.transform.rotation = rotationX * rotationY
        self.C.transform.position += rotationX.Rotate(WASDvector * deltaTime * 0.001)

        if inputs.keyDown(pygame.K_t):
            inputs.LockMouse()
        if inputs.keyDown(pygame.K_y):
            inputs.UnlockMouse()
        face = facecamera.GetPhotos()
        canvas.Fill((0, 0, 100))
        canvas.LockSurface()
        self.C.DrawDots(canvas, self.points, 5, (100, 0, 000))
        self.C.DrawTexturedPolygon(canvas, self.picturePoints, face.convert())
        canvas.UnlockSurface()
        return


if __name__ == '__main__':

    Upd = Updater(scene=A(), framerate=30, canvas=Canvas(pygame.display.set_mode()))

    Upd.Play()
