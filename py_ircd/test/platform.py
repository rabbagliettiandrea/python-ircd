# -*- coding: utf-8 -*-

from collections import namedtuple
from twisted.trial import unittest

from py_ircd import utils
from py_ircd.const import constants
from py_ircd.const import irc_replies


class Platform(unittest.TestCase):
    
    utils.VERBOSITY_LEVEL = constants.VERBOSITY_SILENT
    
    def assert_data_contains(self, client, *expected_list):
        for expected in expected_list:
            if 'RPL' in expected or 'ERR' in expected:
                    self.assertIn(':testing_srv %s' % irc_replies.dict[expected][0], client.t_get_data())
            else:
                self.assertIn(expected, client.t_get_data())

    def assert_exchange(self, client, assert_func, tuples):
        if not isinstance(tuples, list):
            tuples = [tuples]
        ExchangeTuple = namedtuple('ExchangeTuple', 'to_send expected')
        tuples = [ExchangeTuple(tuple[0], tuple[1]) for tuple in tuples]
        for tuple in tuples:
            client.t_send_line(tuple.to_send)
            reply_from_srv = client.t_get_data().strip('\n')
            if 'RPL' in tuple.expected or 'ERR' in tuple.expected:
                assert_func(':testing_srv %s' % irc_replies.dict[tuple.expected][0], reply_from_srv)
            else:
                assert_func(tuple.expected, reply_from_srv)
            client.t_flush_data()
        
    def hello(self, client, psw='passtest', nick='nick_test', user='user_test'):
        client.t_send_lines('pass %s' % psw,
                           'nick %s' % nick,
                           'user %s 0 * :Realname' % user)
        self.assertNotIn(':testing_srv 461', client.t_get_data())
        self.assertIn(':testing_srv 001', client.t_get_data())
        client.t_flush_data()
        
        