# import sys
# sys.path.append("..")

# from orientation import *
from screenIO import *
from render3D import *
import pygame
import renderText
import vector
import orientation2 as oi
import random
if __name__ == '__main__':
    class MyScene(Scene):
        def o_Init(self, updater: 'Updater'):
            updater.get_inputs().LockMouse()

            self.camera = Camera()
            self.camera.transform.position = oi.Vector3(-1, 0, -1)
            self.camera.width = updater.canvas.ratio

            self.corner_distance = 1

            self.mx, self.my = 0, 0
            self.rtext = renderText.RenderText(25)
            self.rtext_small = renderText.RenderText(15)
            self.settings = {"lines to center": False, "lengths": True}
            self.ob1Transform = oi.Transform(oi.Vector3(0, 2, 0), oi.IDENTITY)
            self.points = [oi.Vector3(random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 0.1) for _ in range(500)]

        def o_Update(self, updater: 'Updater'):
            canvas = updater.get_canvas()
            canvas.Fill((0, 0, 100))
            inputs = updater.get_inputs()
            deltaTime = updater.get_deltaTime()
            WASDvector = oi.Vector3(inputs.keyPressed(pygame.K_d) - inputs.keyPressed(pygame.K_a), 0,
                                    inputs.keyPressed(pygame.K_w) - inputs.keyPressed(pygame.K_s))

            def Tag_pixel(pos, text, color):
                # sf = self.rtext.RenderLines(text, color)
                eff = renderText.TextEffects(default=renderText.Effect(color, (0, 0, 0)))
                sf = self.rtext_small.RenderEffects(eff.Prepare(text))
                canvas.Blit(sf, pos)

            def Tag(pos, text, color):
                Tag_pixel(canvas.convert(pos), text, color)

            def arraytext(a):
                return (' '.join(str(round(x, 4)).ljust(7) for x in y) for y in a)
            if inputs.Pressed("mouse left", "x"):
                deltaTime /= 5
            if inputs.Pressed("mouse right", "c"):
                deltaTime *= 5

            mdx, mdy = inputs.get_mouse_movement().complexConjugate() / 4 + inputs.arrows_vector() * deltaTime / 20
            self.mx += mdx
            self.my += mdy
            rotationX = oi.rotation_around((0, 1, 0), (self.mx * math.pi / 180))
            rotationY = oi.rotation_around((1, 0, 0), (self.my * math.pi / 180))
            drX = oi.rotation_around((0, 1, 0), (mdx * math.pi / 180))
            drY = oi.rotation_around((1, 0, 0), (mdy * math.pi / 180))
            self.ob1Transform.rotation = oi.chain_rotation(rotationX, rotationY)

            self.camera.transform.rotation = oi.chain_rotation(rotationX, rotationY)
            # self.camera.transform.rotation = self.camera.transform.rotation @ drX @ drY
            # self.camera.transform.position += oi.rotate(rotationX, WASDvector * deltaTime * 0.001)
            self.camera.transform.position += oi.rotate(self.camera.transform.rotation, WASDvector * deltaTime * 0.001)
            self.camera.transform.position += oi.Vector3(0, inputs.Pressed("space") - inputs.Pressed("left shift"), 0) * deltaTime / 1000

            pointsTr = [self.ob1Transform.GlobalizePosition(p) for p in self.points]
            pointsUn = [self.ob1Transform.LocalizePosition(p) for p in pointsTr]
            self.camera.DrawDots(canvas, pointsTr, 5, (100, 0, 0))
            self.camera.DrawDots(canvas, pointsUn, 5, (0, 0, 0))
            self.camera.DrawDots(canvas, self.points, 5, (0, 100, 0))
            a = (self.ob1Transform.rotation.transpose() @ self.ob1Transform.rotation)
            Tag_pixel((10, 100), (*arraytext(a), ""), (0, 255, 0))

            if inputs.Pressed("f"):
                self.corner_distance *= 2
            if inputs.Pressed("q"):
                updater.canvas.zoom *= 1.1
            if inputs.Pressed("e"):
                updater.canvas.zoom /= 1.1
            # if inputs.Down("r"):
            #     updater.canvas.zoom = 1
            if inputs.Down('r'):
                self.my = 0.
                self.mx = 45.
            if inputs.Down("1"):
                self.settings["lines to center"] ^= True
            if inputs.Down("2"):
                self.settings["lengths"] ^= True

            if inputs.keyDown(pygame.K_t):
                inputs.LockMouse()
            if inputs.keyDown(pygame.K_y):
                inputs.UnlockMouse()
            # face = facecamera.GetPhotos()
            # canvas.LockSurface()

            corners = ((self.corner_distance, 0, 0), (0, 0, self.corner_distance),
                       (self.corner_distance, 1, 0), (0, 1, self.corner_distance),
                       (0, 0, 0), (0, 1, 0))
            markers = (1, 0, 0), (0, 0, 1), (1, 1, 0), (0, 1, 1)  # , Vector3(1, 0, 1)
            markers2 = (v for v in ((1, 0, 0), (0, 1, 0), (0, 0, 1)))

            self.camera.Draw_Wireframe(canvas, corners, 5, (255, 0, 0))
            corners_projected = [p for p, d in self.camera.ProjectPoints(corners)]
            centers_projected = corners_projected[4:]
            markers_projected = [p for p, d in self.camera.ProjectPoints(markers)]
            center_camera_pos = self.camera.transform.LocalizePosition((0, 0, 0))

            def DistanceLine(a, b, width, color, tag_offset=0):
                a, b = vector.Vector(*a), vector.Vector(*b)
                canvas.Line(a, b, width, color)
                dis = a.distance(b)
                Tag((a + b) / 2, [
                    "d: " + str(round(dis, 4)),
                    "k: " + str(round((a - b).slope(), 4))
                ], color)
                return dis

            if self.settings["lengths"] and len(corners_projected) == 6 and len(markers_projected) == 4:
                d_long_right = DistanceLine(corners_projected[0], centers_projected[0], 6, (0, 100, 255))
                d_short_right = DistanceLine(markers_projected[0], centers_projected[0], 6, (255, 100, 0))
                d_long_left = DistanceLine(corners_projected[1], centers_projected[0], 6, (100, 255, 0), 2)
                d_short_left = DistanceLine(markers_projected[1], centers_projected[0], 6, (0, 100, 100), 2)
                d_center = DistanceLine(centers_projected[1], centers_projected[0], 6, (255, 0, 255), 0)
                d_side_left = DistanceLine(markers_projected[1], markers_projected[3], 6, (0, 100, 100), 0)
                if d_short_left and d_short_right:
                    r_right = d_long_right / d_short_right
                    r_left = d_long_left / d_short_left
                    # d_center * center_camera_pos.k == 1
                    # ang = 1 / math.sqrt(2)
                    ang = math.cos(self.mx * math.pi / 180)
                    te = 1 / (1 / d_center + (ang))
                    # te / (d_long_right - d_short_right) == d_center / (d_long_right)
                    # 1 - te / d_center == d_short_right / d_long_right
                    # r_both = 1 / (1 - te / d_center)
                    # idea: maybe replace 1/math.sqrt(2) with the cosine if the angle
                    r_both = 1 / (1 - 1 / (1 + d_center * ang))
                    d_short_right == d_long_right / r_both
                    d_short_right == d_long_right * (1 - 1 / (1 + d_center * ang))

                    Tag_pixel((0, 0), [
                        "",
                        "right: " + str(r_right),
                        "left: " + str(r_left),
                        "both: " + str(r_both),
                        "corner: " + str(center_camera_pos[2]),
                        str(te),
                        "" + str(d_side_left)
                    ], (255, 255, 255))
            Tag_pixel((0, 0), [
                f"{self.mx} {self.my}"
            ], (0, 255, 255))

            if self.settings["lines to center"]:
                for p in itertools.chain(centers_projected, markers_projected):
                    DistanceLine(Vector(0, 0), p, 1, (255, 0, 255))
                pass

            self.camera.DrawDots(canvas, markers, 5, (0, 0, 0))

            # C.DrawTexturedPolygon(canvas, picturePoints, face.convert())
            canvas.Circle((0, 0), 2, (255, 255, 255))
            # canvas.UnlockSurface()

    Upd = Updater(MyScene(), framerate=30, canvas=CanvasZoom(pygame.display.set_mode()))

    Upd.Play()
