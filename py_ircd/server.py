# -*- coding: utf-8 -*-

from twisted.internet import reactor, protocol
from py_ircd.client import Client 


class Server(protocol.ServerFactory):
    
    protocol = Client

    def start(self, host, port):
        if not self.is_running():
            self.connections_count = 0
            self.clients = {} # { nick : client }
            self.host = host
            self.port = port
            reactor.listenTCP(port=port, factory=self, interface=host)
            reactor.run()
        
    def stop(self):
        reactor.stop()
        
    def is_running(self):
        return reactor.running
    
