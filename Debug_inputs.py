import pygame

# import pygame._sdl2.controller as con
from screenIO import *

import renderText

# con.init()
# con.set_eventstate(True)
# c = con.Controller(0)


class A(Scene):
    def o_Init(self, updater: 'Updater'):
        self.rt = renderText.RenderText(height=20)
        self.ev = ['']

    def o_Update(self, updater: 'Updater'):
        events = updater.get_events()
        canvas = updater.get_canvas()
        for event in events:
            t = str(event) + (" key: %s" % pygame.key.name(event.key) if event.type in {pygame.KEYDOWN, pygame.KEYUP} else "")
            self.ev.append(t)
            print(t)
        l = len(self.ev) - 20
        if l > 0:
            self.ev = self.ev[l:]
        # print(ev)
        # axtrl = (c.get_axis(pygame.CONTROLLER_AXIS_TRIGGERLEFT))
        # axjlx = c.get_axis(pygame.CONTROLLER_AXIS_LEFTX)
        # axjly = c.get_axis(pygame.CONTROLLER_AXIS_LEFTY)
        # axjrx = c.get_axis(pygame.CONTROLLER_AXIS_RIGHTX)
        # axjry = c.get_axis(pygame.CONTROLLER_AXIS_RIGHTY)
        # print(str(axtrl).center(5), '-' * (axtrl // 1024))
        # print(str(axjly).center(5), ('-' * (abs(axjly) // 1024)))
        canvas.Fill((0, 100, 0))
        # canvas.Circle((axjlx / 32762 / 2.1, -axjly / 32762 / 2.1), 5, (100, 100, 0))
        # canvas.Circle((axjrx / 32762 / 2.1, -axjry / 32762 / 2.1), 5, (0, 0, 100))
        # canvas.Text(ev, (0, 0))
        canvas.surface.blit(self.rt.Render('\n'.join(self.ev), wrap=0), (50, 50))


upd = Updater(scene=A(), framerate=30)
upd.Play()
