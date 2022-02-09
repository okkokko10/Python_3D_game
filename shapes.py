
from screenIO import *

from vector import *


class Shape:
    pass


class Reflectable:
    def Hit(self, laser: 'Laser') -> 'list[Vector]':
        "does the laser hit, and where"
        raise NotImplementedError

    def Reflect(self, laser: 'Laser', position: 'Vector') -> 'Laser':
        "Old: which direction is a laser facing towards direction reflected towards when hitting the reflectable at position origin"
        raise NotImplementedError


class Line(Shape, Reflectable):
    def __init__(self, start: Vector, end: Vector, is_cap_a=True, is_cap_b=False):
        self.a = start
        self.b = end
        self.is_cap_a = is_cap_a
        self.is_cap_b = is_cap_b
        super().__init__()

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
        "it doesn't count if the point is at the end position -- when cap_a and cap_b are default"
        in1 = (point - self.a).dotProduct(self.vector)
        if ((in1 >= 0) if self.is_cap_a else (in1 > 0)):
            in2 = -(point - self.b).dotProduct(self.vector)
            return (in2 >= 0) if self.is_cap_b else (in2 > 0)
        else:
            return False

    def dotProduct(self, point: Vector):
        "the larger the value, the farther the point is in the line's direction. negative values mean the point is behind"
        in1 = (point - self.a).dotProduct(self.vector)
        return in1

    def Draw(self, canvas: 'Canvas', color=(255, 255, 255), width=1):
        canvas.Line(self.a, self.b, width, color)
        if self.is_cap_a:
            canvas.Circle(self.a, width * 3, color)
        if self.is_cap_b:
            canvas.Circle(self.b, width * 3, color)

    def Hit(self, laser: 'Laser'):
        a = self.Intersection(laser.line)
        if a and self.isInside(a):
            return [a]
        else:
            return []

    def Reflect(self, laser: 'Laser', position: 'Vector') -> 'Laser':
        return Laser(position, self.vector.reflect(laser.line.vector))

    def __str__(self) -> str:
        return 'Line from {} to {}, in direction {} '.format(self.a, self.b, self.vector)

    def distance(self, point: Vector):
        "distance to the line. use Line.distanceSegment for the line segment's distance"
        return abs(self.vector.normal().projectScalar(point - self.a))

    def distanceSq(self, point: Vector):
        "square distance to the line. use Line.distanceSegmentSq for the line segment's distance"
        return self.vector.normal().projectScalarSq(point - self.a)

    def distanceSegment(self, point: Vector) -> float:

        # if self.isInside(point):
        #     return self.distance(point)
        # else:
        #     return math.sqrt(min((self.a - point).lengthSq(), (self.b - point).lengthSq()))

        if (point - self.a).dotProduct(self.vector) > 0:
            if -(point - self.b).dotProduct(self.vector) > 0:
                return self.distance(point)
            else:
                return (self.b - point).length()
        else:
            return (self.a - point).length()

    def distanceSegmentSq(self, point: Vector) -> float:
        if (point - self.a).dotProduct(self.vector) > 0:
            if -(point - self.b).dotProduct(self.vector) > 0:
                return self.distanceSq(point)
            else:
                return (self.b - point).lengthSq()
        else:
            return (self.a - point).lengthSq()


class Sphere(Shape, Reflectable):

    def __init__(self, center: Vector, radiusSq: float):
        self.center = center
        self.edge = center + Vector(math.sqrt(radiusSq), 0)
        super().__init__()

    @property
    def radiusVector(self):
        return self.edge - self.center

    @property
    def radiusSq(self):
        return self.radiusVector.lengthSq()

    @property
    def radius(self) -> float:
        return math.sqrt(self.radiusSq)

    def Hit(self, laser: 'Laser'):
        "returns positions where the laser intersects the sphere."
        lsq = laser.line.vector.lengthSq()
        c = (self.center - laser.line.a).complexMul(laser.line.vector.complexConjugate())
        dsq = lsq * self.radiusSq - c.y**2
        if dsq < 0:
            return []
        v = laser.line.vector / lsq
        if dsq == 0:
            return [c.x * v + laser.line.a]
        d = math.sqrt(dsq)
        return [(c.x + d) * v + laser.line.a, (c.x - d) * v + laser.line.a]

    def Reflect(self, laser: 'Laser', position: 'Vector') -> 'Laser':
        return Laser(position, (position - self.center).complexMul(Vector(0, 1)).reflect(laser.line.vector))

    def Draw(self, canvas: 'Canvas', color=(255, 255, 255), width=1):
        canvas.Circle(self.center, self.radius, color, width)


