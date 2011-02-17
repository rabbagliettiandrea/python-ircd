# -*- coding: utf-8 -*-

import platform
import unittest

from hwup_ircd.test import test_basic

#############################################
if __name__ == '__main__':    
    if platform.python_version_tuple() >= ['2', '7', '0']:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_basic.Test_IRC_command)
        unittest.TextTestRunner(verbosity=2).run(suite)
    else:
        print('Needed Python version >=2.7')