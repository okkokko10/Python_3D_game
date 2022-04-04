import itertools
import math
import os
import sys

import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import screenIO


class Vector(np.ndarray):
    def __new__(cls, *args):
        return np.array(args, dtype=float)


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
    def __init__(self, position: Vector, mass: float, momentum: Vector) -> None:
        self.position = position
        self.mass = mass
        self.momentum = momentum
        "mass * velocity"

    def add_force(self, force: Vector) -> None: self.momentum += force
    def get_mass(self) -> float: return self.mass
    def get_momentum(self) -> Vector: return self.momentum
    def get_velocity(self) -> Vector: return self.momentum / self.mass
    def get_position(self) -> Vector: return self.position

    @property
    def velocity(self) -> Vector:
        return self.momentum / self.mass

    @velocity.setter
    def velocity(self, value: Vector):
        self.momentum = self.mass * value

    def update(self, deltaTime: float) -> None:
        self.position += self.get_velocity() * deltaTime

    def draw(self, canvas: screenIO.Canvas) -> None: ...


class Connection:
    def update(self, deltaTime: float) -> None: ...
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
        canvas.Circle(self.position, self.mass**0.5, (255, 255, 255))
    pass


class Spring(Connection):
    def __init__(self, particle_a: Inertia_Object, particle_b: Inertia_Object, equilibrium_length: float, spring_constant: float):
        self.pA = particle_a
        self.pB = particle_b
        self.length = equilibrium_length
        self.k = spring_constant

    def update(self, deltaTime: float):
        pos_dif = self.pA.position - self.pB.position
        l = vector_length(pos_dif)
        force = (self.length - l) * self.k * deltaTime / l * pos_dif
        self.pA.add_force(force)
        self.pB.add_force(-force)

    def draw(self, canvas: screenIO.Canvas) -> None:
        canvas.Line(self.pA.position, self.pB.position, 1, (255, 255, 255))


class Rigid_Stick(Connection):
    def __init__(self, particle_a: Inertia_Object, particle_b: Inertia_Object, equilibrium_length: float):
        self.pA = particle_a
        self.pB = particle_b
        self.length = equilibrium_length

    def update(self, deltaTime: float):
        pos_dif = self.pA.position - self.pB.position
        velocity_dif = self.pA.velocity - self.pB.velocity  # this could be incorrect
        l = vector_length(pos_dif)
        pos_change = (self.length - l) / l * pos_dif
        momentum_change = vector_project(velocity_dif, pos_dif)
        # because the difference in momentum in the direction of the difference in position should be 0,
        # the change in position in that direction doesn't need to be changed from potential to kinetic energy
        self.pA.position += pos_change * (self.pB.mass / (self.pA.mass + self.pB.mass))
        self.pB.position += -pos_change * (self.pA.mass / (self.pA.mass + self.pB.mass))
        self.pA.momentum += -momentum_change / 2
        self.pB.momentum += momentum_change / 2

    def draw(self, canvas: screenIO.Canvas) -> None:
        canvas.Line(self.pA.position, self.pB.position, 1, (255, 255, 0))


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
    mass: float
    center_of_mass: Vector


class Scene_demo_wheel(screenIO.Scene):
    def o_Init(self, updater: 'screenIO.Updater'):
        self.world = World()
        center = Vector(400, 400)
        a = None
        b = None
        c = None
        self.center = Particle(center, 1, Vector(0, 0))
        self.world.objects.add(self.center)
        particles: list[Particle] = []
        amount = 120
        distance = 200

        def connect(a, b):
            self.world.connections.add(Rigid_Stick(a, b, vector_length(a.position - b.position)))

        for i in range(amount):
            a = Particle(center + vector_from_angle(i * 360 / amount) * distance, 1, Vector(0, 0))
            particles.append(a)
            self.world.objects.add(a)
        for i in range(amount):
            # connect(particles[i], self.center)
            for j in itertools.chain(range(1, 4), (20, 30, 40)):
                connect(particles[i], particles[i - j])
            particles[i].add_force(Vector(10, 0))
        particles[0].mass = 1
        # self.offcenter = Particle(center + Vector(distance * 2, 0), 1, Vector(0, 0))
        # a, b = particles[0], self.offcenter
        # connect(a, b)

        # connect(self.center, self.offcenter)
        a = Particle(Vector(800, 400), 20, Vector(0, 0))
        b = Particle(Vector(800, 450), 1, Vector(0, 0))
        self.world.objects.update((a, b))
        connect(a, b)

    def o_Update(self, updater: 'screenIO.Updater'):
        deltaTime = 0.1
        for obj in self.world.objects:
            obj.add_force(Vector(0, deltaTime * obj.mass))
            if obj.position[1] > 600:
                # obj.add_force(Vector(-deltaTime * obj.momentum[0], 0 * deltaTime * obj.mass))
                obj.momentum[0] = 0
                obj.momentum[1] = -abs(obj.momentum[1])
                obj.position[1] = 2 * 600 - obj.position[1]
        self.world.update(deltaTime)

        updater.canvas.Fill((0, 0, 0))
        self.world.draw(updater.canvas)
        updater.canvas.Line((0, 600), (updater.canvas.width, 600), 1, (0, 0, 255))


screenIO.Updater(Scene_demo_wheel()).Play()
