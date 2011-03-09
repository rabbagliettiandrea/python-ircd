# -*- coding: utf-8 -*-

import unittest
import time

from py_ircd.test.test_mock_client import MockClientTest


if __name__ == '__main__':    
        suite = unittest.TestLoader().loadTestsFromTestCase(MockClientTest)
        for i in range(1000):
            unittest.TextTestRunner(verbosity=0).run(suite)
            #time.sleep(0.5)