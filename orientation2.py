
import math
import numpy as np


IDENTITY = np.identity(3)


Vector = np.ndarray
Rotation = np.ndarray


def cross_product_matrix(vector: Vector):
    x, y, z = vector
    return np.array([[0, -z, y],
                     [z, 0, x],
                     [-y, -x, 0]])


def rotation_matrix_from_axis_rotation(vector: Vector, co: float, si: float) -> Rotation:
    return co * IDENTITY + si * cross_product_matrix(vector) + (1 - co) * (np.outer(vector, vector))


def rotation_matrix_from_axis_angle(vector: Vector, angle: float) -> Rotation:
    return rotation_matrix_from_axis_rotation(vector, math.cos(angle), math.sin(angle))


rotation_around = rotation_matrix_from_axis_angle


def inverse_rotation(rotation: Rotation) -> Rotation:
    return rotation.transpose()


def Vector3(*args: float) -> Vector:
    return np.array(args, dtype=np.float64)


def rotate(rotation: Rotation, vector: Vector) -> Vector:
    return rotation @ vector


def chain_rotation(rotation1: Rotation, rotation2: Rotation) -> Rotation:
    return rotation1 @ rotation2


class Transform:
    def __init__(self, position: Vector, rotation: Rotation):
        self.position = position
        self.rotation = rotation

    def Localize(self, other: 'Transform'):
        'if self and other are in w space, what is other in self space'
        return Transform(self.LocalizePosition(other.position),
                         self.LocalizeRotation(other.rotation))

    def LocalizePosition(self, other: Vector | tuple) -> Vector:
        other = np.asarray(other)
        # return self.rotation.RotateInverse(other - self.position)
        return inverse_rotation(self.rotation) @ (other - self.position)

    def LocalizeRotation(self, other: Rotation) -> Rotation:

        return inverse_rotation(self.rotation) @ other

    def LocalizeDirection(self, other: Vector | tuple) -> Vector:
        other = np.asarray(other)

        # return self.rotation.RotateInverse(other)
        return inverse_rotation(self.rotation) @ (other)

    def Globalize(self, other: 'Transform') -> 'Transform':
        'if self is in w space and other is in self space, what is other in w space'
        return Transform(self.GlobalizePosition(other.position),
                         self.GlobalizeRotation(other.rotation))

    def GlobalizePosition(self, other: Vector) -> Vector:
        other = np.asarray(other)

        return self.position + self.rotation @ other

    def GlobalizeRotation(self, other: Rotation) -> Rotation:
        return self.rotation @ other

    def GlobalizeDirection(self, other: Vector) -> Vector:
        other = np.asarray(other)

        return self.rotation @ other
