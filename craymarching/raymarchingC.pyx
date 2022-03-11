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


cdef double vector_lengthSq(double x, double y, double z):
    return (x*x + y*y + z*z)
cdef double vector_length(double x, double y, double z):
    return sqrt(vector_lengthSq(x,y,z))


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
    cdef double lengthSq(self):
        return vector_lengthSq(self.x,self.y,self.z)
    cdef double distance(self,Vector3 other):
        return vector_length(self.x-other.x,self.y-other.y,self.z-other.z)
    cdef Vector3 copy(self):
        return Vector3(self.x,self.y,self.z)
    cdef Vector3 unit_update(self):
        cdef double le = 1/self.length()
        self.x*=le
        self.y*=le
        self.z*=le
        return self
    cdef Vector3 unit_rotate_update(self,np.ndarray[ndim=2,dtype=double] rotation):
        self.x,self.y,self.z = np.matmul(rotation,(self.x,self.y,self.z))
        self.unit_update()
        return self
    cdef double dot(self,Vector3 other):
        return self.x*other.x+self.y*other.y+self.z*other.z
    cdef Vector3 add(self,Vector3 other):
        return Vector3(self.x+other.x,self.y+other.y,self.z+other.z)
    cdef Vector3 sub(self,Vector3 other):
        return Vector3(self.x-other.x,self.y-other.y,self.z-other.z)
    cdef Vector3 mul(self,double other):
        return Vector3(self.x*other,self.y*other,self.z*other)
    def __str__(self):
        return "({:.3} {:.3} {:.3})".format(self.x,self.y,self.z)

cdef Vector3 Unit_rotated(double x, double y, double z,double[:,:] rotation):
    return Vector3( rotation[0][0]*x+rotation[0][1]*y+rotation[0][2]*z,
                    rotation[1][0]*x+rotation[1][1]*y+rotation[1][2]*z,
                    rotation[2][0]*x+rotation[2][1]*y+rotation[2][2]*z).unit_update()


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

cdef void mirror(Vector3 mirrorable, Vector3 direction, Vector3 origin):
    "mirrors the mirrorable, updating it. direction has to be unit"
    # mirrorable.add_multiplied(direction,(-2*max(0,direction.dot(mirrorable.sub(origin)))))
    # mirrorable.add_multiplied(direction,(-2*max(0,direction.dot(mirrorable))))
    cdef double a = direction.dot(mirrorable)
    if a>0:
        mirrorable.add_multiplied(direction,-2*a)


cdef list spheres = [Sphere(Vector3(0,0,5),2),Sphere(Vector3(0,3,5),1),Sphere(Vector3(3,0,5),1)]

cdef class SdfScene:
    cdef double sdf(self,Vector3 position):
        cdef double min_distance = 100
        cdef double distance
        cdef Sphere s
        for s in spheres:
            distance = s.sdf(position)
            if distance<min_distance:
                min_distance=distance
        return min_distance

cdef class Triangle:
    cdef public Vector3 mirrorer1_direction, mirrorer2_direction
    cdef Vector3 mirrorer_origin
    cdef public int level
    def __init__(self):
        self.mirrorer1_direction= Vector3(-1,1,0).unit_update()
        self.mirrorer2_direction= Vector3(-1,1,0).unit_update()
        self.mirrorer_origin = Vector3(0,0,0)
        self.level = 8
    cdef double sdf(self,Vector3 position):
        cdef Vector3 pos = position.copy()
        cdef int i
        cdef double halver = 4
        for i in range(self.level):
            mirror(pos,self.mirrorer1_direction,self.mirrorer_origin)
            mirror(pos,self.mirrorer2_direction,self.mirrorer_origin)
            halver /=2
            if pos.x>halver:
                pos.x = halver*2-pos.x
        return abs(pos.length()-halver)
    def set_mirrorer1_direction(self,double x, double y, double z):
        self.mirrorer1_direction = Vector3(x,y,z).unit_update()
    def set_mirrorer2_direction(self,double x, double y, double z):
        self.mirrorer2_direction = Vector3(x,y,z).unit_update()

# cdef SdfScene scene = SdfScene()
# cdef Sphere scene = Sphere(Vector3(0.,0.,0.),1.)
cdef Triangle scene = Triangle()

def get_scene():
    return scene


cdef class Ray:
    cdef Vector3 position,direction
    def __cinit__(self,Vector3 position,Vector3 direction):
        self.position = position
        self.direction = direction
    cdef int iterate(self,int max_iterations,double close_enough):
        cdef int i
        cdef double min_distance
        for i in range(max_iterations):
            min_distance = scene.sdf(self.position)
            self.position.add_multiplied(self.direction,min_distance)
            if min_distance<close_enough:
                return 1
            if min_distance>10:
                return 0
        else:
            return 0
        


cdef Vector3 ray_direction(double x,double y,double[:,:] rotation):
    return Unit_rotated(x-0.5,y-0.5,1,rotation)



def rays(np.ndarray rotation, int width, int height, double zoom):
    def func(np.ndarray x, np.ndarray y):
        return rotation @ np.array((x / zoom - 0.5 * width / zoom, y / zoom - 0.5 * height / zoom, 1), dtype=object)
    cdef np.ndarray[ndim=2,dtype=double] x,y,z,l
    x, y, z = np.fromfunction(func, (width, height))
    # l = np.sqrt(x**2 + y**2 + z**2)
    l = np.linalg.norm((x,y,z),axis=0)
    x /= l
    y /= l
    z /= l
    return x, y, z

cdef np.ndarray[ndim=3,dtype=double] Draw2(np.ndarray[ndim=2,dtype=double] rotation, Vector3 origin,int width,int height,double zoom, int max_iterations,double close_enough):
    cdef np.ndarray[ndim=3,dtype=double] arr = np.ndarray(shape=(width,height,4), dtype=np.double)
    # cdef np.ndarray[ndim=2,dtype=double] xl,yl,zl
    # xl,yl,zl = rays(rotation,width,height,zoom)
    cdef double [:,:,:] arr_view = arr
    cdef double [:,:] rotation_view = rotation
    cdef Ray ray1
    cdef int sy,sx
    for sy in range(height):
        for sx in range(width):
            # ray1=Ray(origin.copy(),Vector3(xl[sx,sy],yl[sx,sy],zl[sx,sy]))
            ray1=Ray(origin.copy(),ray_direction(sx/width,sy/height,rotation_view))
            arr_view[sx,sy,3] = ray1.iterate(max_iterations,close_enough)
            arr_view[sx,sy,0:3] = ray1.position.x,ray1.position.y,ray1.position.z

    return arr


def Get_array(rotation not None,double[:] origin,int width,int height,double zoom, int max_iterations, double close_enough):
    return Draw2(rotation, Vector3(origin[0],origin[1],origin[2]),width, height, zoom, max_iterations, close_enough)

# print(sdf(1, 2, 3))
# print(rays(np.identity(3), 100, 100, 100))
