
from itertools import chain
from typing import Any
from screenIO import *

from vector import *


class Drawable:
    def Draw(self, canvas: 'Canvas', color=(255, 255, 255), *args, **kwargs):
        # raise NotImplementedError
        pass

    def Glow(self, canvas: 'Canvas', color=(100, 255, 100), *args, **kwargs):
        # raise NotImplementedError
        pass

    pass


class Reflectable:
    def Hit(self, laser: 'Laser') -> list[tuple[Vector, Any]]:
        "does the laser hit, and where + extra information which is given to Reflect"
        raise NotImplementedError

    def Reflect(self, laser: 'Laser', position: 'Vector', extra_info: Any = None) -> 'Laser':
        "Old: which direction is a laser facing towards direction reflected towards when hitting the reflectable at position origin"
        raise NotImplementedError


class MoveAttribute:
    "immutable"

    def __init__(self, *args, is_special=False):
        self.args = args
        self.is_special = is_special
        "if the attribute should compare true with only itself"

    def __eq__(self, other):
        return self is other if self.is_special else (isinstance(other, MoveAttribute) and self.args == other.args)

    def __hash__(self):
        return hash(self.args)
    WHOLE: "MoveAttribute"
    "sentinel for movable that means all attributes"


MoveAttribute.WHOLE = MoveAttribute(is_special=True)


class Movable:
    """Override needed when subclassing:
    attributes
    Get
    Set
    """
    parent: "Has_Movable"

    def __init__(self, parent: "Has_Movable"):
        self.parent = parent

    def attributes(self) -> Iterable[MoveAttribute]:
        """Override this.
        must be an iterable of MoveAttribute objects, containing all attributes that are valid inputs to Get and Set
        attributes must be absolute positions that can be set independently of each other"""
        return ()

    def Get(self, attr: MoveAttribute) -> Vector:
        "Override this."
        raise NotImplementedError
        return getattr(self, attr)

    def Set(self, attr: MoveAttribute, value: Vector):
        "Override this."
        raise NotImplementedError
        setattr(self, attr, value)

    def Warp(self, attrs: Iterable[MoveAttribute], func: Callable[[Vector], Vector]):
        "applies func to all given attrs"
        for attr in attrs:
            self.Set(attr, func(self.Get(attr)))

    def closest(self, position: Vector) -> tuple[MoveAttribute, float]:
        "Maybe override this. Returns closest attribute, and the squared distance to the attribute"
        def key(k):
            return (self.Get(k) - position).lengthSq()
        a = min(self.attributes(), key=key)
        return a, key(a)

    def distanceSq(self, position: Vector) -> float:
        "Maybe override this. Return the square distance to the position, for finding the closest movable"
        return self.closest(position)[1]
        # raise NotImplementedError

    def OnPick(self, mover: 'Mover', attr: MoveAttribute):
        "What happens when a mover picks up this Movable"
        pass

    def MovePartTo(self, attr: MoveAttribute, position: 'Vector'):
        self.Set(attr, position)

    def Move(self, attr: MoveAttribute, movement: 'Vector'):
        if attr == MoveAttribute.WHOLE:
            self.MoveWhole(movement)
        else:
            self.Set(attr, self.Get(attr) + movement)

    def MoveWhole(self, movement: 'Vector'):
        self.WarpAll(lambda v: v + movement)
        # for k in self.movable_attributes():
        #     self.movable_Set(k, self.movable_Get(k) + movement)

    def MoveWholeTo(self, attr: MoveAttribute, position: 'Vector'):
        "offset the Movable so that the given attribute goes in the given position"
        self.MoveWhole(position - self.Get(attr))

    def Rotozoom(self, center: Vector, zoom: Vector):
        "complex multiplies the Movable by the zoom vector, using center as the origin"
        # might be lossy
        self.WarpAll(lambda old_pos: (old_pos - center).complexMul(zoom) + center)

    def Rotate(self, center: Vector, start: Vector, stop: Vector):
        "rotates the Movable around the center so that what was at start goes to stop"
        a = start - center
        b = stop - center
        self.Rotozoom(center, b.complexDiv(a))

    def WarpAll(self, func: Callable[[Vector], Vector]):
        "applies func to attributes' positions"
        # for k in self.movable_attributes():
        #     old_pos = self.movable_Get(k)
        #     self.movable_Set(k, func(old_pos))
        self.Warp(self.attributes(), func)


class Has_Movable:
    "class that tells that the object has a Movable attribute"
    movable: Movable
    pass


class Shape(Reflectable, Drawable, Has_Movable):
    pass


