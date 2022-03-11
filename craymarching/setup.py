from setuptools import setup
from Cython.Build import cythonize
import numpy
setup(
    name='Hello world app',
    ext_modules=cythonize("raymarchingC2.pyx", annotate=True),
    zip_safe=False,
    include_dirs=[numpy.get_include()]
)
# python setup.py build_ext --inplace
