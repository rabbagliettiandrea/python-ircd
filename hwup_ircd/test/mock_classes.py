# -*- coding: utf-8 -*-


#############################################
class Client(object):   # classe mock che emula il comportamento/attributi della classe reale
    def __init__(self):
        self.password = None
        self.nick = None
        self.reply_output = None
        self.ID = 0
        self.sock = None
        self.registered = False     # Fin quando il client non invia la sequenza [pass->]nick->user
        self.user = None
        self.realname = None
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
