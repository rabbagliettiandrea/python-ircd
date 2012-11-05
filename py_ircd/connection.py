# -*- coding: utf-8 -*-

from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.error import ConnectionDone
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from py_ircd.utils import *


class PingTimeoutHandler():
    
    def __init__(self, connection):
        self.connection = connection
        self.idle_time = 0
        self.loop = LoopingCall(self._handle)
        self.disconnect_schedule = None
        reactor.callLater(1, self.loop.start, 1)
        
    def _handle(self):
        self.idle_time += 1
        if self.idle_time == 240:
            self.connection.send("PING :%s" % self.connection.server_host)
            self.disconnect_schedule = reactor.callLater(240, self.connection.quit, 'Ping timeout: 240 seconds')
    
    def refresh(self):
        self.idle_time = 0
        if self.disconnect_schedule and self.disconnect_schedule.active():
            self.disconnect_schedule.cancel()
    
    def stop(self):
        self.loop.stop()


class Connection(LineOnlyReceiver):
    
    ID = 0
    delimiter = '\n' # overrida il delimitatore di LineOnlyReceiver, '\r\n'  
    
    def connectionMade(self):
        self.timeout_handler = PingTimeoutHandler(self)
        self.factory.connections_count += 1
        self.ID = Connection.ID
        Connection.ID += 1
        self.server_host = self.factory.host
        self.host = self.transport.getHost().host
        print_log("%s connected" % self)
        print_log('connection count: %s' % self.factory.connections_count)

    def connectionLost(self, reason):
        self.timeout_handler.stop()
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
        self.timeout_handler.refresh()

