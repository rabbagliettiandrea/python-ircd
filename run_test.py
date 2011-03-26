# -*- coding: utf-8 -*-

from twisted.trial import unittest, runner, reporter
from py_ircd.test import test_irc


if __name__ == '__main__':
        results = reporter.TreeReporter()
        suite = unittest.TestSuite()
        test_list = runner.TestLoader().loadModule(test_irc)
        suite.addTests(test_list)
        suite.run(results)
        results.done()