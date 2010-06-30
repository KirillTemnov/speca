# -*- coding: utf-8 -*-
"""
Erlang code generator
"""
from speca.lang.erlang import GEN_SERVER_TEMPLATE, FSM_TEMPLATE, SUPERVISOR_TEMPLATE, \
    FUNC_DOC_HL, SET_VAR, ErlangOptionsException, AssignToExistingVariableException
from speca.lang import EmptyModuleNameException
from speca.parser import find_options, get_directive_option, get_params, \
    get_return_param, substitute, Func, FuncParam, Struct, DEFAULT_MODULE_OPTIONS
import os, sys
from datetime import datetime

# start_mode : local of global (default)
# restarting_mode_strategy: one_for_one,  rest_for_one, simpleone_for_one, one_for_all(default)
# max_restarts: number of attemps, default: 10
# time_limit_on_restarts: number of restarts(default=5) in seconds.
#                         If during last time_limit_on_restarts seconds
#                         supervisor restarts its childs is more, than
#                         time_limit_on_restarts, supervisor craches.
ERLANG_MODULE_OPTIONS = dict(start_mode=u'global',restarting_mode_strategy=u'one_for_all',\
                                 max_restarts=10, time_limit_on_restarts=5)
ERLANG_MODULE_OPTIONS.update(DEFAULT_MODULE_OPTIONS)

def make_erlang_var(var):
    """
    Make erlang variable from var.
    """
    var = var.strip()
    if var.find(' ') > -1:
        return ''.join([x.capitalize() for x in var.split(' ')])
    if var.find('_') > -1:
        return ''.join([x.capitalize() for x in var.split('_')])
    if var.find('-') > -1:
        return ''.join([x.capitalize() for x in var.split('-')])
    return var.capitalize()

def make_erlang_func(var):
    """
    Make erlang function or record name from var.
    """
    return var.strip().replace(' ', '_').replace('-', '_').lower()


def can_generate(options):
    """
    Returns true if module can generate code from file.
    """
    lang = options.get_option('lang')
    return type(lang) == list and 'erlang' in lang or lang  == 'erlang'


def get_module_functions(module_directive):
    """
    Get list of :class: `Func` objects, from module_directive.
    """
    functions = []
    for f in module_directive.childs:
        if f.directive == 'func':
            fun = Func(f.value, doc=get_directive_option(f, 'doc'), \
                           store_optional_params_in_list=True)
            for fp in get_params(f):
                fun.add_param(fp)
            fun.returns = get_return_param(f)
            functions.append(fun)
    return functions

def get_records(module_directive, folder):
    """
    Return list of :class: `Struct` objects from module_directive.
    """
    records = []
    for r in module_directive.childs:
        if r.directive == 'struct':
            s = Struct(r.value, doc=get_directive_option(r, 'doc'))
            for param in get_params(r):
                s.add_param(param)
            records.append(s)
    return records

#  TODO add code here

def get_export_functions(functions):
    """
    Get string, representing export functions.
    """
    export_functions = u''
    if functions:
        export_functions = u',\n\t'
        funcs_list = []
        for f in functions:     # TODO single arity!
            funcs_list.append('%s/%s' % (make_erlang_func(f.name), f.arity))
        export_functions += u',\n\t'.join(funcs_list)
    return export_functions

def get_proxy_functions(functions):
    """
    Get string, representing proxy functions for module.
    """
    proxy_functions = u''
    for f in functions:
        params_string = u','.join([make_erlang_var(p.name) for p in f.params])
        proxy_functions += FUNC_DOC_HL
        proxy_functions += u'%% Function:\t%s/%s\n' % (make_erlang_func(f.name), f.arity)
        proxy_functions += u'%% Description: %s\n' % (f.doc)
        if f.returns:
            for p in f.params:
                if p.name == f.returns.name:
                    raise AssignToExistingVariableException('Can\'t assign variable %s [function=%s]' % (make_erlang_var(f.returns.name), f.name))
            proxy_functions += u'%% Returns:\t %s %s\n' % (make_erlang_var(f.returns.name), f.returns.doc)
        proxy_functions += FUNC_DOC_HL
        proxy_functions += u'%s(%s) ->\n' % (make_erlang_func(f.name), params_string)
        if len(params_string) > 0:
            proxy_functions += u'    gen_server:call({global, ?SERVER}, {%s, %s}).\n\n' % (make_erlang_func(f.name), params_string)
        else:
            proxy_functions += u'    gen_server:call({global, ?SERVER}, {%s}).\n\n' % make_erlang_func(f.name)

    return proxy_functions

