# cython: language_level=3
# 
cimport cython
from libc.math cimport sqrt,abs
import numpy as np
cimport numpy as np
np.import_array()

cdef double vector_lengthSq(double x, double y, double z) nogil:
    return (x*x + y*y + z*z)
cdef double vector_length(double x, double y, double z) nogil:
    return sqrt(vector_lengthSq(x,y,z))
@cython.boundscheck(False)
cdef double vector3_length(double[:] vec) nogil:
    return vector_length(vec[0],vec[1],vec[2])


# cdef void Rotate(double[:] in_vector3, double[:] out_vector3,double[:,:] rotation):
#     out_vector3[0] = rotation[0][0]*in_vector3[0]+rotation[0][1]*in_vector3[1]+rotation[0][2]*in_vector3[2]
#     out_vector3[1] = rotation[1][0]*in_vector3[0]+rotation[1][1]*in_vector3[1]+rotation[1][2]*in_vector3[2]
#     out_vector3[2] = rotation[2][0]*in_vector3[0]+rotation[2][1]*in_vector3[1]+rotation[2][2]*in_vector3[2]

@cython.boundscheck(False)
cdef void set_vector(double x, double y, double z, double[:] out_vector3) nogil:
    out_vector3[0] = x
    out_vector3[1] = y
    out_vector3[2] = z

@cython.boundscheck(False)
@cython.cdivision(True)
cdef void set_vector_unit(double x, double y, double z, double[:] out_vector3) nogil:
    "do not input a zero vector"
    cdef double l = 1/vector_length(x,y,z)
    out_vector3[0] = x*l
    out_vector3[1] = y*l
    out_vector3[2] = z*l

@cython.boundscheck(False)
cdef double vector_distance_Sq(double[:] a, double[:] b) nogil:
    return vector_lengthSq(a[0]-b[0],a[1]-b[1],a[2]-b[2])


@cython.boundscheck(False)
@cython.cdivision(True)
cdef void Rotate(double x, double y, double z, double[:] out_vector3,double[:] rotation) nogil:
    cdef double l = 1/vector_length(x,y,z) # is never 0
    out_vector3[0] = (rotation[0]*x+rotation[1]*y+rotation[2]*z)*l
    out_vector3[1] = (rotation[3]*x+rotation[4]*y+rotation[5]*z)*l
    out_vector3[2] = (rotation[6]*x+rotation[7]*y+rotation[8]*z)*l

@cython.boundscheck(False)
cdef void add_multiplied(double[:] addee, double[:] added, double multiplier) nogil:
    addee[0]+= added[0]*multiplier
    addee[1]+= added[1]*multiplier
    addee[2]+= added[2]*multiplier

@cython.boundscheck(False)
cdef double dot_minus(double[:] a,double[:] b,double[:] c) nogil:
    "a*(b-c) where * is dot product"
    return a[0]*(b[0]-c[0])+a[1]*(b[1]-c[1])+a[2]*(b[2]-c[2])

cdef void mirror(double[:] mirrorable, double[:] direction, double[:] origin) nogil:
    "mirrors the mirrorable, updating it. direction has to be unit"
    cdef double a = dot_minus(direction,mirrorable,origin)
    if a>0:
        add_multiplied(mirrorable,direction,-2*a)


cdef class Triangle:
    cdef double[3] mir1_dir_arr,mir2_dir_arr,mir_orig
    cdef public double[:] mirrorer1_direction, mirrorer2_direction
    cdef public double[:] mirrorer_origin
    cdef public int level
    def __init__(self):
        self.mirrorer1_direction = self.mir1_dir_arr
        self.mirrorer2_direction = self.mir2_dir_arr
        self.mirrorer_origin = self.mir_orig
        set_vector(0,0,0,self.mirrorer_origin)
        set_vector_unit(-1,1,0,self.mirrorer1_direction)
        set_vector_unit(-1,1,0,self.mirrorer2_direction)
        self.level = 8
    @cython.boundscheck(False)
    @cython.initializedcheck(False)
    cdef double sdf(self,double[:] position,double[:] pos) nogil:
        # cdef double[3] pos_arr
        # cdef double[:] pos = pos_arr
        pos[0] = position[0]
        pos[1] = position[1]
        pos[2] = position[2]
        cdef double halver = 4
        cdef int i
        for i in range(self.level):
            mirror(pos,self.mirrorer1_direction,self.mirrorer_origin)
            mirror(pos,self.mirrorer2_direction,self.mirrorer_origin)
            halver /=2
            if pos[0]>halver:
                pos[0] = halver*2-pos[0]
        return abs(vector3_length(pos)-halver)
    def set_mirrorer1_direction(self,double x, double y, double z):
        if x!=0 or y!=0 or z!=0:
            set_vector_unit(x,y,z,self.mirrorer1_direction)
    def set_mirrorer2_direction(self,double x, double y, double z):
        if x!=0 or y!=0 or z!=0:
            set_vector_unit(x,y,z,self.mirrorer2_direction)
    cdef double simple_sdf(self,double[:] position, double[:] extra_vector) nogil:
        return abs(vector3_length(position)-1)

