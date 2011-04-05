# -*- coding: utf-8 -*-

from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.error import ConnectionDone
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from py_ircd.utils import *

class Connection(LineOnlyReceiver):
    
    ID = 0
    delimiter = '\n' # overrida il delimitatore di LineOnlyReceiver, '\r\n'  
    
    def connectionMade(self):
        self.idle_time = 0
        self.check_alive_loop = LoopingCall(self.handle_idle_time)
        reactor.callLater(1, self.check_alive_loop.start, 1)

        self.factory.connections_count += 1
        self.ID = Connection.ID
        Connection.ID += 1
        self.server_host = self.factory.host
        self.host = self.transport.getHost().host
        print_log("%s connected" % self)
        print_log('connection count: %s' % self.factory.connections_count)

    def connectionLost(self, reason):
        self.check_alive_loop.stop()
        self.factory.connections_count -= 1
        if not reason.check(ConnectionDone):
            self.quit()
        if self in self.factory.clients:
            del self.factory.clients[self]
        print_log('%s disconnected: %s' % (self, reason.getErrorMessage()))
        print_log('connection count: %s' % self.factory.connections_count)

    def __str__(self):
        return  "[connectionID: %s]" % self.ID

    def dataReceived(self, data):
        LineOnlyReceiver.dataReceived(self, data)
        self.idle_time = 0
    
    def handle_idle_time(self):
        self.idle_time += 1
        if self.idle_time == 5:
            self.send(":%s PING" % self.get_ident()
            
#            if 
#            self.idle_time = 0