def get_handle_call_functions(functions):
    handle_call_functions = u''
    for f in functions:
        params_string = u','.join([make_erlang_var(p.name) for p in f.params])
        if len(params_string) > 0:
            handle_call_functions += u'handle_call({%s, %s}, From, State) ->\n    %% Insert code here\n' % (make_erlang_func(f.name), params_string)
        else:
             handle_call_functions += u'handle_call({%s}, From, State) ->\n    %% Insert code here\n' % make_erlang_func(f.name)
        if f.returns:
            handle_call_functions += u'    %s = %s,\n    {reply, {ok, %s}, State};\n\n' % \
                (make_erlang_var(f.returns.name), SET_VAR, make_erlang_var(f.returns.name))
        else:
            handle_call_functions += u'    {reply, ok, State}; \n\n'
    return handle_call_functions

def generate_genserver(directive, functions, records, folder):
    """
    Generate genserver files from functions and records lists.
    """
    d = directive
    params = dict(module_name=d.value, author=get_directive_option(d, 'author'),\
                      author_email=get_directive_option(d, 'author-email'), \
                      description=get_directive_option(d, 'doc'), \
                      date=datetime.now().strftime('%d.%m.%Y'), \
                      export_functions=get_export_functions(functions), \
                      proxy_functions=get_proxy_functions(functions), \
                      handle_call_functions=get_handle_call_functions(functions))
    params.update(ERLANG_MODULE_OPTIONS)
    if records:                 # make hrl file
        header_file = '%s.hrl' % d.value
        params['header_files'] = '-include("%s").' % header_file
        header_file = os.path.join(folder, header_file)
        records_string = u''
        for r in records:
            if len(r.params) == 0:
                print 'Warning: record %s has no fields, skip it...' % make_erlang_func(r.name)
                continue

            records_string += FUNC_DOC_HL + u'%% ' + r.doc + u'\n'
            for p in r.params:
                records_string += u'%%%% %s : %s\n' % (make_erlang_var(p.name), p.doc)
            records_string += FUNC_DOC_HL
            records_string += u'-record(%s, {%s}).\n\n' % \
                (make_erlang_func(r.name), u', '.join([make_erlang_var(x.name) for x in r.params]))

        if records_string:
            f = open(header_file, 'wb')
            f.write(records_string.encode('utf-8'))
            f.close()
            print 'Create file %s' % header_file
        else:
            print 'Header file %s was not prodused. ' % header_file
            del params['header_files']

    f_name = os.path.join(folder, '%s.erl' % d.value)
    f = open(f_name, 'wb')
    unicode_string = substitute(GEN_SERVER_TEMPLATE, params)
    f.write(unicode_string.encode('utf-8'))
    f.close()
    print 'Create file %s' % f_name
    if get_directive_option(d, 'supervisor'): # make supervisor for genserver
        params['supervisor_name'] = '%s_sup' % d.value
        f_name = os.path.join(folder, '%s_sup.erl' % d.value)
        f = open(f_name, 'wb')
        unicode_string = substitute(SUPERVISOR_TEMPLATE, params)
        f.write(unicode_string.encode('utf-8'))
        f.close()
        print 'Create file %s' % f_name


def generate(directives, filename):
    """
    Function, that generates code in Erlang
    """
    print 'Erlang generator [START]'
    options = find_options(directives, ERLANG_MODULE_OPTIONS)
    if not can_generate(options):
        raise ErlangOptionsException("Erlang can't generate template for file %s " % filename)
    e_dir = options.get_option('out_dir')
    if options.get_option('make_lang_dir'):
        e_dir = os.path.join(e_dir, 'erlang')

    e_dir = os.path.abspath(e_dir)
    if not os.path.exists(e_dir):
        os.makedirs(e_dir)
    mod_name = ''
    for d in directives:
        if d.directive == 'module':
            if not d.value:
                raise EmptyModuleNameException('module name can\'t be empty [%s]' % filename)

            functions = get_module_functions(d)

            # create hrl file, if needed
            records = get_records(d, e_dir)

            # read module and write it down
            if get_directive_option(d, 'genserver'): # make genserver
                generate_genserver(d, functions=functions, records=records, folder=e_dir)


            elif get_directive_option(d, 'fsmserver'): # make fsm server
                pass
            else:               # just make erlang module
                pass
    print 'Erlang generator [DONE]'

