# -*- coding: utf-8 -*-

import traceback
import sys

from py_ircd.const import constants


VERBOSITY_LEVEL = constants.VERBOSITY_NORMAL # può essere variare a causa di argparse nel main

def print_log(msg):
    if VERBOSITY_LEVEL > 0:
        print '-L- %s' % msg

def print_exc(exc=None, msg=None): 
    if VERBOSITY_LEVEL > 0:
        empty_arg = not exc and not msg
        if empty_arg:
            raise TypeError('print_exc() takes at least one argument (0 given)')
       
        if exc and msg: 
            print '-E- [%s]: %s' % (exc.__class__.__name__, msg)
        elif exc and not msg: 
            print '-E- [%s]: %s' % (exc.__class__.__name__, str(exc))
        else: 
            print '-E- %s' % msg

        if VERBOSITY_LEVEL>=2 and exc:
            traceback.print_exc(file=sys.stderr)
        
def print_warn(msg):
    if VERBOSITY_LEVEL > 0:
        print '-W- %s' % msg
        