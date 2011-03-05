# -*- coding: utf-8 -*-

from hwup_ircd.const import irc_regex
from hwup_ircd.channel import Channel
from hwup_ircd.const import irc_replies
from hwup_ircd.utils import print_warn

# Funzioni per gestire i comandi richiesti dal client

#############################################
def get_command(name):
    return globals().get('command_' + name, command_unknown)

#############################################
def command_unknown(client, commandSplit, server=None):
    reply_msg = client.get_irc_reply('ERR_UNKNOWNCOMMAND', commandSplit[0])
    print_warn("--> %s: %s" % (client, reply_msg) )
    if client.registered:
        client.send_data(reply_msg)
    
#############################################
def command_pass(client, commandSplit, server=None):
    if not client.password and not client.nick:
        if len(commandSplit)==2 and irc_regex.connectionRegex['pass'].match(commandSplit[1]):
            client.password = commandSplit[1]
        else:
            client.send_data(client.get_irc_reply('ERR_NEEDMOREPARAMS', commandSplit[0]))
    else:
        client.send_data(client.get_irc_reply('ERR_ALREADYREGISTRED'))

#############################################
def command_nick(client, commandSplit, server=None):
    if not client.nick:
        if len(commandSplit) == 2 and irc_regex.connectionRegex['nick'].match(commandSplit[1]):
            client.nick = commandSplit[1]
        else:
            client.send_data('-E- Il formato del nick è illegale')
    else:
        client.send_data("-E- Nick già inviato ---")

#############################################
def command_user(client, commandSplit, server=None):
    if not client.username and client.nick:  
        if len(commandSplit) > 4 and irc_regex.connectionRegex['user'].match(commandSplit[1]):
            # visto che realname può contenere spazi tramite la list comprehension otteniamo la lista contenente tutti i segmenti del realname
            realname = ' '.join(commandSplit[4 : ]).strip(':') # successivamente joiniamo questi segmenti insieme con ' '

            if irc_regex.connectionRegex['realname'].match(realname):
                client.username = commandSplit[1]
                client.realname = realname
                for flag in {'4' : 'w', '8' : 'i', '12' : 'wi'}.get(commandSplit[2], ''):
                    client.modes.add(flag)
                client.send_data(client.get_irc_reply('RPL_WELCOME', client.get_ident()))
                client.registered = True
            else:
                client.send_data('-E- Il formato del realname è illegale')
        else:
            client.send_data('-E- Il formato dello user è illegale')
    else:
        client.send_data("-E- User già inviato o non è stato inviato prima nick")

#############################################
def command_join(client, commandSplit, server):
    chanName = commandSplit[1]
    if len(commandSplit) == 2 and irc_regex.connectionRegex['chanName'].match(chanName):
        if not chanName in server.channel_list:                   		# Crea il canale se non esiste
            server.channel_list[chanName] = Channel(chanName)
        
        channel = server.channel_list[chanName]
        
        if not client in channel.client_list:		# Controlla che il client non sia gia' presente nel canale
            channel.add_client(client)	# Aggiungo il client nella lista di quel canale
            client.channel_joined_list[chanName] = channel # Aggiungo il canale alla lista di quel client
            join_succesful_msg = ":%s JOIN :%s" % (client.get_ident(), channel.name)
            client.send_data(join_succesful_msg)
            channel.relay(client, join_succesful_msg)
            if channel.topic:
                client.send_data(client.get_irc_reply('RPL_TOPIC', channel.name, channel.topic))
            client.send_data(client.get_irc_reply('RPL_NAMREPLY', channel.scope_flag, channel.name, channel.nicklist_to_string()))
            client.send_data(client.get_irc_reply('RPL_ENDOFNAMES', channel.name))
        else:
            client.send_data("-E- User già collegato in questo canale")
    else:
        client.send_data("-E- Invalid channel name")

#############################################
def command_privmsg(client, commandSplit, server):
    chanName = commandSplit[1]
    if chanName in client.channel_joined_list.keys():
        if irc_regex.connectionRegex['privmsg'].match(commandSplit[2]):
            msg = ' '.join(commandSplit[2:]).lstrip(':')
            channel = server.channel_list[chanName]
            channel.relay(client, ":%s PRIVMSG %s :%s" % (client.get_ident(), channel.name, msg))
        else:
            client.send_data("-E- Invalid privmsg syntax")
    else:
        client.send_data("-E- Invalid channel name")

#############################################
def command_quit(client, commandSplit, server):
    if len(commandSplit) > 1:
        quit_msg = ' '.join(commandSplit[1 : ]).lstrip(':')
    else: quit_msg = "Quit"
    server.disconnectClient(client, quit_msg)
