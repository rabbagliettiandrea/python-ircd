# -*- coding: utf-8 -*-

from py_ircd.connection import Connection
from py_ircd.error import client_errors 
from py_ircd.utils import *
from py_ircd.const import irc_replies
from py_ircd import irc_commands
from py_ircd.const.regex import util_regex


class Client(Connection):

    def __init__(self):
        self.username = None
        self.nick = None
        self.realname = None
        self.password = None
        self.registered = False
        self.modes = set()          # Usermodes attivi per quell'utente
        self.joined_channels = {}   # { chan_name : channel }
        
    def __str__(self):      
        return Connection.__str__(self) + ((self.registered and '[ident: %s]' % self.get_ident()) or '')

    def get_ident(self):
        if self.registered:
            return "%s!%s@%s" % (self.nick, self.username, self.host)
        else:
            return 'none!none@none'

    def lineReceived(self, line):
        line = line.rstrip('\r')
        # se il comando è nella forma:
        # "COMMAND someoptions :    ciaoaoo  oaaoao"
        # eseguiamo lo split solo sulla parte prima dei :
        colon_index = line.find(':')
        if colon_index != -1:
            line = util_regex['subcommaspace'].sub(',', line[ : colon_index])+line[colon_index : ]
            lineSplit = line[ : colon_index].lower().split()
            lineSplit.append(line[colon_index+1 : ]) # il +1 ci elimina i :
        else:
            lineSplit = util_regex['subcommaspace'].sub(',', line).lower().split()
            
        command = irc_commands.get_command(lineSplit[0])
        try:
            command(self, lineSplit)
        except client_errors.UnknownCommandError as ex:
            print_warn("->  %s: %s" % (self, str(ex)))
        except client_errors.ClientError:
            pass
        print_log("|M| %s: %s" % (self, line.strip()))
    
    def send(self, string, *args):
        type = string[ :3]
        if type in ['RPL', 'ERR']:
            msg = irc_replies.dict[string][1](*args)
            id_msg = irc_replies.dict[string][0]
            to_send = ':%s %s %s %s' % (self.server_host, id_msg, self.nick, msg)
            Connection.sendLine(self, to_send)
            if type == 'ERR':
                if string == 'ERR_UNKNOWNCOMMAND':
                    raise client_errors.UnknownCommandError(msg)
                else:
                    raise client_errors.ClientError(msg)
        else:
            Connection.sendLine(self, string)
    
    def quit(self, quit_msg=None):
        for channel in self.joined_channels.values():
            channel.relay(self, ":%s QUIT :%s" % (self.get_ident(), quit_msg))
            del channel.clients[self]
        if self.transport.connected:
            self.transport.loseConnection()
        