class Movable:
    def movable_attributes(self) -> tuple[str]:
        """Override this. Empty string is a keyword for whole.
        attributes must be absolute positions that can be set independently of each other"""
        return ()

    def movable_closest(self, position: Vector) -> tuple[str, float]:
        "Maybe override this. Returns closest attribute, and the squared distance to the attribute"
        def key(k):
            return (self.movable_Get(k) - position).lengthSq()
        a = min(self.movable_attributes(), key=key)
        return a, key(a)

    def movable_distanceSq(self, position: Vector) -> float:
        "Override this. Return the square distance to the position, for finding the closest movable"
        return self.movable_closest(position)[0]
        # raise NotImplementedError

    def movable_OnPick(self, mover: 'Mover', attr: 'str'):
        pass

    def movable_Get(self, attr: str) -> Vector:
        return getattr(self, attr)

    def movable_Set(self, attr: str, value: Vector):
        assert attr
        setattr(self, attr, value)

    def MovePartTo(self, attr: str, position: 'Vector'):
        self.movable_Set(attr, position)

    def Move(self, attr: str, movement: 'Vector'):
        if attr:  # !=""
            self.movable_Set(attr, self.movable_Get(attr) + movement)
        else:
            self.MoveWhole(movement)

    def MoveWhole(self, movement: 'Vector'):
        for k in self.movable_attributes():
            self.movable_Set(k, self.movable_Get(k) + movement)

    def MoveWholeTo(self, attr: str, position: 'Vector'):
        self.MoveWhole(position - self.movable_Get(attr))

    def Rotozoom(self, center: Vector, zoom: Vector):
        # might be lossy
        self.Warp(lambda old_pos: (old_pos - center).complexMul(zoom) + center)

    def Rotate(self, center: Vector, start: Vector, stop: Vector):
        a = start - center
        b = stop - center
        self.Rotozoom(center, b.complexDiv(a))

    def Warp(self, func: Callable[[Vector], Vector]):
        "applies func to attributes"
        for k in self.movable_attributes():
            old_pos = self.movable_Get(k)
            self.movable_Set(k, func(old_pos))


class MovableLine(Line, Movable):
    def movable_attributes(self):
        return 'a', 'b'

    def movable_distanceSq(self, position: Vector) -> float:
        return self.distanceSegmentSq()


class MovableSphere(Sphere, Movable):
    def movable_attributes(self) -> tuple[str]:
        return "center", "edge"

    def movable_distanceSq(self, position: Vector) -> float:
        return self.movable_closest(position)[1]

# TODO: rotation, highlighting an object


class Mover:
    def __init__(self):
        self._position = Vector(0, 0)
        self._movement = Vector(0, 0)
        self._picked = None
        self._pickedAttr = None
        self._down = False
        "if on the previous frame the mover was pressed down"
        self._whole = False
        "if the whole Movable is moved"
        pass

    def update(self, position: Vector, down: bool, movables: list[Movable], whole=False) -> None:
        self._movement = position - self._position
        self._position = position
        self._whole = whole
        if self._picked and self._picked not in movables:
            self._picked, self._pickedAttr = None, None
        if down and not self._down:  # down
            self._picked, self._pickedAttr = self.findClosest(self._position, movables)
            if self._picked and self._pickedAttr:  # move the picked point to the cursor, with the other points if total is True
                self._picked.movable_OnPick(self, self._pickedAttr)
                if self._whole:
                    self._picked.MoveWholeTo(self._pickedAttr, self._position)
                else:
                    self._picked.MovePartTo(self._pickedAttr, self._position)
        elif self._down and not down:  # up
            self._picked, self._pickedAttr = None, None
        elif self._picked and self._down:  # do not execute immediately after picking
            if self._whole:
                self._picked.MoveWhole(self._movement)
            else:
                self._picked.Move(self._pickedAttr, self._movement)
        self._down = down

    def findClosest(self, position: Vector, movables: list[Movable], maxDistanceSq=-1) -> tuple[Movable, str] | tuple[None, None]:
        closestP = None
        closestAttr = None
        distanceSq = maxDistanceSq
        for p in movables:
            if not isinstance(p, Movable):
                raise TypeError("{} is not Movable".format(p))
                continue
            attr, dsq = p.movable_closest(position)
            if distanceSq > dsq or distanceSq == -1:
                closestP = p
                closestAttr = attr
                distanceSq = dsq
        # if closestP is None:
        #     return None, None
        # else:
        return closestP, closestAttr


