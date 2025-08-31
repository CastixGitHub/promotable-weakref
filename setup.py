from setuptools import setup, Extension

module = Extension('promotable_weakref', sources=['promotable_weakref.c'], extra_compile_args=['-ggdb3', '-DDEBUG', '-Wstrict-overflow'])
setup(ext_modules=[module])
