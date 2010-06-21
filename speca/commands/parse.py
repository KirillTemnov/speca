#!/usr/bin/env python 
# -*- coding: utf-8 -*-   

import sys, re
from speca.commands import AbstractCommand
from speca.parser import parse_file, find_options
from speca.lang import get_generators

class XCommand(AbstractCommand):
      """
      test command
      """
      name = 'test'

      def __init__(self):
          pass


      def run(self, *args, **kw):
          # TODO add error checks
          if 'cmd_line_args' in kw:
              cmd_args = kw['cmd_line_args']
              print 'filename= %s' % cmd_args[0]
              directives = parse_file(cmd_args[0])
              for d in directives:
                  print '.. Block::'
                  d.princ()
                  print '-'* 80

class YCommand(AbstractCommand):
      """
      test for generate 
      """
      name = 'gen'

      def __init__(self):
          pass

      def run(self, *args, **kw):
          if 'cmd_line_args' in kw:
              cmd_args = kw['cmd_line_args']
              filename = cmd_args[0]
              directives = parse_file(filename)
              opts = find_options(directives)
              if opts:
                  for gen in get_generators():
                      if gen.can_generate(opts): 
                          # break not needed, you may use more 1 generator
                          gen.generate(directives, filename)


__all__ = [XCommand, YCommand]

