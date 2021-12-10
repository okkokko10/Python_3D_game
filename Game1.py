from orientation import *
from screenIO import *
from render3D import *
import pygame
import random
import facecamera


def init(updater: 'Updater'):
    o = updater.get_objects()
    o.C = Camera()
    o.C.transform.position = Vector3(0, 0, 0)

    # den = 5
    # points = [Vector(i, j, k)/den for i in range(3*den) for j in range(3*den) for k in range(3*den)]
    # points += [Vector(i/den, 0, k/den) for i in range(-3*den, 6*den) for k in range(-3*den, 6*den)]

    o.points = [Vector3(random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 0.1 + 2) for _ in range(500)]
    o.picturePoints = Vector3(0, 0, 0), Vector3(1, 0, 0), Vector3(1, 1, 0), Vector3(0, 1, 0)

    o.mx, o.my = 0, 0

    updater.get_inputs().LockMouse()
    o.C.width = updater.canvas.ratio
    pass


def update(updater: 'Updater'):
    canvas = updater.get_canvas()
    inputs = updater.get_inputs()
    events = updater.get_events()
    deltaTime = updater.get_deltaTime()
    o = updater.get_objects()
    # C.DrawLines(canvas, points, 5, (100, 0, 100))
    # for e in events:
    #     print(e)
    mdx, mdy = inputs.get_mouse_movement()
    o.mx += mdx
    o.my += mdy
    # C.transform.rotation *= Vector(1,0,0).RotationAround(-mdy/400)*(Vector(0,1,0).RotationAround(-mdx/400))
    rotationX = Vector3(0, 1, 0).RotationAround(o.mx / 200)
    rotationY = Vector3(1, 0, 0).RotationAround(o.my / 200)
    WASDvector = Vector3(inputs.keyPressed(pygame.K_d) - inputs.keyPressed(pygame.K_a), 0,
                         inputs.keyPressed(pygame.K_w) - inputs.keyPressed(pygame.K_s))

    o.C.transform.rotation = rotationX * rotationY
    o.C.transform.position += rotationX.Rotate(WASDvector * deltaTime * 0.001)

    if inputs.keyDown(pygame.K_t):
        inputs.LockMouse()
    if inputs.keyDown(pygame.K_y):
        inputs.UnlockMouse()
    face = facecamera.GetPhotos()
    canvas.Fill((0, 0, 100))
    canvas.LockSurface()
    o.C.DrawDots(canvas, o.points, 5, (100, 0, 000))
    o.C.DrawTexturedPolygon(canvas, o.picturePoints, face.convert())
    canvas.UnlockSurface()
    return


if __name__ == '__main__':

    Upd = Updater(func=update, init=init, framerate=30, canvas=Canvas(pygame.display.set_mode()))

    Upd.Play()
