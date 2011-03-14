# -*- coding: utf-8 -*-

from py_ircd.connection import Connection
from py_ircd.error import client_errors 
from py_ircd.utils import *
from py_ircd.const import irc_replies
from py_ircd import irc_commands

class Client(Connection):

    def __init__(self):
        self.username = None
        self.nick = None
        self.realname = None
        self.password = None
        self.registered = False
        self.modes = set()          # Usermodes attivi per quell'utente
        self.joined_channels = {}   # { channame : channel }
        
    def __str__(self):      
        return Connection.__str__(self) + ((self.registered and '[ident: %s]' % self.get_ident()) or '')

    def get_ident(self):
        if self.registered:
            return "%s!%s@%s" % (self.nick, self.username, self.host)
        else:
            raise client_errors.NotRegisteredException()

    def lineReceived(self, line):
        command = line.lower()
        # se il comando è nella forma:
        # "COMMAND someoptions :    ciaoaoo  oaaoao"
        # eseguiamo lo split solo sulla parte prima dei :
        colon_index = command.find(':')
        if colon_index != -1: # se ha trovato ':'
            commandSplit = command[ : colon_index].split()
            commandSplit.append(command[colon_index+1 : ]) # il +1 ci elimina i :
        else:
            commandSplit = command.split()
        # chiamiamo il relativo comando in irc_commands
        irc_commands.get_command(commandSplit[0])(self, commandSplit)
        self.print_log("|M| %s: %s" % (self, command.strip()))
    
    def send_line(self, line):
        Connection.sendLine(self, line)
    
    def send_reply(self, reply, *args_reply):
        msg = irc_replies.dict[reply][1](*args_reply)
        id_msg = irc_replies.dict[reply][0]
        reply = ':%s %s %s %s' % (self.server_host, id_msg, self.nick, msg)
        Connection.sendLine(self, reply)
        return msg
    
    def quit(self, quit_msg):
        for channel in self.joined_channels.values():
            channel.relay(self, ":%s QUIT :%s" % (self.get_ident(), quit_msg))
            del channel.clients[self]
        self.transport.loseConnection()
        