class Laser:
    def __init__(self, origin: Vector, direction: Vector, sources: set[Reflectable] = None):
        self.line = Line.fromVector(origin, direction)
        self.sources = sources or set()

    def ReflectOnce(self, reflectors: set[Reflectable]):
        "returns new laser at the point of relfection, and the distance traveled. If there is no intersection, returns self and distance is 0."
        # idea: partition areas
        hits, point = self.ClosestHit(reflectors)
        if point:
            # w = v
            # for h in hits:
            #     w = w + h.Reflect(point, v) - v  # TODO: hitting a corner doesn't work like this
            # s = sum((h.vector.normalized() for h in hits), start=Vector())
            # w = s.reflect(v)
            # if w.dotProduct(v) > 0:
            #     w *= -1
            if len(hits) == 1:
                a = hits[0].Reflect(self, point)
            else:
                w = -self.line.vector
                a = Laser(point, w)
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
                        endpoint = path[-1][0].line.a + path[-1][0].line.vector.unit() * maxDistance
                        maxDistance = 0
                        break
                    maxDistance -= d
                path.append((a, d))
            else:
                endpoint = path[-1][0].line.a + path[-1][0].line.vector.unit() * (maxDistance or 0)
                maxDistance = 0
                break
        else:
            endpoint = path[-1][0].line.a
        return path, Laser(endpoint, path[-1][0].line.vector), maxReflections, maxDistance
        # TODO: add sources to end laser
        # TODO: add portals


def main():
    class A(Scene):
        def o_Init(self, updater: 'Updater'):
            self.shapes: list[Shape] = []
            self.one: Vector = None
            self.oldmpos = Vector(0, 0)
            self.mover = Mover()

        def o_Update(self, updater: 'Updater'):
            GRID = Vector(10, 10)
            inputs = updater.get_inputs()
            canvas = updater.get_canvas()
            mpos = Vector(*inputs.get_mouse_position()).round(GRID) + GRID / 2
            if inputs.keyDown(pygame.K_UP) or inputs.mouseDown(1):
                if self.one:
                    self.shapes.append(MovableLine(self.one, mpos))
                    self.one = None
                else:
                    self.one = mpos
            if inputs.keyPressed(pygame.K_LEFT) or inputs.mousePressed(6):
                if self.one:
                    self.shapes.append(MovableSphere(self.one, (self.one - mpos).lengthSq()))
                    self.one = None
            movedown = inputs.keyPressed(pygame.K_DOWN) or inputs.mousePressed(3)
            movewhole = inputs.keyPressed(pygame.K_RSHIFT) or inputs.keyPressed(pygame.K_LSHIFT)
            self.mover.update(mpos, movedown, self.shapes, movewhole)

            canvas.Fill((0, 100, 100))
            # for i in range(len(self.lines) - 1):
            #     a = self.lines[i].Intersection(self.lines[-1])
            #     if a:
            #         b = self.lines[i].isInside(a)
            #         canvas.Circle(a, 4 + 8 * b, (100 + 50 * b, 100 - 100 * b, 50))
            if len(self.shapes) >= 1:
                l = Laser(self.shapes[0].a, self.shapes[0].vector)
                p, e, *_ = l.ReflectMultiple(self.shapes[1:], -1, self.shapes[0].vector.length() * 4)
                canvas.Lines([a.line.a for a, b in p] + [e.line.a], 5, (200, 100, 100))
                for a, b in p:
                    canvas.Circle(a.line.a, 1 + min(b, 100) // 10, (0, 0, min(b, 100)))
            for line in self.shapes:
                line.Draw(canvas)
            s = pygame.Surface((GRID.x, GRID.y,))
            s.fill((50, 0, 50))
            canvas.surface.blit(s, canvas.convert(mpos - GRID / 2), special_flags=pygame.BLEND_ADD)
            canvas.Circle(mpos, 10, (100, 200, 100))
            if self.one:
                canvas.Circle(self.one, 10, (250, 0, 100))
            self.oldmpos = mpos
            pass
    Updater(A(), Canvas(pygame.display.set_mode())).Play()


if __name__ == '__main__':
    main()
