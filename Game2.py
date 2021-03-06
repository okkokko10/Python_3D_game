# import sys
# sys.path.append("..")

from orientation import *
from screenIO import *
from render3D import *
import pygame
import random
import facecamera


if __name__ == '__main__':
    class MyScene(Scene):
        def o_Init(self, updater: 'Updater'):
            updater.get_inputs().LockMouse()

            self.camera = Camera()
            self.camera.transform.position = Vector3(0, 0, 0)
            self.camera.width = updater.canvas.ratio

            self.points = [Vector3(random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 0.1) for _ in range(500)]
            self.picturePoints = Vector3(0, 0, 0), Vector3(1, 0, 0), Vector3(1, 1, 0), Vector3(0, 1, 0)
            self.points += self.picturePoints
            self.corner_distance = 1

            self.ob1Transform = Transform(Vector3(), Quaternion(1))

            self.mx, self.my = 0, 0
            self.ox, self.oy = 0, 0
            self.mode = True

        def o_Update(self, updater: 'Updater'):
            canvas = updater.get_canvas()
            inputs = updater.get_inputs()
            events = updater.get_events()
            deltaTime = updater.get_deltaTime()
            WASDvector = Vector3(inputs.keyPressed(pygame.K_d) - inputs.keyPressed(pygame.K_a), 0,
                                 inputs.keyPressed(pygame.K_w) - inputs.keyPressed(pygame.K_s))
            if inputs.keyDown(pygame.K_g):
                self.mode = not self.mode

            mdx, mdy = inputs.get_mouse_movement()
            if self.mode:
                self.mx += mdx
                self.my += mdy
                rotationX = Vector3(0, 1, 0).RotationAround(self.mx / 200)
                rotationY = Vector3(1, 0, 0).RotationAround(self.my / 200)

                self.camera.transform.rotation = rotationX * rotationY
                self.camera.transform.position += rotationX.Rotate(WASDvector * deltaTime * 0.001)
                self.camera.transform.position += Vector3(0, inputs.Pressed("space") - inputs.Pressed("left shift"), 0) * deltaTime / 1000
            else:
                self.ox += mdx
                self.oy += mdy
                rotationX = Vector3(0, 1, 0).RotationAround(self.ox / 200)
                rotationY = Vector3(1, 0, 0).RotationAround(self.oy / 200)

                self.ob1Transform.rotation = rotationX * rotationY
                self.ob1Transform.position += rotationX.Rotate(WASDvector * deltaTime * 0.001)
            pointsTr = [self.ob1Transform.GlobalizePosition(p) for p in self.points]
            if inputs.Pressed("f"):
                self.corner_distance *= 2
            if inputs.Pressed("q"):
                updater.canvas.zoom *= 1.1
            if inputs.Pressed("e"):
                updater.canvas.zoom /= 1.1
            # if inputs.Down("r"):
            #     updater.canvas.zoom = 1
            if inputs.Down('r'):
                self.my = 0

            if inputs.keyDown(pygame.K_t):
                inputs.LockMouse()
            if inputs.keyDown(pygame.K_y):
                inputs.UnlockMouse()
            # face = facecamera.GetPhotos()
            canvas.Fill((0, 0, 100))
            canvas.LockSurface()
            self.camera.DrawDots(canvas, pointsTr, 5, (100, 0, 000))
            self.camera.DrawLines(canvas, pointsTr[-4:], 5, (0, 100, 0))

            corners = (Vector3(self.corner_distance, 0, 0), Vector3(0, 0, self.corner_distance),
                       Vector3(self.corner_distance, 1, 0), Vector3(0, 1, self.corner_distance),
                       Vector3(0, 0, 0), Vector3(0, 1, 0),)
            markers = Vector3(1, 1, 0), Vector3(0, 1, 1), Vector3(0, 0, 1), Vector3(1, 0, 0)  # , Vector3(1, 0, 1)

            self.camera.Draw_Wireframe(canvas, corners, 5, (255, 0, 0))
            self.camera.DrawDots(canvas, markers, 5, (0, 0, 0))
            corners_projected = self.camera.ProjectPoints(corners)
            markers_projected = self.camera.ProjectPoints(markers)

            # C.DrawTexturedPolygon(canvas, picturePoints, face.convert())
            canvas.Circle((0, 0), 2, (255, 255, 255))
            canvas.UnlockSurface()

    Upd = Updater(MyScene(), framerate=30, canvas=CanvasZoom(pygame.display.set_mode()))

    Upd.Play()
