# -*- coding: utf-8 -*-

from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.error import ConnectionDone
from py_ircd.utils import *

class Connection(LineOnlyReceiver):
    
    ID = 0
    delimiter = '\n' # overrida il delimitatore di LineOnlyReceiver, '\r\n'  
    
    def connectionMade(self):
        self.ID = Connection.ID
        Connection.ID += 1
        self.server_host = self.factory.host
        self.host = self.transport.getHost().host
        self.factory.client_list.append(self)
        print_log("%s connected" % self)
        print_log('connection count: %s' % self.factory.connections_count())

    def connectionLost(self, reason):
        if not reason.check(ConnectionDone):
            self.quit()
        self.factory.client_list.remove(self)
        print_log('%s disconnected: %s' % (self, reason.getErrorMessage()))
        print_log('connection count: %s' % self.factory.connections_count())

    def __str__(self):
        return  "[connectionID: %s]" % self.ID
