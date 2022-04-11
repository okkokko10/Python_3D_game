import itertools
import math
import os
import sys
from typing import Iterable, Type, TypeVar, overload

import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import screenIO
import quantities as qu

# TODO: ability to see how much a body resists a momentum vector at a location


class Vector(np.ndarray):
    def __new__(cls, *args) -> "Vector":
        return np.array(args, dtype=float)

    @staticmethod
    def zero():
        return Vector(0, 0, 0)


_Q = TypeVar("_Q", bound=qu.Quantity)
_Q1 = TypeVar("_Q1", bound=qu.Quantity)


@overload
def qu_vector_length(vector: _Q) -> _Q: ...


def qu_vector_length(vector: qu.Quantity[Vector]) -> qu.Quantity[float]:
    return qu.cast(np.linalg.norm(qu.get_value(vector)), vector)
    # return vector.cast(np.linalg.norm(vector.value))


def qu_vector_dot(a: qu.Quantity[Vector], b: qu.Quantity[Vector]):
    "output has dimensions of a*b"
    c: float = np.dot(qu.get_value(a), qu.get_value(b))
    return qu.cast(c, a * b)
    # return (a * b).cast(c)


@overload
def qu_vector_project(a: _Q, b: qu.Quantity[Vector]) -> _Q: ...


def qu_vector_project(a: qu.Quantity[Vector], b: qu.Quantity[Vector]) -> qu.Quantity[Vector]:
    "projects a onto b. the qd (quantity dimensions) of b do not matter. has the same qd as a"
    l = qu_vector_length(b)**2
    if l:
        return b * (qu_vector_dot(a, b) / l)  # dimensions a
    else:
        return a * 0


@overload
def qu_cross_product(a: _Q, b: _Q1):
    return a * b


def qu_cross_product(a: qu.Quantity[Vector], b: qu.Quantity[Vector]) -> qu.Quantity[Vector]:
    qu.cast(np.cross(qu.get_value(a), qu.get_value(b)), a * b)


def vector_length(vector: Vector):
    return np.linalg.norm(vector)


def vector_length_Sq(vector: Vector):
    return sum(a**2 for a in vector)


def vector_from_angle(angle: float):
    angle = math.radians(angle)
    return Vector(math.cos(angle), math.sin(angle))


def vector_dot(a: Vector, b: Vector) -> float:
    return np.dot(a, b)


def vector_project(a: Vector, b: Vector):
    "projects a onto b"
    l = vector_length_Sq(b)
    if l:
        return b * (vector_dot(a, b) / l)
    else:
        return b * 0


class Inertia_Object:
    position: qu.Length[Vector]
    mass: qu.Mass[float]
    velocity: qu.Speed[Vector]

    def __init__(self, position: qu.Length[Vector], mass: qu.Mass[float], velocity: qu.Speed[Vector]) -> None:
        if qu.CHECK:
            assert all(isinstance(a, qu.Quantity) for a in (position, mass, velocity))
        self.position = position
        self.mass = mass
        self.velocity = velocity
        # self.momentum = momentum

    def add_momentum(self, momentum: qu.Momentum[Vector]) -> None: self.velocity += momentum / self.mass

    @property
    def momentum(self) -> qu.Momentum[Vector]:
        "mass * velocity"
        return self.mass * self.velocity

    @momentum.setter
    def momentum(self, value: qu.Momentum[Vector]):
        self.velocity = value / self.mass

    def update(self, deltaTime: qu.Time[float]) -> None:
        self.position += self.velocity * deltaTime

    def draw(self, canvas: screenIO.Canvas) -> None: ...


class Connection:
    def update(self, deltaTime: qu.Time[float]) -> None: ...
    def draw(self, canvas: screenIO.Canvas) -> None: ...


class World:
    objects: set[Inertia_Object]
    connections: set[Connection]

    def __init__(self) -> None:
        self.objects = set()
        self.connections = set()

    def update(self, deltaTime: float) -> None:
        for con in self.connections:
            con.update(deltaTime)
        for obj in self.objects:
            obj.update(deltaTime)

    def draw(self, canvas: screenIO.Canvas) -> None:
        for con in self.connections:
            con.draw(canvas)
        for obj in self.objects:
            obj.draw(canvas)
        pass


class Particle(Inertia_Object):
    def draw(self, canvas: screenIO.Canvas) -> None:
        canvas.Circle(qu.get_value(self.position), qu.get_value(self.mass)**0.5, (255, 255, 255))
    pass


