# cython: language_level=3

# import cython
# import numpy as np
from libc.math cimport sqrt,abs
import numpy as np
cimport numpy as np
np.import_array()

# def rays(double[:,:] rotation, int width, int height, double zoom): # -> tuple[np.ndarray, np.ndarray, np.ndarray]:
#     def func(np.ndarray x1, np.ndarray y1):
#         return np.matmul(rotation, (x1 / zoom - 0.5 * width / zoom, y1 / zoom - 0.5 * height / zoom, 1))
#         # return rotation @ np.array((x1 / zoom - 0.5 * width / zoom, y1 / zoom - 0.5 * height / zoom, 1), dtype=object)
#     cdef np.ndarray[ndim=1,dtype=double] x, y, z
#     x, y, z = np.fromfunction(func, (width, height))
#     cdef np.ndarray[ndim=1,dtype=double] l = np.sqrt(x**2 + y**2 + z**2)
#     x /= l
#     y /= l
#     z /= l
#     return x, y, z


cdef double vector_length(double x, double y, double z):
    return sqrt(x*x + y*y + z*z)

cdef class Vector3:
    cdef double x,y,z
    def __cinit__(self, double x,double y, double z):
        self.x=x
        self.y=y
        self.z=z
    cdef void add_multiplied(self,Vector3 other, double multiplier):
        self.x+= other.x*multiplier
        self.y+= other.y*multiplier
        self.z+= other.z*multiplier
    cdef double length(self):
        return vector_length(self.x,self.y,self.z)
    cdef double distance(self,Vector3 other):
        return vector_length(self.x-other.x,self.y-other.y,self.z-other.z)
    cdef Vector3 copy(self):
        return Vector3(self.x,self.y,self.z)
    cdef Vector3 unit_update(self):
        le = 1/self.length()
        self.x*=le
        self.y*=le
        self.z*=le
        return self

cdef class Rayable:
    pass


cdef class Sphere:
    cdef double radius
    cdef Vector3 position
    def __cinit__(self,Vector3 position,double radius):
        self.position = position
        self.radius=radius
    cdef double sdf(self,Vector3 point):
        return abs(self.position.distance(point)-self.radius)



cdef list spheres = [Sphere(Vector3(0,0,5),2),Sphere(Vector3(0,3,5),1),Sphere(Vector3(3,0,5),1)]

cdef class SdfScene:
    cdef double closest_distance(self,Vector3 position):
        cdef double min_distance = 100
        cdef double distance
        cdef Sphere s
        for s in spheres:
            distance = s.sdf(position)
            if distance<min_distance:
                min_distance=distance
        return min_distance

cdef SdfScene scene = SdfScene()


cdef class Ray:
    cdef Vector3 position,direction
    def __cinit__(self,Vector3 position,Vector3 direction):
        self.position = position
        self.direction = direction
    cdef bint iterate(self):
        cdef double min_distance
        for i in range(10):
            min_distance = scene.closest_distance(self.position)
            self.position.add_multiplied(self.direction,min_distance)
            if min_distance<0.1:
                return True
        else:
            return False
        

cdef int shape_x,shape_y
shape_x = 512
shape_y = 512

cdef Vector3 ray_direction(int sx,int sy,np.ndarray[ndim=2,dtype=double] rotation):
    return Vector3(sx/shape_x-0.5,sy/shape_y-0.5,1).unit_update()

cdef np.ndarray[ndim=2,dtype=int] Draw(np.ndarray[ndim=2,dtype=double] rotation, Vector3 origin):
    cdef np.ndarray arr = np.ndarray(shape=(shape_x,shape_y), dtype=int)
    cdef Ray ray1
    for sy in range(shape_y):
        for sx in range(shape_x):
            ray1=Ray(origin.copy(),ray_direction(sx,sy,rotation))
            arr[sx,sy] = ray1.iterate()
    
    return arr

def Get_array(rotation not None,double x,double y,double z):
    return Draw(rotation, Vector3(x,y,z))

# print(sdf(1, 2, 3))
# print(rays(np.identity(3), 100, 100, 100))
