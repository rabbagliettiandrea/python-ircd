# -*- coding: utf-8 -*-

import unittest
import socket
import threading

from py_ircd.const import constants
from py_ircd import utils
from py_ircd.server import Server


class MockClientTest(unittest.TestCase):

    @staticmethod
    def setUpClass():
        utils.VERBOSITY_LEVEL = constants.VERBOSITY_SILENT
        
    def setUp(self): # viene chiamato prima del test
        addr_tuple = ('localhost', 6969)
        self.server = Server(*addr_tuple)
        t = threading.Thread(target=self.server.start)
        t.start()
        self.client = socket.create_connection(addr_tuple)
    
    def tearDown(self): # viene chiamato dopo il test
        self.server.stop()
        
    def test_OK1(self):
        self.client.sendall('pass passDiProva\n\
                             nick nickDiProva\n\
                             user guest 0 * :Nome\n\
                             join #chanDiProva\n')
        #print self.client.recv(1024)
        
        
    