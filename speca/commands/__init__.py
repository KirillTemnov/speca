# -*- coding: utf-8 -*-   
"""
speca commands.
"""
#from speca import commands, import_module
import os, sys

class AbstractCommand:
    name = 'abstract_cmd'
    def __init__(self):
        pass

    def run(self, *args, **kw):
        pass
        

def load_all_commands():
    for name in command_names():
        load_command(name)

    
def get_command(command_name):
    """
    Return command object or none.
    """
    for cmd in command_names():
        load_command(cmd)
        cmd = 'speca.commands.%s' % cmd
        if cmd in sys.modules:
            command_module = sys.modules[cmd]
            for command_class in command_module.__all__:

                if 'name' in dir(command_class) and command_class.name == command_name:
                    return command_class()

    return None 

def load_command(name):
    full_name = 'speca.commands.%s' % name
    if full_name in sys.modules:
        return 
    try:
        __import__(full_name)
    except ImportError:
        pass


def command_names():
    c_dir = os.path.dirname(__file__)
    names = []
    for name in os.listdir(c_dir):
        if name.endswith('.py') and os.path.isfile(os.path.join(c_dir, name)):
            names.append(name[:-3])
    return names

__all__ = [get_command, command_names, load_command, load_all_commands, AbstractCommand]