class Spring(Connection):
    k: qu.times[qu.Force, qu.inverse[qu.Length]]

    def __init__(self, particle_a: Inertia_Object, particle_b: Inertia_Object, equilibrium_length: qu.Length[float], spring_constant: qu.times[qu.Force, qu.inverse[qu.Length]]):
        self.pA = particle_a
        self.pB = particle_b
        self.length = equilibrium_length
        self.k = spring_constant

    def update(self, deltaTime: qu.Time[float]):
        pos_dif = self.pA.position - self.pB.position
        l: qu.Length[float] = qu_vector_length(pos_dif)
        momentum: qu.Momentum[Vector] = (self.length - l) * self.k / l * pos_dif * deltaTime

        self.pA.add_momentum(momentum)
        self.pB.add_momentum(-momentum)

    def draw(self, canvas: screenIO.Canvas) -> None:
        canvas.Line(qu.get_value(self.pA.position), qu.get_value(self.pB.position), 1, (255, 255, 255))


class Rigid_Stick(Connection):
    def __init__(self, particle_a: Inertia_Object, particle_b: Inertia_Object, equilibrium_length: qu.Length[float]):
        self.pA = particle_a
        self.pB = particle_b
        self.length = equilibrium_length

    def update(self, deltaTime: qu.Time[float]):
        pos_dif = self.pA.position - self.pB.position
        velocity_dif = self.pA.velocity - self.pB.velocity
        l: qu.Length[float] = qu_vector_length(pos_dif)
        pos_change: qu.Length[Vector] = (self.length - l) / l * pos_dif
        velocity_change = qu_vector_project(velocity_dif, pos_dif)
        # because the difference in momentum in the direction of the difference in position should be 0,
        # the change in position in that direction doesn't need to be changed from potential to kinetic energy
        # perfectly inelastic collision (v is the resulting shared velocity): m1 * v1 + m2 * v2 = (m1 + m2) * v
        # v = (self.pA.mass * velocity_change + self.pB.mass * velocity_change * 0) / (self.pA.mass + self.pB.mass)
        self.pA.position += pos_change * (self.pB.mass / (self.pA.mass + self.pB.mass))
        self.pB.position += -pos_change * (self.pA.mass / (self.pA.mass + self.pB.mass))
        self.pA.velocity += -velocity_change * (self.pB.mass / (self.pA.mass + self.pB.mass))  # is this right?
        self.pB.velocity += velocity_change * (self.pA.mass / (self.pA.mass + self.pB.mass))
        # self.pA.velocity * self.pA.mass + self.pB.velocity * self.pB.mass == \
        #     self.pA.velocity * self.pA.mass + self.pB.velocity * self.pB.mass \
        #     - velocity_change * (self.pB.mass / (self.pA.mass + self.pB.mass)) * self.pA.mass \
        #     + velocity_change * (self.pA.mass / (self.pA.mass + self.pB.mass)) * self.pB.mass

    def draw(self, canvas: screenIO.Canvas) -> None:
        canvas.Line(qu.get_value(self.pA.position), qu.get_value(self.pB.position), 1, (255, 255, 0))


class RigidBody_Connection(Connection):
    def __init__(self, particles: list[tuple[Inertia_Object, Vector]]):
        self.particles = particles
        "a collection of tuples of inertia objects and their equilibrium positions"
        assert self.particles
        self.reupdate()

    def reupdate(self):
        self.total_mass = sum(obj.mass for obj, pos in self.particles)
        self.equilibrium_center_of_mass = sum(obj.mass * pos for obj, pos in self.particles) / self.total_mass
        for obj, pos in self.particles:
            pos[...] -= self.equilibrium_center_of_mass

    def update(self, deltaTime: float) -> None:
        center_of_mass = sum(obj.mass * obj.position for obj, pos in self.particles) / self.total_mass
        total_momentum = sum(obj.momentum for obj, pos in self.particles)
        velocity = total_momentum / self.total_mass

        for obj, pos in self.particles:
            p = (obj.position - center_of_mass)
            v = obj.velocity - velocity
            a = vector_project(v, p)
            b = v - a
            vector_length(p) * vector_length(b)
        pass


class Torque:
    def __init__(self, center_of_mass: Vector, mass: float) -> None:
        self.center_of_mass = center_of_mass
        self.mass = mass
    pass


class Body:
    mass: qu.Mass[float]
    momentum: qu.Momentum[Vector]
    mass_position: qu.times[qu.Mass[float], qu.Length[Vector]]
    "mass times the center of mass"

    @property
    def center_of_mass(self) -> qu.Length[Vector]:
        return self.mass_position / self.mass

    @property
    def velocity(self) -> qu.Speed[Vector]:
        return self.momentum / self.mass

    def angular_momentum_to(self, origin: qu.Length[Vector], origin_velocity: qu.Speed[Vector]) -> qu.times[qu.Length[Vector], qu.Momentum[Vector]]:
        m = self.mass
        return qu_cross_product(self.mass_position / m - origin, self.momentum - origin_velocity * m)
        # return qu_cross_product(self.center_of_mass - origin, self.momentum - origin_velocity * self.mass)


