# -*- coding: utf-8 -*-

import platform
import unittest

from hwup_ircd.test import test_basic


if __name__ == '__main__':    
    installed_ver = [int(i) for i in platform.python_version_tuple()] # verifica che la ver di python sia 3>= x >2.7
    if installed_ver[0] == 3 or (installed_ver[0] == 2 and installed_ver[1] >= 7):
        suite = unittest.TestLoader().loadTestsFromTestCase(test_basic.Test_IRC_command)
        unittest.TextTestRunner(verbosity=2).run(suite)
    else:
        print('Needed Python version >=2.7')