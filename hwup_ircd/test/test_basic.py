# -*- coding: utf-8 -*-

import unittest

from hwup_ircd import irc_command
from hwup_ircd.test import mock_classes


#############################################
class Test_IRC_command(unittest.TestCase):
    
    #############################################
    def setUp(self): # viene chiamato prima di tutti (non di ognuno) i metodi di test
        self.client = mock_classes.Client()
        self.server = mock_classes.Server()
    
    #############################################
    def tearDown(self): # viene chiamato dopo ogni i metodi di test
        self.client.__init__()
        self.server.__init__()

    #############################################
    def test_OK1(self): # test su una simulazione di traffico corretto client-server
        traffic = [ (irc_command.command_pass, 'pass provapwd', 'OK\n'), 
                    (irc_command.command_nick, 'nick provanick', 'OK\n'),  
                    (irc_command.command_user, 'user guest 0 * :Nome Cognome', 'OK, logged in\n'), 
                    (irc_command.command_join, 'join #canale', "Ok, joined channel") ]
        for tuple in traffic:
            dataSplit = tuple[1].lower().strip().rsplit()
            tuple[0](self.client, dataSplit, self.server)
            self.assertIn(tuple[2], self.client.reply_output) # se la stringa tuple[2] è sottoinsieme della stringa reply_output (casa is in casato) sennò raisa un fail
        self.client.reply_output = None # assicura che reply_output sia None
        dataSplit = 'privmsg #canale :prova'.split()
        irc_command.command_privmsg(self.client, dataSplit, self.server) # se privmsg da errore manderà una reply al client che andrà finire nell'attributo del mock: reply_output
        if self.client.reply_output: # quindi se diverso da None il test avrà fallito
            self.fail(self.client.reply_output)
            
