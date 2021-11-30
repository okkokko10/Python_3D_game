
import math
'''ii = jj = kk = ijk = -1


    i*j = -j*i = k
    -i*k = k*i = j
    j*k = -k*j = i


    ij = k
    ik = -j
    ji = -k
    jk = i
    ki = j
    kj = -i
    '''


class Quaternion:  # (namedtuple('Quaternion', 'r i j k')):
    r: float
    i: float
    j: float
    k: float

    def __init__(self, r=0, i=0, j=0, k=0):
        self.r = r
        self.i = i
        self.j = j
        self.k = k

    def __mul__(a, b):
        if isinstance(b, Quaternion):
            r = a.r * b.r - a.i * b.i - a.j * b.j - a.k * b.k
            i = a.j * b.k - a.k * b.j + a.r * b.i + a.i * b.r
            j = a.k * b.i - a.i * b.k + a.r * b.j + a.j * b.r
            k = a.i * b.j - a.j * b.i + a.r * b.k + a.k * b.r
            if isinstance(a, Vector3) or isinstance(b, Vector3):
                return Vector3.new(r, i, j, k)
            return Quaternion(r, i, j, k)
        return a.new(a.r * b, a.i * b, a.j * b, a.k * b)

    def __rmul__(a, b):
        return a.new(b * a.r, b * a.i, b * a.j, b * a.k)

    def __truediv__(a, b):
        return a.new(a.r / b, a.i / b, a.j / b, a.k / b)

    def __add__(a, b):
        return a.new(a.r + b.r, a.i + b.i, a.j + b.j, a.k + b.k)

    def __sub__(a, b):
        return a.new(a.r - b.r, a.i - b.i, a.j - b.j, a.k - b.k)

    @classmethod
    def new(cls, r, i, j, k):
        self = cls.__new__(cls)
        Quaternion.__init__(self, r, i, j, k)
        return self

    def normSq(self): return self.r**2 + self.i**2 + self.j**2 + self.k**2
    def norm(self): return math.sqrt(self.normSq())
    def conjugate(self): return Quaternion(self.r, -self.i, -self.j, -self.k)
    def versor(self): return self / self.norm()
    def reciprocal(self) -> 'Quaternion': return self.conjugate() / self.normSq()

    def GetVector(self): return Vector3(self.i, self.j, self.k)

    def Rotate(self, vector: 'Vector3') -> 'Vector3':
        'rotates the given vector\n\n(p*q).Rotate(v) == p.Rotate(q.Rotate(v))\n\nalso called conjugation'
        return self * vector * self.reciprocal()

    def RotateInverse(self, vector: 'Vector3') -> 'Vector3':
        'rotates the given vector in the opposite direction\n\np.RotateInverse(p.Rotate(v)) == v'
        return self.reciprocal() * vector * self

    def __str__(self): return '{}({} {} {} {})'.format(self.__class__.__name__, self.r, self.i, self.j, self.k)


class Vector3(Quaternion):
    # def __new__(cls,x, y, z): return Quaternion.__new__(cls,0, x, y, z)

    def __init__(self, i=0, j=0, k=0):
        super().__init__(0, i, j, k)
        # self.r = 0
        # self.i = i
        # self.j = j
        # self.k = k

    def RotationAround(self: 'Vector3', angle):
        "rotation around the vector by the given angle"
        return self.RotationComplexHalf(math.cos(angle / 2), math.sin(angle / 2))
        # s = math.sin(angle/2)
        # return Quaternion(math.cos(angle/2), self.i*s, self.j*s, self.k*s)

    def RotationComplexHalf(self: 'Vector3', x, y):
        "rotation around the vector by double the argument of complex(x,y)"
        return Quaternion(x, self.i * y, self.j * y, self.k * y)

    def RotatedAroundAxis(self: 'Vector3', axis: 'Vector3', angle) -> 'Vector3':
        rotator = axis.RotationAround(angle)
        return rotator.Rotate(self)


class Transform:
    def __init__(self, position: 'Vector3', rotation: 'Quaternion'):
        self.position = position
        self.rotation = rotation

    def Localize(self, other: 'Transform'):
        'if self and other are in w space, what is other in self space'
        return Transform(self.LocalizePosition(other.position),
                         self.LocalizeRotation(other.rotation))

    def LocalizePosition(self, other):
        return self.rotation.RotateInverse(other - self.position)

    def LocalizeRotation(self, other: 'Quaternion'):
        return self.rotation.reciprocal() * other

    def LocalizeDirection(self, other: 'Vector3'):
        return self.rotation.RotateInverse(other)

    def Globalize(self, other: 'Transform or Vector3 or Quaternion'):
        'if self is in w space and other is in self space, what is other in w space'
        return Transform(self.GlobalizePosition(other.position),
                         self.GlobalizeRotation(other.rotation))

    def GlobalizePosition(self, other: 'Vector3'):
        return self.position + self.rotation.Rotate(other)

    def GlobalizeRotation(self, other: 'Quaternion'):
        return self.rotation * other

    def GlobalizeDirection(self, other: 'Vector3'):
        return self.rotation.Rotate(other)


if __name__ == '__main__':
    A = Quaternion(1, 2, 3, 4)
    print(A)
    B = Quaternion(1, 2, 3, 4)
    print('B', B)

    C = A * B
    print(C)
    D = A.reciprocal() * C
    print(D)
