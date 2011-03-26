# -*- coding: utf-8 -*-

from twisted.test.proto_helpers import StringTransport

from py_ircd.client import Client


class MockClient(Client):
    
    def __init__(self):
        Client.__init__(self)
        self.transport = StringTransport()
        self.makeConnection(self.transport)
    
    def connectionMade(self):
        def do_nothing(*args):
            pass
        self.print_log = do_nothing
        self.host = self.transport.getHost().host
        self.server_host = 'testing_srv'
        
    def t_get_data(self):
        return self.transport.value()
    
    def t_flush_data(self):
        self.transport.clear()
        
    def t_send_data(self, data):
        self.dataReceived(data)
        
    def t_send_line(self, line):
        self.dataReceived(line+'\n')
    
        
        
        