class BodySystem(Body):
    parts: Iterable[Body]

    @property
    def mass(self) -> qu.Mass[float]:
        return sum((p.mass for p in self.parts)) if self.parts else qu.Mass(0.)

    @property
    def momentum(self) -> qu.Momentum[Vector]:
        return sum((p.momentum for p in self.parts)) if self.parts else qu.Momentum(Vector.zero())

    @property
    def mass_position(self) -> qu.times[qu.Mass[float], qu.Length[Vector]]:
        return sum((p.mass_position for p in self.parts)) if self.parts else qu.Mass(0.) * qu.Length(Vector.zero())

    def angular_momentum_spin(self) -> qu.times[qu.Length[Vector], qu.Momentum[Vector]]:
        if self.parts:
            mass = self.mass
            center = self.mass_position / mass
            velocity = self.momentum / mass
            return sum((p.angular_momentum_to(center, velocity) for p in self.parts))
        else:
            return qu.Length(0.) * qu.Momentum(Vector())
        return sum((qu_cross_product(p.center_of_mass - self.center_of_mass, p.mass * (p.velocity - self.velocity)) for p in self.parts)) if self.parts else qu.Length(0.) * qu.Momentum(Vector())
    ...


class Collision:
    def __init__(self, a: Body, b: Body, hit_position: qu.Length[Vector], a_hit_velocity):
        pass


class Scene_demo_wheel(screenIO.Scene):
    def o_Init(self, updater: 'screenIO.Updater'):
        self.world = World()
        center = qu.Length(Vector(400, 400))
        a = None
        b = None
        c = None
        self.center = Particle(center, qu.Mass(1), qu.Speed(Vector(0, 0)))
        self.world.objects.add(self.center)
        particles: list[Particle] = []
        amount = 120
        distance: qu.Length[float] = qu.Length(200)

        def connect(a: Inertia_Object, b: Inertia_Object):
            self.world.connections.add(Rigid_Stick(a, b, qu_vector_length(a.position - b.position)))

        for i in range(amount):
            a = Particle(center + distance * vector_from_angle(i * 360 / amount), qu.Mass(1), qu.Speed(Vector(0, 0)))
            particles.append(a)
            self.world.objects.add(a)
        for i in range(amount):
            # connect(particles[i], self.center)
            for j in itertools.chain(range(1, 4), (20, 30, 40)):
                connect(particles[i], particles[i - j])
            particles[i].add_momentum(qu.Momentum(Vector(10, 0)))
        # particles[0].mass = 1
        # self.offcenter = Particle(center + Vector(distance * 2, 0), 1, Vector(0, 0))
        # a, b = particles[0], self.offcenter
        # connect(a, b)

        # connect(self.center, self.offcenter)
        a = Particle(qu.Length(Vector(800, 400)), qu.Mass(20), qu.Speed(Vector(0, 0)))
        b = Particle(qu.Length(Vector(801, 450)), qu.Mass(1), qu.Speed(Vector(0, 0)))
        self.world.objects.update((a, b))
        connect(a, b)

    def o_Update(self, updater: 'screenIO.Updater'):
        deltaTime = qu.Time(0.1)
        ground_spring_constant = - qu.Force(5) / qu.Length(1)
        for obj in self.world.objects:
            obj.add_momentum(deltaTime * obj.mass * qu.Acceleration(Vector(0, 1)))
            if qu.get_value(obj.position)[1] > 600:
                surface_position = qu.Length(Vector(qu.get_value(obj.position - obj.velocity * qu.Time(1))[0], 600))
                # obj.add_force(Vector(-deltaTime * obj.momentum[0], 0 * deltaTime * obj.mass))
                # qu.get_value(obj.velocity)[0] = 0
                obj.add_momentum((obj.position - surface_position) * ground_spring_constant * deltaTime)
                # qu.get_value(obj.velocity)[1] = -abs(qu.get_value(obj.velocity)[1])
                # obj.add_momentum(deltaTime * obj.mass * qu.Acceleration(Vector(0, -20)))
                # qu.get_value(obj.position)[1] = 2 * 600 - qu.get_value(obj.position)[1]
        self.world.update(deltaTime)

        updater.canvas.Fill((0, 0, 0))
        self.world.draw(updater.canvas)
        updater.canvas.Line((0, 600), (updater.canvas.width, 600), 1, (0, 0, 255))


qu.disable_CHECK()

screenIO.Updater(Scene_demo_wheel()).Play()
