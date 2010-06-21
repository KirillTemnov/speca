# -*- coding: utf-8 -*-   
"""
generators for various languages
"""
import sys, os

MODULE_PREFIX = 'speca.lang.%s'
GENERATOR_PREFIX = 'speca.lang.%s.generator'

def load_generator(name):
    g_name = GENERATOR_PREFIX % name
    if g_name in sys.modules:
        return 
    try:
        __import__(g_name)
    except ImportError:
        pass

def load_generators():
    for name in generator_names():
        load_generator(name)

def get_generators():
    generators = []
    for g_name in generator_names():
        load_generator(g_name)
        g = GENERATOR_PREFIX % g_name
        if g in sys.modules:
            generators.append(sys.modules[g])
    return generators

def generator_names():
    cur_dir = os.path.dirname(__file__)
    names = []
    for name in os.listdir(cur_dir):
        c_dir = os.path.join(cur_dir, name)
        if os.path.isfile(os.path.join(c_dir, 'generator.py')):
            names.append(name)
    return names

class EmptyModuleNameException(Exception):
      """
      Exception raising on empty module name
      """
      
