
from screenIO import *

from vector import *


class Shape:
    pass


class Reflectable:
    def Hit(self, laser: 'Laser') -> 'list[Vector]':
        "does the laser hit, and where"
        return

    def Reflect(self, origin: 'Vector', direction: 'Vector') -> 'Vector':
        "which direction is a laser facing towards direction reflected towards when hitting the reflectable at position origin"
        return
    pass


class Line(Shape, Reflectable):
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

    def Intersection(self, ray: 'Line'):
        "Use Line.Hit if you only want the line segment intersection."
        # s=\frac{\left(c-a\right).y\left(d-c\right).x-\left(c-a\right).x\ \left(d-c\right).y}{\left(b-a\right).y\left(d-c\right).x-\left(b-a\right).x\left(d-c\right).y}
        # a+s\left(b-a\right)
        cax, cay = ray.a - self.a
        dcx, dcy = ray.vector
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

    def Hit(self, laser: 'Laser'):
        a = self.Intersection(laser.line)
        if a and self.isInside(a):
            return [a]
        else:
            return []

    def Reflect(self, origin: 'Vector', direction: 'Vector') -> 'Vector':
        return self.vector.reflect(direction)

    def __str__(self) -> str:
        return 'Line from {} to {}, in direction {} '.format(self.a, self.b, self.vector)


class Laser:
    def __init__(self, origin: Vector, direction: Vector, sources: set[Reflectable] = None):
        self.line = Line.fromVector(origin, direction)
        self.sources = sources or set()

    def ReflectOnce(self, reflectors: set[Reflectable]):
        "returns new laser at the point of relfection, and the distance traveled. If there is no intersection, returns self and distance is 0."
        # idea: partition areas
        hits, point = self.ClosestHit(reflectors)
        if point:
            v = self.line.vector
            # w = v
            # for h in hits:
            #     w = w + h.Reflect(point, v) - v  # TODO: hitting a corner doesn't work like this
            s = sum((h.vector.normalized() for h in hits), start=Vector())
            w = s.reflect(v)
            if w.dotProduct(v) > 0:
                w *= -1
            a = Laser(point, w, hits)
            return a, (point - self.line.a).length()
        else:
            return self, 0

    def ClosestHit(self, reflectors: set[Reflectable]):
        distance = -1
        point = None
        hits = []
        for r in (reflectors):
            for a in r.Hit(self):
                d = self.line.dotProduct(a)
                if d > 0.000000001:
                    if distance >= d or distance == -1:
                        if distance == d:
                            hits.append(r)
                        else:
                            point = a
                            hits = [r]
                            distance = d
        # if set(self.sources).intersection(hits):
        #     print(point, self.line.a, point - self.line.a, (point - self.line.a).x == 0, distance)
        return hits, point

    def ReflectMultiple(self, reflectors: set[Reflectable], maxReflections: int = 10, maxDistance: float = None) -> tuple[list[tuple['Laser', float]], 'Laser', int, float | None]:
        "path the laser takes, the last position of the laser,reflections left over, distance left over"
        path = [(self, 0)]
        while maxReflections != 0:
            maxReflections -= 1
            a, d = path[-1][0].ReflectOnce(reflectors)
            if d:
                if maxDistance != None:
                    if maxDistance - d < 0:
                        endpoint = path[-1][0].line.a + path[-1][0].line.vector.normalized() * maxDistance
                        maxDistance = 0
                        break
                    maxDistance -= d
                path.append((a, d))
            else:
                endpoint = path[-1][0].line.a + path[-1][0].line.vector.normalized() * (maxDistance or 0)
                maxDistance = 0
                break
        else:
            endpoint = path[-1][0].line.a
        return path, Laser(endpoint, path[-1][0].line.vector), maxReflections, maxDistance
        # TODO: add sources to end laser
        # TODO: add portals


if __name__ == '__main__':
    class A(Scene):
        def o_Init(self, updater: 'Updater'):
            self.lines: list[Line] = []
            self.one: Vector = None
            self.oldmpos = Vector(0, 0)

        def o_Update(self, updater: 'Updater'):
            inputs = updater.get_inputs()
            canvas = updater.get_canvas()
            mpos = Vector(*inputs.get_mouse_position()).round(Vector(64, 64)) + Vector(32, 32)
            if inputs.keyDown(pygame.K_UP) or inputs.mouseDown(1):
                if self.one:
                    self.lines.append(Line(self.one, mpos))
                    self.one = None
                else:
                    self.one = mpos
            if inputs.keyPressed(pygame.K_DOWN) or inputs.mousePressed(3):
                GRAB_DISTANCE = 100

                def key2(v: Vector):
                    return (v - self.oldmpos).lengthSq()

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
            # for i in range(len(self.lines) - 1):
            #     a = self.lines[i].Intersection(self.lines[-1])
            #     if a:
            #         b = self.lines[i].isInside(a)
            #         canvas.Circle(a, 4 + 8 * b, (100 + 50 * b, 100 - 100 * b, 50))
            if len(self.lines) > 1:
                l = Laser(self.lines[0].a, self.lines[0].vector)
                p, e, *_ = l.ReflectMultiple(self.lines[1:], -1, self.lines[0].vector.length() * 4)
                canvas.Lines([a.line.a for a, b in p] + [e.line.a], 5, (200, 100, 100))
                for a, b in p:
                    canvas.Circle(a.line.a, 1 + min(b, 100) // 10, (0, 0, min(b, 100)))
            for line in self.lines:
                line.Draw(canvas)
                canvas.Circle(line.a, 5, (0, 0, 0))
            s = pygame.Surface((64, 64))
            s.fill((50, 0, 50))
            canvas.surface.blit(s, canvas.convert(mpos - Vector(32, 32)), special_flags=pygame.BLEND_ADD)
            canvas.Circle(mpos, 10, (100, 200, 100))
            self.oldmpos = mpos
            pass

Updater(A(), CanvasNoZoom(pygame.display.set_mode())).Play()
