# from orientation import *
import itertools
import numpy as np
import screenIO
import orientation2 as oi


def isSmall(x):
    return abs(x) < (1 << 16)


def clamp(x, y):
    while not (isSmall(x) and isSmall(y)):
        x //= 1 << 4
        y //= 1 << 4
    return x, y


class Camera:
    def __init__(self, height=1, width=1, zoom=400, transform: oi.Transform = None):
        "zoom: how many pixels is a x=y"
        self.transform = transform or oi.Transform(oi.Vector3(0, 0, 0), oi.IDENTITY)
        self.height = height
        self.width = width
        self.zoom = zoom

    def ProjectPosition(self, other: oi.Vector3, countOutside=True) -> tuple[tuple[int, int], float]:
        p = self.transform.LocalizePosition(other)
        return self.Projection(p), p[2]
        # x, y, z = p
        # if z <= 0:
        #     return None
        # if not countOutside and (abs(x) * 2 > self.width * z or abs(y) * 2 > self.height * z):
        #     return None
        # x1, y1 = x / z, y / z
        # x1, y1 = x, y
        # if isSmall(x) and isSmall(y):
        #     return x, y
        # return clamp(x1, y1)

    def Projection(self, vector: oi.Vector3) -> tuple[int, int]:
        x, y, z = vector
        if z <= 0.05:
            return None
        x1, y1 = self.zoom * x // z + self.width // 2, -self.zoom * y // z + self.height // 2

        return clamp(x1, y1)

    def DrawLines(self, canvas: 'screenIO.Canvas', vectors, width, color):
        poslist = self.ProjectPoints(vectors)
        if len(poslist) >= 2:
            canvas.Lines(poslist, width, color)

    def DrawDots(self, canvas: 'screenIO.Canvas', vectors, radius, color):
        for v in vectors:
            p, z = self.ProjectPosition(v)
            if p:
                canvas.Circle(p, self.zoom * radius // z, color)
            pass

    def ProjectPoints(self, vectors, countOutside=True):
        return [p for p in (self.ProjectPosition(v, countOutside) for v in vectors) if p[0]]

    def DrawTexturedPolygon(self, canvas: 'screenIO.Canvas', vectors, image):
        poslist = self.ProjectPoints(vectors, True)
        if len(poslist) >= 3:
            # canvas.TexturedPolygon(poslist, image)
            canvas.StretchTexture((p for (p, z) in poslist), image)

    def Draw_Wireframe(self, canvas: 'screenIO.Canvas', vectors, width, color):
        poslist = self.ProjectPoints(vectors)
        # positions = (p for (p, z) in poslist)
        for a, b in itertools.combinations(poslist, 2):
            canvas.Line(a[0], b[0], self.zoom * width * 2 // (a[1] + b[1]), color)
