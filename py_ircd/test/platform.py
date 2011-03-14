# -*- coding: utf-8 -*-

from collections import namedtuple
from twisted.trial import unittest

from twisted.internet import reactor
from twisted.test.proto_helpers import StringTransport

from py_ircd.test.mock_client import MockClient

class Platform(unittest.TestCase):
    
    def setUp(self): # viene chiamato prima del test
        self.transport = StringTransport()
        self.protocol = MockClient()
        self.protocol.makeConnection(self.transport)
        
    def tearDown(self): # viene chiamato dopo il test
        pass
    
    def assert_exchange(self, tuples):
        ExchangeTuple = namedtuple('ExchangeTuple', 'to_send expected')
        tuples = [ExchangeTuple(tuple[0]+'\r\n', tuple[1]) for tuple in tuples]
        for tuple in tuples:
            self.protocol.lineReceived(tuple.to_send)
            reply = self.transport.value()
            self.assertIn(tuple.expected, reply)
            
    