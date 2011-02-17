# -*- coding: utf-8 -*-

from hwup_ircd.error import client_error

#############################################
# Classe Channel: gestisce tutte le informazioni su un canale
class Channel(object):

    def __init__(self, name):
        self.name = name
        self.topic = None
        self.flags = set()
        self.client_list = []
        self.owner = None

    def relay(self, sender, msg):
        for client in self.client_list:
            if not client == sender:
                client.reply("[" + self.name + "] " + sender.nick + ": " + msg + "\n")

#############################################
# Classe Client: gestisce le comunicazioni con un singolo client remoto
class Client(object):
    ID = 0                      # ID serve per generare un id per ogni client

    def __init__(self, sock):
        self.ID = Client.ID
        self.sock = sock
        self.logged = False     # Fin quando il client non invia la sequenza [pass->]nick->user
        self.user = None
        self.nick = None
        self.realName = None
        self.password = None
        self.flags = set()         # Flag attivi per quell'utente
        self.joinChannel_list = {}
        Client.ID += 1

    def __str__(self):
        if self.logged:
            return "client [%s] {nick: %s}" % (self.ID, self.nick)
        else:
            return "client [%s] {nick: %s, not logged}" % (self.ID, self.nick)

    def reply(self, msg):
        try:
            if self.sock.sendall(msg): raise # se sendall() restituisce None è andato tutto a buon fine
        except:
            raise client_error.ReplyException()

