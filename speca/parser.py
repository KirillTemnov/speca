#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parser for pseudo-code api file in reST format

file sample:
================================================================================
.. comment


.. options::
  :o1: val1
  :o2: val2

.. module:: module_name
  :doc: Module docstring
  :author: author
  :author-email: author email

.. class:: Class
   :doc: Class docstring

   .. method:: method1
      :doc: Method docstring
      :param1: Param1 description
      :param2: Param2 description
      :return: return description

.. func:: name
   :doc: Func docstring
   :param1: Param1 description
   :param2: Param2 description
================================================================================

"""

import re
# re for any directive
# .. sample::
# .. another_sample::
# ..id and_another:: with val
DIRECTIVE_RE = re.compile('^\s*\.\.(((?P<id>[-\|\w ]+)|)\s+|)(?P<directive>([^\:]+))\:\:(\s*(?P<value>[^$]+)|)\s*$')
# re for any attribute in colons
# :sample:
# :second sample: with value
ATTRIB_RE = re.compile('\s*\:(?P<name>[-\w ]+)\:\s*(P?<value>.*)$')
# re for any attribute in colons, whithout spece inside
# :sample:
# :this is not valid:
OPTION_RE = re.compile('\s*\:(?P<name>[^\:]+)\:\s*(?P<value>.*)$')
# re for parameter (inside function or method), consists of keyword 'param', param name
# and optional param type
# :param p1: docs
# :param p2:
# :param p3 Int: docs
# :param: docs <- this is not valid
PARAM_RE = re.compile('^\s*\:param (?P<name>[-\w]+)( (?P<type>[-\w]*)|)\:\s+(?P<doc>.*)$')

RETURN_RE = re.compile('^\s*\:return\s*(?P<name>[-\w]+)( (?P<type>[-\w]*)|)\:\s+(?P<doc>.*)$')

COMMENT_RE = re.compile('^\s*\.\.[^:]+$')

INDENT_RE = re.compile('^\s*')

# default options for parser
# out_dir - folder for creating templates
# make_lang_dir - if set to True, each generator creates subfolder with corresponding language name
DEFAULT_MODULE_OPTIONS = dict(out_dir='.', make_lang_dir=True)

def is_comment(string):
    """
    Check if string is reST comment
    """
    return COMMENT_RE.match(string) and True or False

def get_directive_from_string(string):
    return DIRECTIVE_RE.search(string)

def get_attribute_from_string(string):
    return ATTRIB_RE.search(string)

def get_option_from_string(string):
    return OPTION_RE.search(string)

def get_indent(string):
    return len(INDENT_RE.match(string).group(0))



class DirectiveOption:
      """
      Option for reST directive
      """
      def __init__(self, name, value, dtype=u''):
          self.name, self.value, self.type = name, value, dtype

class Directive:
    """
    Class, representing reST directives.
    """
    def __init__(self, directive, id=u'', value=u'', parent=None, indent=0):
        self.directive = directive
        self.id = id
        self.value = value
        self.options = []
        self.childs = []
        self.parent = parent
        self.indent = indent

    def princ(self):
        """
        Debug print function
        """
        print '%s<%s |%s|> %s' % (' '*self.indent, self.directive, self.id, self.value)
        print '%soptions:'  % (' '*self.indent)
        if not self.options:
            print '%s[Empty]'% (' '*self.indent)
        for o in self.options:
            print '%s :%s: %s' % (' '*self.indent, o.name, o.value)
        print '%schilds: ' % (' '*self.indent)
        if not self.childs:
            print '%s[Empty]' % (' '*self.indent)
        for c in self.childs:
            c.princ()

def read_blocks(filename):
    """
    Read reST file by text blocks
    """
    blocks = []
    block = u''
    last_indent = 0
    f = open(filename)
    for line in f.readlines():
        if line.strip() != '':   # insert hl ?
            indent = get_indent(line)
            if indent <= last_indent:
                blocks.append(block)
                block = u''
            block += line.decode('utf-8')
    if block:
        blocks.append(block)
    return blocks[1:]

def parse_block(lines, index=0, directive=None, default_param_value='true'):
    """
    Parse block and returns instance of :class: `Directive` object

    :param lines: lines of block.
    :param index: line index.
    :param directive: directive, uses for recursive call.
    :param default_param_value: default value for directive option
    """
    if index >= len(lines):      #
        return directive

    if lines[index].strip() == '':
        parse_block(lines, index+1, directive, default_param_value)
    elif is_comment(lines[index]):
        indent =  get_indent(lines[index])
        c_indent = indent-1
        while index < len(lines) and c_indent < indent:
            index += 1
            if len(lines) > index:
                c_indent = get_indent(lines[index])
                if c_indent >= indent:
                    index -=1
        parse_block(lines, index+1, directive, default_param_value)

    elif get_directive_from_string(lines[index]): # directive
        indent = get_indent(lines[index])
        m = get_directive_from_string(lines[index])
        id = m.group('id') or u''
        value = m.group('value') or u''
        d =  Directive(m.group('directive'), id=id, value=value, parent=directive, indent=indent)
        if isinstance(directive, Directive):
            if directive.indent == indent:
                directive.parent.childs.append(d)
                d.parent = directive.parent # tricky hack!
                parse_block(lines, index+1, d, default_param_value)
            elif directive.indent < indent:
                directive.childs.append(d)
                parse_block(lines, index+1, d, default_param_value)
            else:
                parse_block(lines, index, directive.parent, default_param_value)
        else:
            directive = d
            parse_block(lines, index+1, d, default_param_value)
    elif get_option_from_string(lines[index]):
        m =  get_option_from_string(lines[index])
        name = m.group('name') or default_param_value
        value = m.group('value') or 'true'
        o = DirectiveOption(name, value)
        if directive:
            directive.options.append(o)
        parse_block(lines, index+1, directive, default_param_value)
    else:                       # skip comments and other objects
        parse_block(lines, index+1, directive, default_param_value)
    return directive

def parse_file(filename):
    """
    Read reST file and return directives
    """
    blocks = read_blocks(filename)
    directives = []
    for block in blocks:
        directive = parse_block(block.split('\n'))
        if directive:
            directives.append(directive)
    return directives

def find_options(directives, def_opts=DEFAULT_MODULE_OPTIONS):
    """
    find ``options`` directive and return id
    """
    for d in directives:
        if d.directive == u'options':
            return Options.from_directive(d, def_opts)
    return None

def get_directive_option(directive, option, default=None):
    """
    Get directive's option value
    """
    if isinstance(directive, Directive):
        for o in directive.options:
            if o.name == option:
                return o.value
    return default

def get_params(directive):
    params = []
    if isinstance(directive, Directive):
        for d_option in directive.options:
            _str = ':%s: %s' % (d_option.name, d_option.value)
            m = PARAM_RE.search(_str)
            if m:         # name, type, doc
                fp = FuncParam(name=m.group('name'), doc=m.group('doc'), ptype=m.group('type'))
                params.append(fp)
    return params

def get_return_param(directive):
    if isinstance(directive, Directive):
        for d_option in directive.options:
            _str = ':%s: %s' % (d_option.name, d_option.value)
            m = RETURN_RE.search(_str)
            if m:
                return FuncParam(name=m.group('name'), doc=m.group('doc'), ptype=m.group('type'))
    return None

def substitute(content, target_dict, ommited=''):
    """
    Sibstitute vars in string bo a dict values.
    >>> substitute("{{sample_1}} world {{ another }}", dict(sample_1='Hello'), ommited='!')
    Hello world !
    """
    var_name_brackets_re = re.compile('\{\{\s{0,}[-a-z_A-Z0-9]+\s{0,}\}\}')
    var_name_re = re.compile('[-a-z_A-Z0-9]+')
    for var_str in var_name_brackets_re.findall(content):
        var = target_dict.get(var_name_re.findall(var_str)[0], ommited)
        content = content.replace(var_str, unicode(var))
    return content

class FuncParam:
    """
    Function/method parameter
    """
    def __init__(self, name, doc=u'', ptype=u'', optional=False):
        self.name = name
        self.doc, self.type = doc, ptype
        self.optional = optional

    def __str__(self):
        return u'<FuncParam: %s[%s]> %s%s'(self.name, self.type, self.doc, self.optional and '[optional]' or '')

class Func:
    """
    Class for storing function/method
    """
    def __init__(self, name, doc='', store_optional_params_in_list=False):
        self.name = name
        self.__params = []
        self.returns = None
        self.doc = doc
        self.store_in_list = store_optional_params_in_list

    def add_param(self, param):
        if isinstance(param, FuncParam):
            self.__params.append(param)

    def __repr__(self):
        return u'<speca.parser.Func %s>' % self.name

    @property
    def params(self):
        return self.__params

    @property
    def arity(self):
        active_params = 0
        optional_params = 0
        for p in self.__params:
            if p.optional:
                optional_params += 1
            else:
                active_params += 1
        if optional_params == 0:
            return active_params
        elif self.store_in_list: #  optional_params >= 1 - store optional params in list
            return [active_params, active_params+1]
        else:
            return [active_params, active_params+optional_params]

    def __str__(self):
        params = [p.name for p in self.__params]
        return u'%s (%s) -> %s \n doc: %s\n' % (self.name, ', '.join(params), self.returns, self.doc)

class Struct:
    """
    Data structure description.
    Format:
      .. struct:: name
         :doc: Struct docs
         :param param1: Param1 doc.
         :param param2: Param2 doc.
    """
    def __init__(self, name, doc=''):
        self.name = name
        self.doc = doc
        self.__params = []

    def add_param(self, param):
        if isinstance(param, FuncParam):
            self.__params.append(param)

    def __repr__(self):
        return u'<speca.parser.Struct %s>' % self.name

    @property
    def params(self):
        return self.__params


class Options:
      """
      Class for storing file options
      """
      def __init__(self, opts={}):
          self.__opts = opts

      @classmethod
      def from_directive(self, directive, def_opts):
          o = Options(def_opts)
          for opt in directive.options:
              o.replace_option(opt.name, opt.value)
          return o

      def add_option(self, key, value):
          if key in self.__opts:
              if type(self.__opts[key]) == list:
                  self.__opts[key].append(value)
              else:
                  self.__opts[key] = [self.__opts[key], value]
          else:
              self.__opts[key] = value

      def replace_option(self, key, value):
          self.__opts[key] = value

      def get_option(self, key, default=u''):
          return self.__opts.get(key, default)

      def __repr__(self):
          return u'<speca.parser.Options: %s >' % self.__opts

