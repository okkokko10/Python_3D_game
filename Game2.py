# import sys
# sys.path.append("..")

from orientation import *
from screenIO import *
from render3D import *
import pygame
import random
import facecamera


if __name__ == '__main__':

    C = Camera()
    C.transform.position = Vector3(0, 0, 0)

    points = [Vector3(random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 0.1) for _ in range(500)]
    picturePoints = Vector3(0, 0, 0), Vector3(1, 0, 0), Vector3(1, 1, 0), Vector3(0, 1, 0)
    points += picturePoints

    ob1Transform = Transform(Vector3(), Quaternion(1))

    mx, my = 0, 0
    ox, oy = 0, 0
    mode = False

    def update(updater: 'Updater'):
        canvas = updater.get_canvas()
        inputs = updater.get_inputs()
        events = updater.get_events()
        deltaTime = updater.get_deltaTime()
        WASDvector = Vector3(inputs.keyPressed(pygame.K_d) - inputs.keyPressed(pygame.K_a), 0,
                             inputs.keyPressed(pygame.K_w) - inputs.keyPressed(pygame.K_s))
        global mode
        if inputs.keyDown(pygame.K_g):
            mode = not mode

        mdx, mdy = inputs.get_mouse_movement()
        if mode:
            global mx, my
            mx += mdx
            my += mdy
            rotationX = Vector3(0, 1, 0).RotationAround(mx / 200)
            rotationY = Vector3(1, 0, 0).RotationAround(my / 200)

            C.transform.rotation = rotationX * rotationY
            C.transform.position += rotationX.Rotate(WASDvector * deltaTime * 0.001)
        else:
            global ox, oy
            ox += mdx
            oy += mdy
            rotationX = Vector3(0, 1, 0).RotationAround(ox / 200)
            rotationY = Vector3(1, 0, 0).RotationAround(oy / 200)

            ob1Transform.rotation = rotationX * rotationY
            ob1Transform.position += rotationX.Rotate(WASDvector * deltaTime * 0.001)
        pointsTr = [ob1Transform.GlobalizePosition(p) for p in points]

        if inputs.keyDown(pygame.K_t):
            inputs.LockMouse()
        if inputs.keyDown(pygame.K_y):
            inputs.UnlockMouse()
        # face = facecamera.GetPhotos()
        canvas.Fill((0, 0, 100))
        canvas.LockSurface()
        C.DrawDots(canvas, pointsTr, 5, (100, 0, 000))
        C.DrawLines(canvas, pointsTr[-4:], 5, (0, 100, 0))
        # C.DrawTexturedPolygon(canvas, picturePoints, face.convert())
        canvas.UnlockSurface()
        return

    Upd = Updater(func=update, framerate=30, canvas=Canvas(pygame.display.set_mode()))

    Upd.get_inputs().LockMouse()
    C.width = Upd.canvas.ratio
    Upd.Play()
