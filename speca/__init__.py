#!/usr/bin/env python 
# -*- coding: utf-8 -*-   

from  speca.commands import get_command
import sys
from optparse import OptionParser

usage = """usage: %prog cmd filename

Commands:
  gen       Generate specifications using file.
  test      Test command.
"""

parser = OptionParser(usage=usage)

def main(init_args=None):
    if init_args is None:
        init_args = sys.argv[1:]

    (options, args) = parser.parse_args(init_args)
    
    if len(args) == 2:
        cmd = get_command(args[0])
        if not cmd:
            print 'unknown command'
            print usage
        else:
            cmd.run(cmd_line_args=[args[1]])
    else:
        print usage



def import_module(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