class Line(Shape):
    class _Movable(Movable):
        parent: "Line"

        _movable_attributes = MoveAttribute("a"), MoveAttribute("b")

        def attributes(self):
            return self._movable_attributes

        def Get(self, attr: MoveAttribute) -> Vector:
            return getattr(self.parent, attr.args[0])

        def Set(self, attr: MoveAttribute, value: Vector):
            setattr(self.parent, attr.args[0], value)

        def distanceSq(self, position: Vector) -> float:
            return self.parent.distanceSegmentSq()

    def __init__(self, start: Vector, end: Vector, is_cap_a=True, is_cap_b=False):
        self.a = start
        self.b = end
        self.is_cap_a = is_cap_a
        self.is_cap_b = is_cap_b
        self.movable = type(self)._Movable(self)
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

    def Glow(self, canvas: 'Canvas', color=(100, 255, 100), width=1):
        offset = width * self.vector.unit().normal()
        for i in 1, -1:
            canvas.Line(self.a + offset * i, self.b + offset * i, width, color)
        # if self.is_cap_a:
        #     canvas.Circle(self.a, width * 3, color)
        # if self.is_cap_b:
        #     canvas.Circle(self.b, width * 3, color)

    def Hit(self, laser: 'Laser'):
        a = self.Intersection(laser.line)
        if a and self.isInside(a):
            return [(a, None)]
        else:
            return []

    def Reflect(self, laser: 'Laser', position: 'Vector', extra_info: None) -> 'Laser':
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
        "returns the distance to the closest point on the line segment."
        if (point - self.a).dotProduct(self.vector) > 0:
            if -(point - self.b).dotProduct(self.vector) > 0:
                return self.distanceSq(point)
            else:
                return (self.b - point).lengthSq()
        else:
            return (self.a - point).lengthSq()


class Sphere(Shape):
    class _Movable(Movable):
        parent: "Sphere"

        _movable_attributes = MoveAttribute("center"), MoveAttribute("edge")

        def attributes(self):
            return self._movable_attributes

        def Get(self, attr: MoveAttribute) -> Vector:
            return getattr(self.parent, attr.args[0])

        def Set(self, attr: MoveAttribute, value: Vector):
            setattr(self.parent, attr.args[0], value)

        # def distanceSq(self, position: Vector) -> float:
        #     return self.closest(position)[1]

    def __init__(self, center: Vector, radiusSq: float):
        self.center = center
        self.edge = center + Vector(math.sqrt(radiusSq), 0)
        self.movable = type(self)._Movable(self)
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
            return [(c.x * v + laser.line.a, None)]
        d = math.sqrt(dsq)
        return [((c.x + d) * v + laser.line.a, None), ((c.x - d) * v + laser.line.a, None)]

    def Reflect(self, laser: 'Laser', position: 'Vector', extra_info: None) -> 'Laser':
        return Laser(position, (position - self.center).complexMul(Vector(0, 1)).reflect(laser.line.vector))

    def Draw(self, canvas: 'Canvas', color=(255, 255, 255), width=1):
        canvas.Circle(self.center, self.radius, color, width)

    def Glow(self, canvas: 'Canvas', color=(100, 255, 100), width=1):
        canvas.Circle(self.center, self.radius - width, color, width)
        canvas.Circle(self.center, self.radius + width, color, width)


class ShapeCombination(Shape):
    class _Movable(Movable):
        # TODO: make overridden distanceSq in subshapes work
        #       make combining attributes possible
        #       maybe put the methods that don't override Movable in ShapeCombination
        parent: "ShapeCombination"
        # bonds: dict[MoveAttribute, tuple[Callable[[Vector, list[tuple[Vector, Vector]]], Vector], list[MoveAttribute]]]
        # bonds: list[tuple[list[MoveAttribute], Callable[["ShapeCombination", int, Vector],None]]]
        # "the callable is of the form: func(self,changedIndex)"
        binds: dict[MoveAttribute, set[MoveAttribute]]

        def __init__(self, parent: "ShapeCombination"):
            super().__init__(parent)
            self.binds = {}

        def attributes(self):
            return tuple(MoveAttribute(shape, attribute) for shape in self.parent.shapes for attribute in shape.movable.attributes())

        def Get(self, attr: MoveAttribute) -> Vector:
            return attr.args[0].movable.Get(attr.args[1])
            # return getattr(self.parent, attr.args[0])

        def Set(self, attr: MoveAttribute, value: Vector):
            # TODO: this will not work
            # for attr1 in self.get_bound(attr):
            attr.args[0].movable.Set(attr.args[1], value)

        def update(self, attr: MoveAttribute) -> None:

            pass

        # def Set_bond_oneway(self, attr: MoveAttribute, func: Callable[[Vector, list[tuple[Vector, Vector]]], Vector], connections: list[MoveAttribute]):
        #     """when one of the connections changes, func is called with the attr's position and the list of all connections' old and new positions.
        #     func should return attr's new position
        #     always do it both ways"""
        #     self.bonds[attr] = func, connections
        def Bind(self, attributes: set[MoveAttribute]) -> None:
            # self.binds is a network, where self.binds[x] is the set in which all attributes connected to x are.
            # if a and b are connected, then self.binds[a] and self.binds[b] refer to the same set, which contains both a and b
            bunch = set(attributes)
            for attr in attributes:
                if attr in self.binds:
                    bunch.update(self.binds[attr])
            for attr in bunch:
                self.binds[attr] = bunch

                # b = self.binds.setdefault(attr, {attr})
                # for a in list(b):
                #     self.binds[a].update(attributes)
        def get_bound(self, attr: MoveAttribute):
            return self.binds[attr]

    def __init__(self, *shapes: Shape):
        self.shapes = list(shapes)
        self.movable = type(self)._Movable(self)
        pass

    def Hit(self, laser: 'Laser'):

        return list(chain(*(shape.Hit(laser) for shape in self.shapes)))

    def Reflect(self, laser: 'Laser', position: 'Vector', extra_info: Any = None) -> 'Laser':
        return super().Reflect(laser, position)

    def Draw(self, canvas: 'Canvas', color=(255, 255, 255), *args, **kwargs):
        for shape in self.shapes:
            shape.Draw(canvas, color, *args, **kwargs)

    def Glow(self, canvas: 'Canvas', color=(100, 255, 100), *args, **kwargs):
        for shape in self.shapes:
            shape.Glow(canvas, color, *args, **kwargs)


