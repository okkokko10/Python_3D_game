
from screenIO import *

from vector import *


class Shape:
    pass


class Line(Shape):
    def __init__(self, start: Vector, end: Vector):
        self.a = start
        self.b = end

    @staticmethod
    def fromVector(origin: Vector, direction: Vector):
        return Line(origin, origin + direction)

    @property
    def vector(self): return self.b - self.a

    def projectPoint(self, point: Vector):
        return (self.vector).project(point - self.a) + self.a

    def Intersection(self, other: 'Line'):
        # s=\frac{\left(c-a\right).y\left(d-c\right).x-\left(c-a\right).x\ \left(d-c\right).y}{\left(b-a\right).y\left(d-c\right).x-\left(b-a\right).x\left(d-c\right).y}
        # a+s\left(b-a\right)
        cax, cay = other.a - self.a
        dcx, dcy = other.vector
        bax, bay = self.vector
        sd = (bay * dcx - bax * dcy)
        if not sd:
            return None
        s = (cay * dcx - cax * dcy) / sd
        return self.a + s * (self.vector)

    def isInside(self, point: Vector):
        "it doesn't count if the point is at the end position"
        in1 = (point - self.a).dotProduct(self.vector)
        in2 = -(point - self.b).dotProduct(self.vector)
        return (in1 >= 0) and (in2 > 0)

    def dotProduct(self, point: Vector):
        "the larger the value, the farther the point is in the line's direction. negative values mean the point is behind"
        in1 = (point - self.a).dotProduct(self.vector)
        return in1

    def Draw(self, canvas: 'Canvas', color=(255, 255, 255), width=1):
        canvas.Line(self.a, self.b, width, color)


class Laser:
    def __init__(self, origin: Vector, direction: Vector):
        self.line = Line.fromVector(origin, direction)

    def Reflect(self, reflectors: list[Line]):
        "returns new laser at the point of relfection, and the distance traveled. If there is no intersection, returns self and distance is 0."
        # idea: partition areas
        hits, point, distance = self.ClosestHit(reflectors)
        if point:
            v = self.line.vector
            for h in hits:
                v = h.vector.reflect(v)
            a = Laser(point, v)
            return a, (point - self.line.a).length()
        else:
            return self, 0

    def ClosestHit(self, reflectors: list[Line]):
        distance = -1
        point = None
        hits = []
        for r in reflectors:
            a = r.Intersection(self.line)
            if a and r.isInside(a):
                d = self.line.dotProduct(a)
                if d > 0:
                    if distance >= d or distance == -1:
                        if distance == d:
                            hits.append(r)
                        else:
                            point = a
                            hits = [r]
                            distance = d
        return hits, point, distance

    def ReflectMultiple(self, reflectors: list[Line], maxreflections=5):
        path = [(self, 0)]
        for i in range(maxreflections):
            a, d = path[-1][0].Reflect(reflectors)
            if d:
                path.append((a, d))
            else:
                break
        return path


if __name__ == '__main__':
    class A(Scene):
        def o_Init(self, updater: 'Updater'):
            self.lines: list[Line] = []
            self.one: Vector = None

        def o_Update(self, updater: 'Updater'):
            inputs = updater.get_inputs()
            canvas = updater.get_canvas()
            mpos = Vector(*inputs.get_mouse_position())
            if inputs.keyDown(pygame.K_UP):
                if self.one:
                    self.lines.append(Line(self.one, mpos))
                    self.one = None
                else:
                    self.one = mpos
            if inputs.keyPressed(pygame.K_DOWN):
                GRAB_DISTANCE = 30

                def key2(v: Vector):
                    return (v - mpos).lengthSq()

                def key(line: Line):
                    return min(key2(line.a), key2(line.b))
                if len(self.lines):
                    l = min(self.lines, key=key)
                    i = self.lines.index(l)
                    if key2(l.a) < key2(l.b):
                        if key2(l.a) < GRAB_DISTANCE**2:
                            self.lines[i] = Line(mpos, l.b)
                    elif key2(l.b) < GRAB_DISTANCE**2:
                        self.lines[i] = Line(l.a, mpos)
            canvas.Fill((0, 100, 100))
            for i in range(len(self.lines) - 1):
                a = self.lines[i].Intersection(self.lines[-1])
                if a:
                    b = self.lines[i].isInside(a)
                    canvas.Circle(a, 4 + 8 * b, (100 + 50 * b, 100 - 100 * b, 50))
            if len(self.lines) > 1:
                l = Laser(self.lines[0].a, self.lines[0].vector)
                p = l.ReflectMultiple(self.lines[1:])
                canvas.Lines([a.line.a for a, b in p] + [p[-1][0].line.b], 5, (200, 100, 100))
            for line in self.lines:
                line.Draw(canvas)
            pass

Updater(A(), CanvasNoZoom(pygame.display.set_mode())).Play()
