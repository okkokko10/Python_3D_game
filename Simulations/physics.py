
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import screenIO
import quantities as qu
import numpy as np


class Vector(np.ndarray):
    def __new__(cls, *args) -> "Vector":
        return np.array(args, dtype=float)

    @staticmethod
    def zero():
        return Vector(0, 0, 0)


class Rigidbody:
    mass: float
    position: Vector

    def __init__(self, mass: float, position: Vector):
        self.mass = mass
        self.position = position