cdef class Light:
    cdef double[3] position_arr
    cdef double[:] position
    cdef public double strength
    cdef public int enabled
    def __init__(self):
        self.position = self.position_arr
        set_vector(1,3,-3,self.position)
        self.enabled = 1
        self.strength = 1.
    def set_position(self,double x, double y, double z):
        set_vector(x,y,z,self.position)
    def get_position(self):
        return (self.position[0],self.position[1],self.position[2])
    @cython.boundscheck(False)
    cdef void readjust_direction(self,double[:] direction, double[:] position) nogil:
        set_vector_unit(self.position[0]-position[0],self.position[1]-position[1],self.position[2]-position[2],direction)
    cdef double distance_to(self,double[:] position,double[:] direction) nogil:
        "misleading"
        return dot_minus(direction,position,self.position)


cdef Triangle sdf_object = Triangle()
cdef Light light = Light()

def get_sdf_object():
    return sdf_object
def get_light():
    return light


cdef double SDF(double[:] position,double[:] extra_vector) nogil:
    # return abs(vector3_length(position)-1)
    return sdf_object.sdf(position,extra_vector)

cdef int Iterate(double[:] position, double[:] direction,int max_iterations,double close_enough, double[:] extra_vector) nogil:
    cdef int i
    cdef double distance
    for i in range(max_iterations):
        distance = SDF(position,extra_vector)
        add_multiplied(position,direction,distance)
        if distance<close_enough:
            return i+1
        if distance>10:
            return 0
    else:
        return 0

cdef class Rules:
    cdef public int max_iterations
    cdef public int max_iterations_light 
    cdef public double close_enough 
    cdef public double close_enough_light
    def __init__(self):
        self.max_iterations = 10
        self.max_iterations_light = 20
        self.close_enough = 0.01
        self.close_enough_light = 0.001

cdef Rules rules = Rules()

def get_rules():
    return rules



cdef np.ndarray[ndim=3,dtype=double] Draw2(np.ndarray[ndim=2,dtype=double] rotation, double[:] origin,int width,int height,double zoom):
    cdef np.ndarray[ndim=3,dtype=double] arr = np.ndarray(shape=(width,height,5), dtype=np.double)
    cdef double close_enough = rules.close_enough
    cdef int max_iterations = rules.max_iterations
    cdef double close_enough_light = rules.close_enough_light
    cdef int max_iterations_light = rules.max_iterations_light

    cdef double [:,:,:] arr_view = arr
    cdef double [9] rotation_flat = rotation.flatten()
    cdef double [:] rotation_view = rotation_flat
    cdef double[3] ray_direction_arr
    cdef double[3] ray_position_arr
    cdef double[:] ray_direction = ray_direction_arr
    cdef double[:] ray_position = ray_position_arr
    cdef double[3] extra_vector_arr
    cdef double[:] extra_vector = extra_vector_arr
    cdef double distance_to_light_sq
    cdef int iteration_result
    cdef int sy,sx
    with nogil:
        with cython.boundscheck(False): 
            with cython.cdivision(True):
                for sy in range(height):
                    for sx in range(width):
                        ray_position[:] = origin[:]
                        Rotate(<double>sx/width-0.5,<double>sy/height-0.5,1,ray_direction,rotation_view)
                        iteration_result = Iterate(ray_position,ray_direction,max_iterations,close_enough,extra_vector)
                        arr_view[sx,sy,0] = ray_position[0]
                        arr_view[sx,sy,1] = ray_position[1]
                        arr_view[sx,sy,2] = ray_position[2]
                        arr_view[sx,sy,3] = iteration_result
                        if light.enabled !=0 and iteration_result !=0:
                            light.readjust_direction(ray_direction,ray_position)
                            # distance_to_light_sq = light.distance_to(ray_position,ray_direction)
                            # add_multiplied(ray_position,ray_direction,close_enough)
                            iteration_result = Iterate(ray_position,ray_direction,max_iterations_light,close_enough_light,extra_vector)
                            # arr_view[sx,sy,4] = iteration_result
                            arr_view[sx,sy,4] = (0>light.distance_to(ray_position,ray_direction))
                        else:
                            arr_view[sx,sy,4] = 0


    return arr


def Get_array(rotation not None,double[:] origin,int width,int height,double zoom):
    return Draw2(rotation, origin,width, height, zoom)

