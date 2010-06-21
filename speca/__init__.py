#!/usr/bin/env python 
# -*- coding: utf-8 -*-   

# autocomplete ?

from  speca.commands import get_command
import sys

def main(init_arg=None):
    if init_arg is None:
        init_arg = sys.argv[1:]
    # autocomplete

    command = init_arg[0]
    cmd = get_command(command)

    if cmd:
        cmd.run(cmd_line_args=init_arg[1:])
    else:
        print 'Command not found!'


def import_module(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
