# -*- coding: utf-8 -*-

from collections import namedtuple
from twisted.trial import unittest
from twisted.internet import reactor

from py_ircd import utils
from py_ircd.const import constants


class Platform(unittest.TestCase):
    
    utils.VERBOSITY_LEVEL = constants.VERBOSITY_SILENT
    
    def assert_data_contains(self, client, expected):
        self.assertIn(expected, client.t_get_data())

    def assert_exchange(self, client, tuples):
        if not isinstance(tuples, list):
            tuples = [tuples]
        ExchangeTuple = namedtuple('ExchangeTuple', 'to_send expected')
        tuples = [ExchangeTuple(tuple[0], tuple[1]) for tuple in tuples]
        for tuple in tuples:
            client.t_send_line(tuple.to_send)
            reply_from_srv = client.t_get_data()
            self.assertIn(tuple.expected, reply_from_srv)
        client.t_flush_data()
            
    def hello(self, client, psw='pass_test', nick='nick_test', user='user_test'):
        client.t_send_lines('pass %s' % psw,
                           'nick %s' % nick,
                           'user %s 0 * :Realname' % user)
        self.assertIn(':testing_srv 001', client.t_get_data())
        client.t_flush_data()

    def join(self, client, chan_name):
        self.assert_exchange(client, ('join %s' % chan_name, ':testing_srv 366'))
        