# -*- coding: utf-8 -*-

from hwup_ircd.error import client_errors
from hwup_ircd.utils import print_replyToClient

#############################################
# Classe Channel: gestisce tutte le informazioni su un canale
class Channel(object):
    
    class Client_Property(object):
        def __init__(self, nick):
            self.nick = nick
            self.operator = False
            self.voice = False
        
        def __str__(self):
            prefix = (self.operator and '@') or (self.voice and '%') or ''
            return '%s%s' % (prefix, self.nick)
    
    def __init__(self, name):
        self.name = name
        self.topic = 'Topicozzo'
        self.flags = set()
        self.scope_flag = '='  # @ is used for secret channels, * for private channels, = for others (public channels)
        self.client_list = {} # { client : proprietà }
        self.owner = None
        
    def add_client(self, client):
        self.client_list[client] = Channel.Client_Property(client.nick)

    def nicklist_to_string(self):
        nicklist = []
        for client in self.client_list:
            nicklist.append(str(self.client_list[client]))
        return ' '.join(nicklist)
    
    def relay(self, sender, data):
        for client in self.client_list:
            if not client == sender:
                client.send_data(data)

            