# TODO: rotation, highlighting an object


class Mover:
    def __init__(self):
        "all attributes are read-only"
        self.position = Vector(0, 0)
        "the position the Mover is at"
        self.movement = Vector(0, 0)
        "the change in self.position from last frame"
        self.picked: Has_Movable = None
        "the Movable that is being moved"
        self.picked_attr: MoveAttribute = None
        "the attribute of self.picked that is being moved"
        self.down = False
        "if on the previous frame the mover was pressed down"
        self.whole = False
        "if the whole Movable is moved"
        pass

    def update(self, position: Vector, down: bool, has_movables: list[Has_Movable], whole=False) -> None:
        self.movement = position - self.position
        self.position = position
        self.whole = whole
        if self.picked and self.picked not in has_movables:
            self.picked, self.picked_attr = None, None
        if down and not self.down:  # down
            self.picked, self.picked_attr = self.findClosest(self.position, has_movables)
            if self.picked is not None:  # and self.picked_attr:  # if above findClosest returned something else than (None,None)
                # move the picked point to the cursor, with the other points if total is True
                self.picked.movable.OnPick(self, self.picked_attr)
                if self.whole:
                    self.picked.movable.MoveWholeTo(self.picked_attr, self.position)
                else:
                    self.picked.movable.MovePartTo(self.picked_attr, self.position)
        elif self.down and not down:  # up
            self.picked, self.picked_attr = None, None
        elif self.picked is not None and self.down:  # do not execute immediately after picking
            if self.whole:
                self.picked.movable.MoveWhole(self.movement)
            else:
                self.picked.movable.Move(self.picked_attr, self.movement)
        self.down = down

    def findClosest(self, position: Vector, has_movables: list[Has_Movable], maxDistanceSq=-1) -> tuple[Has_Movable, MoveAttribute] | tuple[None, None]:
        "returns (None,None) if nothing is found"
        closestP = None
        closestAttr = None
        distanceSq = maxDistanceSq
        for p in has_movables:
            # if not isinstance(p, Movable):
            #     raise TypeError("{} is not Movable".format(p))
            #     continue
            attr, dsq = p.movable.closest(position)
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
                a = hits[0][0].Reflect(self, point, hits[0][1])
            else:
                w = -self.line.vector
                a = Laser(point, w)
            return a, (point - self.line.a).length()
        else:
            return self, 0

    def ClosestHit(self, reflectors: set[Reflectable]):
        "returns a list of tuples containing a Reflectable object which the Laser hits at a point and extra information about that hit, and a point"
        distance = -1
        point = None
        hits = []
        for r in (reflectors):
            for a, extra in r.Hit(self):
                d = self.line.dotProduct(a)
                if d > 0.000000001:
                    if distance >= d or distance == -1:
                        if distance == d:
                            hits.append((r, extra))
                        else:
                            point = a
                            hits = [(r, extra)]
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

            adding = inputs.keyPressed(pygame.K_LCTRL) or inputs.keyPressed(pygame.K_RIGHT)
            if inputs.keyDown(pygame.K_UP) or inputs.mouseDown(1):
                if self.one:
                    a = Line(self.one, mpos)
                    if adding:
                        b = ShapeCombination(self.shapes[-1], a)
                        self.shapes.pop(-1)
                        self.shapes.append(b)
                    else:
                        self.shapes.append(a)
                    self.one = None
                else:
                    self.one = mpos
            if inputs.keyPressed(pygame.K_LEFT) or inputs.mousePressed(6):
                if self.one:
                    a = Sphere(self.one, (self.one - mpos).lengthSq())
                    if adding:
                        b = ShapeCombination(self.shapes[-1], a)
                        self.shapes.pop(-1)
                        self.shapes.append(b)
                    else:
                        self.shapes.append(a)
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
            if self.mover.picked:
                self.mover.picked.Glow(canvas)
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
