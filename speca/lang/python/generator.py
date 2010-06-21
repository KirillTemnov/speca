# -*- coding: utf-8 -*-  

def can_generate(options):
    """
    Returns true if module can generate code from file
    """
    lang = options.get_option('lang')
    return type(lang) == list and 'python' in lang or lang  == 'python'


def generate(directives, filename):
    """
    Function, that generates code in Python
    """
    print 'Python generator [START]'
    print 'Python generator [DONE]'
