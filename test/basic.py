# -*- coding: utf-8 -*-

import unittest

import sys
sys.path.append('../')

import irc_command

#############################################
class Client(object):   # classe mock che emula il comportamento/attributi della classe reale
    def __init__(self):
        self.password = None
        self.nick = None
        self.reply_output = None
        self.ID = 0
        self.sock = None
        self.logged = False     # Fin quando il client non invia la sequenza [pass->]nick->user
        self.user = None
        self.realName = None
        self.flags = set()         # Flag attivi per quell'utente
        self.joinChannel_list = {}
        
    def reply(self, reply_msg):
        self.reply_output = reply_msg


#############################################
class Server(object):   # classe mock che emula il comportamento/attributi della classe reale

    def __init__(self,):
        self.client_list = {}
        self.socket_list = []
        self.channel_list = {}


#############################################
class Test_irc_command(unittest.TestCase):
    
    #############################################
    def setUp(self): # viene chiamato prima di tutti (non di ognuno) i metodi di test
        self.client = Client()
        self.server = Server()
    
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


#############################################     
if __name__ == '__main__':
    import platform
    
    installed_ver = [int(i) for i in platform.python_version_tuple()] # verifica che la ver di python sia 3>= x >2.7
    if installed_ver[0] == 3 or (installed_ver[0] == 2 and installed_ver[1] >= 7):
        unittest.main()
    else:
        print('Needed Python version >=2.7')
        
    