# -*- coding: utf-8 -*-

import platform
import unittest

from py_ircd.test.test_mock_client import MockClientTest


if __name__ == '__main__':    
        suite = unittest.TestLoader().loadTestsFromTestCase(MockClientTest)
        unittest.TextTestRunner(verbosity=2).run(suite)