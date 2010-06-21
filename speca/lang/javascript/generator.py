# -*- coding: utf-8 -*-  

def can_generate(options):
    """
    Returns true if module can generate code from file
    """
    lang = options.get_option('lang')
    return type(lang) == list and 'javascript' in lang or lang  == 'javascript'

def generate():
    """
    Function, that generates code in Javascript
    """
    print 'Javascript generator [START]'
    print 'Javascript generator [DONE]'
