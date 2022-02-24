# from orientation import *
import screenIO
import orientation2 as oi


def isSmall(x):
    return abs(x) < (1 << 16)


def clamp(x, y):
    while not (isSmall(x) and isSmall(y)):
        x /= 1 << 4
        y /= 1 << 4
    return x, y


class Camera:
    def __init__(self):
        self.transform = oi.Transform(oi.Vector3(0, 0, 0), oi.IDENTITY)
        self.height = 1
        self.width = 1

    def ProjectPosition(self, other: 'oi.Vector', countOutside=True):
        p = self.transform.LocalizePosition(other)
        x, y, z = p
        if z <= 0:
            return None
        if not countOutside and (abs(x) * 2 > self.width * z or abs(y) * 2 > self.height * z):
            return None
        x1, y1 = x / z, y / z
        # x1, y1 = x, y
        # if isSmall(x) and isSmall(y):
        #     return x, y
        return clamp(x1, y1)

    def DrawLines(self, canvas: 'screenIO.Canvas', vectors, width, color):
        poslist = self.ProjectPoints(vectors)
        if len(poslist) >= 2:
            canvas.Lines(poslist, width, color)

    def DrawDots(self, canvas: 'screenIO.Canvas', vectors, radius, color):
        for v in vectors:
            p = self.ProjectPosition(v)
            if p:
                canvas.Circle(p, radius, color)
            pass

    def ProjectPoints(self, vectors, countOutside=True):
        return [p for p in (self.ProjectPosition(v, countOutside) for v in vectors) if p]

    def DrawTexturedPolygon(self, canvas: 'screenIO.Canvas', vectors, image):
        poslist = self.ProjectPoints(vectors, True)
        if len(poslist) >= 3:
            # canvas.TexturedPolygon(poslist, image)
            canvas.StretchTexture(poslist, image)

    def Draw_Wireframe(self, canvas: 'screenIO.Canvas', vectors, width, color):
        poslist = self.ProjectPoints(vectors)
        canvas.GroupLines(poslist, width, color)
