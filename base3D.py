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
import raymarching as rm


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
        mdx, mdy = inputs.get_mouse_movement().complexConjugate() * speed + inputs.arrows_vector()
        self.x += mdx
        self.y += mdy


class Template_Player:
    def __init__(self, transform: oi.Transform = None, speed: float = 1 / 200, mouse_sensitivity: float = 1 / 4):
        self.transform = oi.Transform.Get_Identity_Transform() if transform is None else transform
        self.rotation_controller = RotationController()
        self.speed = speed
        self.mouse_sensitivity = mouse_sensitivity

    def Update(self, updater: screenIO.Updater):
        self.rotation_controller.take_mouse(updater.inputs, self.mouse_sensitivity)
        self.transform.rotation = self.rotation_controller.rot()
        self.transform.Move((oi.xy_to_x0y(updater.inputs.WASD()) + oi.Vector3(0, updater.inputs.Pressed("space") -
                            updater.inputs.Pressed("left shift"), 0)) * updater.deltaTime * self.speed)


def cubegrid(x, y, z):
    return [oi.Vector3(a, b, c) for a in range(x) for b in range(y) for c in range(z)]


if __name__ == '__main__':
    class MyScene(Scene):
        def o_Init(self, updater: 'Updater'):
            updater.get_inputs().LockMouse()

            self.camera = Camera(updater.canvas.height, updater.canvas.width, updater.canvas.height)
            self.player = Template_Player()
            self.player.transform.position = oi.Vector3(-1, 0, -1)
            a = [
                *cubegrid(3, 2, 3),
                oi.Vector3(1, 2, 1),
                oi.Vector3(1, 2, 2),
                oi.Vector3(2, 2, 2)
            ]
            self.test_object = TriDimObject(None, a)
            self.object1 = TriDimObject(None, [
                oi.Vector3(0, 0, 0),
                oi.Vector3(0, 0, 1)
            ])
            self.object1_player = Template_Player()
            self.movement_mode = True
            self.settings = {"crosshair": True, "info": True}
            self.object1_rotation = RotationController()
            self.zooming = 4
            self.raycamera = rm.RayCamera(*(updater.canvas.size // self.zooming), self.camera.zoom // self.zooming)
            self.ray_object_list = rm.Raymarch_list()
            self.ray_object_list.spheres = [rm.Sphere(oi.Vector3(0, 0, 0), 1, (100, 100, 0)),
                                            rm.Sphere(oi.Vector3(0, 3, 0), 2, (0, 100, 0)),
                                            rm.Sphere(oi.Vector3(0, 0, 0), 15, (0, 0, 255))]
            self.text_renderer = renderText.RenderText(25)

        def o_Update(self, updater: 'Updater'):
            canvas = updater.get_canvas()
            canvas.Fill((0, 0, 100))
            inputs = updater.get_inputs()
            deltaTime = updater.get_deltaTime()
            WASDvector = oi.xy_to_x0y(inputs.WASD())
            text_to_render = []
            text_to_render.append("milliseconds spent on previous frame: %s" % deltaTime)

            if inputs.Pressed("mouse left", "x"):
                deltaTime /= 5
            if inputs.Pressed("mouse right", "c"):
                deltaTime *= 5
            if inputs.Down("f"):
                self.movement_mode = not self.movement_mode

            if self.movement_mode:
                self.player.Update(updater)
                self.camera.transform = self.player.transform
            else:
                self.object1_player.Update(updater)
                self.object1.transform = self.object1_player.transform

            if inputs.Pressed("q"):
                self.camera.zoom *= 1.1
            if inputs.Pressed("e"):
                self.camera.zoom /= 1.1
            # if inputs.Down("mouse up"):
            #     self.raycamera.depth += 1
            # if inputs.Down("mouse down"):
            #     self.raycamera.depth -= 1
            if inputs.Pressed("right shift"):
                if inputs.Down("1"):
                    self.settings["crosshair"] ^= True
                if inputs.Down("2"):
                    self.settings["info"] ^= True
            if inputs.Pressed("1"):
                self.raycamera.iteration_amount += inputs.get_mousewheel()
            if inputs.Pressed("2"):
                self.zooming += inputs.get_mousewheel()
                self.zooming = max(self.zooming, 1)
            self.raycamera.width, self.raycamera.height, self.raycamera.zoom = updater.canvas.width // self.zooming, updater.canvas.height // self.zooming, self.camera.zoom // self.zooming

            if False:
                ax, ay = 64, 64
                rays = rm.rays(self.camera.transform.LocalizeRotation(self.object1.transform.rotation), ax, ay)
                poos = self.camera.transform.LocalizePosition(self.object1.transform.position)
                for x, y in itertools.product(range(ax), range(ay)):
                    radius = 0.01
                    color = (x * (256 // ax), y * (265 // ay), 0)
                    b = rays[x, y]
                    a = b + poos
                    p = self.camera.Projection(a)
                    z = a[2]
                    if p:
                        canvas.Circle(p, self.camera.zoom * radius // z, color)
            if False:
                ax, ay = 100, 100
                rays = rm.rays2(self.camera.transform.LocalizeRotation(self.object1.transform.rotation), ax, ay)
                poos = self.camera.transform.LocalizePosition(self.object1.transform.position)
                x, y, z = rays + poos
                radius = 0.01
                color = (0, 0, 0)
                x1 = self.camera.zoom * x // z + self.camera.width // 2
                y1 = - self.camera.zoom * y // z + self.camera.height // 2
                z1 = z
                for x2, y2, z2 in zip(x1, y1, z1):
                    if z2 >= 0.01 and x2 and y2:
                        canvas.Circle((x2, y2), self.camera.zoom * radius // z2, color)
            if True:
                self.raycamera.transform = self.camera.transform
                rayimage, ray_info = self.raycamera.Draw(self.ray_object_list)
                rayimage = pygame.transform.flip(rayimage, False, True)
                pygame.transform.scale(rayimage, (*canvas.size,), canvas.surface)
                text_to_render.extend(ray_info)
                text_to_render.append("pixelation: %s" % self.zooming)
                # canvas.Blit(a, (0, 0))
                # for sphere in self.ray_object_list.spheres:
                #     self.camera.DrawDots(canvas, [sphere.position], sphere.radius, (0, 255, 0))
            if False:
                self.camera.DrawDots(canvas, self.test_object.global_vertices(), 0.1, pygame.Color(255, 255, 0))
                self.camera.Draw_Wireframe(canvas, self.test_object.global_vertices(), 0.05, pygame.Color(255, 255, 0))
                self.camera.DrawDots(canvas, self.object1.global_vertices(), 0.1, pygame.Color(255, 0, 0))

            if self.settings["crosshair"]:
                canvas.Circle(canvas.center, 2, (255, 255, 255))  # reticle
            if self.settings["info"]:
                eff = renderText.TextEffects(default=renderText.Effect((0, 255, 0), (50, 50, 50)))
                sf = self.text_renderer.RenderEffects(eff.Prepare(text_to_render))
                canvas.Blit(sf, (0, 0))

    Upd = Updater(MyScene(), framerate=60, canvas=Canvas(pygame.display.set_mode()))

    Upd.Play()
