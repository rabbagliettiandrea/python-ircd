# -*- coding: utf-8 -*-

from py_ircd.const import irc_replies


#############################################
# Classe Client: gestisce le comunicazioni con un singolo client remoto
class Client(object):
    ID = 0                      # ID serve per generare un id per ogni client

    def __init__(self, sock, server_host):
        self.ID = Client.ID
        Client.ID += 1
        self.sock = sock
        
        self.username = None
        self.host = sock.getpeername()[0]
        self.server_host = server_host
        self.nick = None
        self.realname = None
        self.password = None
        self.registered = False
        self.modes = set()              # Usermodes attivi per quell'utente
        self.channel_joined_list = {}   # { channame : channel_obj }

    def __str__(self):
        if self.registered:
            return "[clientID: %s][ident: %s]" % (self.ID, self.get_ident())
        else:
            return "[clientID: %s]" % self.ID

    def send_data(self, msg):
        #print_replyToClient(self, msg)
        if self.sock.sendall(msg + '\n'): # se sendall() restituisce None è andato tutto a buon fine
            raise client_errors.ReplyException()
    
    def get_irc_reply(self, reply, *args_reply):
        msg = irc_replies.dict[reply][1](*args_reply)
        id_msg = irc_replies.dict[reply][0]
        return ':%s %s %s %s' % (self.server_host, id_msg, self.nick, msg)

    def quit_irc(self, quit_msg):
        for channel in self.channel_joined_list.values():
            channel.relay(self, ":%s QUIT :%s" % (self.get_ident(), quit_msg))
            del channel.client_list[self]

    def get_ident(self):
        return "%s!%s@%s" % (self.nick, self.username, self.host)
