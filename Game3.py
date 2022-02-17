# import sys
# sys.path.append("..")

from orientation import *
from screenIO import *
from render3D import *
import pygame
import renderText
import vector
if __name__ == '__main__':
    class MyScene(Scene):
        def o_Init(self, updater: 'Updater'):
            updater.get_inputs().LockMouse()

            self.camera = Camera()
            self.camera.transform.position = Vector3(0, 0, 0)
            self.camera.width = updater.canvas.ratio

            self.corner_distance = 1

            self.mx, self.my = 0, 0
            self.rtext = renderText.RenderText(25)

        def o_Update(self, updater: 'Updater'):
            canvas = updater.get_canvas()
            inputs = updater.get_inputs()
            deltaTime = updater.get_deltaTime()
            WASDvector = Vector3(inputs.keyPressed(pygame.K_d) - inputs.keyPressed(pygame.K_a), 0,
                                 inputs.keyPressed(pygame.K_w) - inputs.keyPressed(pygame.K_s))

            mdx, mdy = inputs.get_mouse_movement() / 4 + inputs.arrows_vector().complexConjugate() * deltaTime / 20
            self.mx += mdx
            self.my += mdy
            rotationX = Vector3(0, 1, 0).RotationAround(self.mx * math.pi / 180)
            rotationY = Vector3(1, 0, 0).RotationAround(self.my * math.pi / 180)

            self.camera.transform.rotation = rotationX * rotationY
            self.camera.transform.position += rotationX.Rotate(WASDvector * deltaTime * 0.001)
            self.camera.transform.position += Vector3(0, inputs.Pressed("space") - inputs.Pressed("left shift"), 0) * deltaTime / 1000

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
                self.mx = 45

            if inputs.keyDown(pygame.K_t):
                inputs.LockMouse()
            if inputs.keyDown(pygame.K_y):
                inputs.UnlockMouse()
            # face = facecamera.GetPhotos()
            canvas.Fill((0, 0, 100))
            # canvas.LockSurface()

            corners = (Vector3(self.corner_distance, 0, 0), Vector3(0, 0, self.corner_distance),
                       Vector3(self.corner_distance, 1, 0), Vector3(0, 1, self.corner_distance),
                       Vector3(0, 0, 0), Vector3(0, 1, 0))
            markers = Vector3(1, 0, 0), Vector3(0, 0, 1), Vector3(1, 1, 0), Vector3(0, 1, 1)  # , Vector3(1, 0, 1)

            self.camera.Draw_Wireframe(canvas, corners, 5, (255, 0, 0))
            corners_projected = self.camera.ProjectPoints(corners)
            centers_projected = corners_projected[4:]
            markers_projected = self.camera.ProjectPoints(markers)

            def Tag_pixel(pos, text, color):
                sf = self.rtext.RenderLines(text, color)
                canvas.Blit(sf, pos)

            def Tag(pos, text, color):
                Tag_pixel(canvas.convert(pos), text, color)

            def DistanceLine(a, b, width, color, tag_offset=0):
                a, b = vector.Vector(*a), vector.Vector(*b)
                canvas.Line(a, b, width, color)
                dis = a.distance(b)
                Tag((a + b) / 2, [""] * tag_offset + [str(dis)], color)
                return dis

            if len(corners_projected) == 6 and len(markers_projected) == 4:
                d_long_right = DistanceLine(corners_projected[0], centers_projected[0], 6, (0, 100, 255))
                d_short_right = DistanceLine(markers_projected[0], centers_projected[0], 6, (255, 100, 0))
                d_long_left = DistanceLine(corners_projected[1], centers_projected[0], 6, (100, 255, 0), 2)
                d_short_left = DistanceLine(markers_projected[1], centers_projected[0], 6, (0, 100, 100), 2)
                d_center = DistanceLine(centers_projected[1], centers_projected[0], 6, (255, 0, 255), 0)
                if d_short_left and d_short_right:
                    r_right = d_long_right / d_short_right
                    r_left = d_long_left / d_short_left
                    Tag_pixel((0, 0), [
                        str(r_right),
                        str(r_left),
                        str(r_right / d_short_right),
                        str(r_right / d_short_left)
                    ], (255, 255, 255))
            Tag_pixel((0, 100), [
                f"{self.mx} {self.my}"
            ], (0, 255, 255))

            self.camera.DrawDots(canvas, markers, 5, (0, 0, 0))

            # C.DrawTexturedPolygon(canvas, picturePoints, face.convert())
            canvas.Circle((0, 0), 2, (255, 255, 255))
            # canvas.UnlockSurface()

    Upd = Updater(MyScene(), framerate=30, canvas=CanvasZoom(pygame.display.set_mode()))

    Upd.Play()
