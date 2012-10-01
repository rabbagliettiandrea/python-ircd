# -*- coding: utf-8 -*-

from twisted.trial import unittest, runner, reporter
from py_ircd.test import test_irc, test_debug


if __name__ == '__main__':
        results = reporter.TreeReporter()
        suite = unittest.TestSuite()
        test_list = runner.TestLoader().loadModule(test_irc)
        singleton = runner.TestLoader().loadModule(test_debug)
        suite.addTests(test_list)
        suite.addTests(singleton)
        suite.run(results)
        results.done()