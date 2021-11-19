from orientation import *
from screenIO import *
from render3D import *
import pygame
import random

if __name__ == '__main__':

    C = Camera()
    C.transform.position = Vector(0, 0, 0)

    # den = 5
    # points = [Vector(i, j, k)/den for i in range(3*den) for j in range(3*den) for k in range(3*den)]
    # points += [Vector(i/den, 0, k/den) for i in range(-3*den, 6*den) for k in range(-3*den, 6*den)]

    points = [Vector(random.random()*2-1,  random.random()*2-1, random.random()*0.1+2) for _ in range(500)]

    mx, my = 0, 0

    def update(updater: 'Updater'):
        canvas = updater.get_canvas()
        inputs = updater.get_inputs()
        events = updater.get_events()
        deltaTime = updater.get_deltaTime()
        canvas.Fill((0, 0, 100))
        canvas.LockSurface()
        # C.DrawLines(canvas, points, 5, (100, 0, 100))
        C.DrawDots(canvas, points, 5, (100, 0, 000))
        canvas.UnlockSurface()
        # for e in events:
        #     print(e)
        global mx, my
        mdx, mdy = pygame.mouse.get_rel()
        mx += mdx
        my += mdy
        # C.transform.rotation *= Vector(1,0,0).RotationAround(-mdy/400)*(Vector(0,1,0).RotationAround(-mdx/400))
        rotationX = Vector(0, 1, 0).RotationAround(mx/200)
        rotationY = Vector(1, 0, 0).RotationAround(my/200)
        WASDvector = Vector(inputs.IsHeld(pygame.K_d)-inputs.IsHeld(pygame.K_a), 0,
                            inputs.IsHeld(pygame.K_w)-inputs.IsHeld(pygame.K_s))

        C.transform.rotation = rotationX * rotationY
        C.transform.position += rotationX.Rotate(WASDvector*deltaTime*0.001)

        if inputs.IsDown(pygame.K_t):
            inputs.LockMouse()
        if inputs.IsDown(pygame.K_y):
            inputs.UnlockMouse()

        return

    Upd = Updater().Setup(func=update, framerate=40)

    Upd.get_inputs().LockMouse()

    Upd.Play()
