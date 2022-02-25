
from functools import reduce
import math
import numpy as np


IDENTITY = np.identity(3)


Rotation = np.ndarray


class Vector3(np.ndarray):
    def __new__(cls, *args) -> np.ndarray:
        return np.array(args, dtype=float)
    pass


def cross_product_matrix(vector: Vector3):
    x, y, z = vector
    return np.array([[0, -z, y],
                     [z, 0, x],
                     [-y, -x, 0]])


def rotation_from_axis_and_complex(vector: Vector3, co: float, si: float) -> Rotation:
    "a rotation of axis vector and angle of (co,si) relative to (1,0). (idk if non-unit vector (co,si) are valid)"
    return co * IDENTITY + si * cross_product_matrix(vector) + (1 - co) * (np.outer(vector, vector))


def rotation_from_axis_angle(vector: Vector3, angle: float) -> Rotation:
    return rotation_from_axis_and_complex(vector, math.cos(angle), math.sin(angle))


rotation_around = rotation_from_axis_angle


def inverse_rotation(rotation: Rotation) -> Rotation:
    return rotation.transpose()


def rotate(rotation: Rotation, vector: Vector3) -> Vector3:
    return rotation @ vector


def chain_rotation(rotation1: Rotation, rotation2: Rotation) -> Rotation:
    return rotation1 @ rotation2


def chain_rotations(*rotations: Rotation) -> Rotation:
    return reduce(np.matmul, rotations or [IDENTITY])


def xy_to_x0y(vector: tuple[float, float]) -> Vector3:
    "returns a 3d vector on the xz-plane"
    return np.array((vector[0], 0, vector[1]))


def x_rotation_complex(co: float, si: float) -> Rotation:
    return np.array([[1, 0, 0],
                     [0, co, -si],
                     [0, si, co]])


def y_rotation_complex(co: float, si: float) -> Rotation:
    return np.array([[co, 0, si],
                     [0, 1, 0],
                     [-si, 0, co]])


def z_rotation_complex(co: float, si: float) -> Rotation:
    return np.array([[co, -si, 0],
                     [si, co, 0],
                     [0, 0, 1]])


def elemental_rotation_x(angle: float) -> Rotation:
    return x_rotation_complex(math.cos(angle), math.sin(angle))


def elemental_rotation_y(angle: float) -> Rotation:
    return y_rotation_complex(math.cos(angle), math.sin(angle))


def elemental_rotation_z(angle: float) -> Rotation:
    return z_rotation_complex(math.cos(angle), math.sin(angle))


class Transform:
    def __init__(self, position: Vector3, rotation: Rotation):
        self.position = position
        self.rotation = rotation

    def Localize(self, other: 'Transform'):
        'if self and other are in w space, what is other in self space'
        return Transform(self.LocalizePosition(other.position),
                         self.LocalizeRotation(other.rotation))

    def LocalizePosition(self, other: Vector3 | tuple) -> Vector3:
        other = np.asarray(other)
        # return self.rotation.RotateInverse(other - self.position)
        return inverse_rotation(self.rotation) @ (other - self.position)

    def LocalizeRotation(self, other: Rotation) -> Rotation:

        return inverse_rotation(self.rotation) @ other

    def LocalizeDirection(self, other: Vector3 | tuple) -> Vector3:
        other = np.asarray(other)

        # return self.rotation.RotateInverse(other)
        return inverse_rotation(self.rotation) @ (other)

    def Globalize(self, other: 'Transform') -> 'Transform':
        'if self is in w space and other is in self space, what is other in w space'
        return Transform(self.GlobalizePosition(other.position),
                         self.GlobalizeRotation(other.rotation))

    def GlobalizePosition(self, other: Vector3) -> Vector3:
        other = np.asarray(other)

        return self.position + self.rotation @ other

    def list_GlobalizePosition(self, others: list[Vector3]):
        "I don't know if this works"
        others = np.asarray(others)
        return self.position + self.rotation @ others

    def GlobalizeRotation(self, other: Rotation) -> Rotation:
        return self.rotation @ other

    def GlobalizeDirection(self, other: Vector3) -> Vector3:
        other = np.asarray(other)

        return self.rotation @ other
