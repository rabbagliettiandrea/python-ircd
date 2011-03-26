# -*- coding: utf-8 -*-

from collections import namedtuple
from twisted.trial import unittest
from twisted.internet import reactor


class Platform(unittest.TestCase):

    def assert_data_contains(self, client, expected):
        self.assertIn(expected, client.t_get_data())

    def assert_exchange(self, client, tuples):
        if not isinstance(tuples, list):
            tuples = [tuples]
        ExchangeTuple = namedtuple('ExchangeTuple', 'to_send expected')
        tuples = [ExchangeTuple(tuple[0]+'\n', tuple[1]) for tuple in tuples]
        for tuple in tuples:
            client.t_send_data(tuple.to_send)
            reply_from_srv = client.t_get_data()
            self.assertIn(tuple.expected, reply_from_srv)
        client.t_flush_data()
            
    def hello(self, client, psw='pass_test', nick='nick_test', user='user_test'):
        client.t_send_data('pass %s\n' % psw+
                           'nick %s\n' % nick +
                           'user %s 0 * :Realname\n' % user)
        self.assertIn(':testing_srv 001', client.t_get_data())
        client.t_flush_data()