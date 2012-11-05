# -*- coding: utf-8 -*-

from twisted.test.proto_helpers import StringTransport
from twisted.protocols.basic import LineOnlyReceiver

from py_ircd.client import Client    


class MockFactory():
    def __init__(self):
        self.clients = {}


class MockClient(Client):
            
    factory = MockFactory()
    
    def __init__(self):
        Client.__init__(self)
        self.transport = StringTransport()
        self.makeConnection(self.transport)
        
    def connectionMade(self):
        self.host = self.transport.getHost().host
        self.server_host = 'testing_srv'
        
    def dataReceived(self, data):
        LineOnlyReceiver.dataReceived(self, data)
    
    def t_get_data(self):
        return self.transport.value()
    
    def t_flush_data(self):
        self.transport.clear()
        
    def t_send_lines(self, *lines):
        lines = '\n'.join(lines) 
        self.dataReceived(lines + '\n')
        
    def t_send_line(self, line):
        self.dataReceived(line + '\n')

        