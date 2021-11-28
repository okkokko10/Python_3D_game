from orientation import *
from screenIO import *
from render3D import *
import pygame
import random
import facecamera

if __name__ == '__main__':

    C = Camera()
    C.transform.position = Vector(0, 0, 0)

    # den = 5
    # points = [Vector(i, j, k)/den for i in range(3*den) for j in range(3*den) for k in range(3*den)]
    # points += [Vector(i/den, 0, k/den) for i in range(-3*den, 6*den) for k in range(-3*den, 6*den)]

    points = [Vector(random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 0.1 + 2) for _ in range(500)]
    picturePoints = Vector(0, 0, 0), Vector(1, 0, 0), Vector(1, 1, 0), Vector(0, 1, 0)

    mx, my = 0, 0

    def update(updater: 'Updater'):
        canvas = updater.get_canvas()
        inputs = updater.get_inputs()
        events = updater.get_events()
        deltaTime = updater.get_deltaTime()
        # C.DrawLines(canvas, points, 5, (100, 0, 100))
        # for e in events:
        #     print(e)
        global mx, my
        mdx, mdy = inputs.get_mouse_movement()
        mx += mdx
        my += mdy
        # C.transform.rotation *= Vector(1,0,0).RotationAround(-mdy/400)*(Vector(0,1,0).RotationAround(-mdx/400))
        rotationX = Vector(0, 1, 0).RotationAround(mx / 200)
        rotationY = Vector(1, 0, 0).RotationAround(my / 200)
        WASDvector = Vector(inputs.keyPressed(pygame.K_d) - inputs.keyPressed(pygame.K_a), 0,
                            inputs.keyPressed(pygame.K_w) - inputs.keyPressed(pygame.K_s))

        C.transform.rotation = rotationX * rotationY
        C.transform.position += rotationX.Rotate(WASDvector * deltaTime * 0.001)

        if inputs.keyDown(pygame.K_t):
            inputs.LockMouse()
        if inputs.keyDown(pygame.K_y):
            inputs.UnlockMouse()
        face = facecamera.GetPhotos()
        canvas.Fill((0, 0, 100))
        canvas.LockSurface()
        C.DrawDots(canvas, points, 5, (100, 0, 000))
        C.DrawTexturedPolygon(canvas, picturePoints, face.convert())
        canvas.UnlockSurface()
        return

    Upd = Updater().Setup(func=update, framerate=30, canvas=Canvas(pygame.display.set_mode()))

    Upd.get_inputs().LockMouse()
    C.width = Upd.canvas.ratio
    Upd.Play()
