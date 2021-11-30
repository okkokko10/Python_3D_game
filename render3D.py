from orientation import *
from screenIO import *


class Camera:
    def __init__(self):
        self.transform = Transform(Vector3(0, 0, 0), Quaternion(1))
        self.height = 1
        self.width = 1

    def ProjectPosition(self, other: 'Vector3', countOutside=False):
        p = self.transform.LocalizePosition(other)
        if p.k <= 0:
            return None
        if not countOutside and (abs(p.i) * 2 > self.width * p.k or abs(p.j) * 2 > self.height * p.k):
            return None
        x, y = p.i / p.k, p.j / p.k
        return x, y

    def DrawLines(self, canvas: 'Canvas', vectors, width, color):
        poslist = self.ProjectPoints(vectors)
        if len(poslist) >= 2:
            canvas.Lines(poslist, width, color)

    def DrawDots(self, canvas: 'Canvas', vectors, radius, color):
        for v in vectors:
            p = self.ProjectPosition(v)
            if p:
                canvas.Circle(p, radius, color)
            pass

    def ProjectPoints(self, vectors, countOutside=False):
        return [p for p in (self.ProjectPosition(v, countOutside) for v in vectors) if p]

    def DrawTexturedPolygon(self, canvas: 'Canvas', vectors, image):
        poslist = self.ProjectPoints(vectors, True)
        if len(poslist) >= 3:
            # canvas.TexturedPolygon(poslist, image)
            canvas.StretchTexture(poslist, image)
