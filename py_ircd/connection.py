# -*- coding: utf-8 -*-

from twisted.protocols.basic import LineOnlyReceiver
from py_ircd import utils


class Connection(LineOnlyReceiver):
    
    ID = 0
    delimiter = '\n' # overrida il delimitatore di LineOnlyReceiver, '\r\n'  
    
    def connectionMade(self):
        self.print_log = utils.print_log
        self.ID = Connection.ID
        Connection.ID += 1
        self.server_host = self.factory.host
        self.host = self.transport.getHost().host
        self.factory.connections_count += 1
        self.print_log("%s connected" % self)
        self.print_log('connection count: %s' % self.factory.connections_count)

    def connectionLost(self, reason):
        self.factory.connections_count -= 1
        self.print_log('%s disconnected: %s' % (self, reason.getErrorMessage()))
        self.print_log('connection count: %s' % self.factory.connections_count)

    def __str__(self):
        return  "[connectionID: %s]" % self.ID
