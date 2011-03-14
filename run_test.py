# -*- coding: utf-8 -*-

from twisted.trial import unittest, runner, reporter
import py_ircd.test


if __name__ == '__main__':
        results = reporter.TreeReporter()
        suite = runner.TestLoader().loadPackage(py_ircd.test)
        suite.run(results)
        results.done()