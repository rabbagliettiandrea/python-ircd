# -*- coding: utf-8 -*-

from py_ircd.client import Client

class MockClient(Client):
    
    def connectionMade(self):
        
        def do_nothing(*args):
            pass
        
        self.print_log = do_nothing
        self.host = self.transport.getHost().host
        self.server_host = 'testing_srv'