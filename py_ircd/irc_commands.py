# -*- coding: utf-8 -*-

from py_ircd.const import regex
from py_ircd.channel import Channel
from py_ircd.utils import print_warn

# Funzioni per gestire i comandi richiesti dal client

#############################################
def get_command(name):
    return globals().get('command_' + name, command_unknown)

#############################################
def command_unknown(client, commandSplit):
    reply_msg = client.send_reply('ERR_UNKNOWNCOMMAND', commandSplit[0])
    print_warn("->  %s: %s" % (client, reply_msg))
    
#############################################
def command_pass(client, commandSplit):
    if not client.password and not client.nick:
        if len(commandSplit)==2 and regex.connection_regex['pass'].match(commandSplit[1]):
            client.password = commandSplit[1]
        else:
            client.send_reply('ERR_NEEDMOREPARAMS', commandSplit[0])
    else:
        client.send_reply('ERR_ALREADYREGISTRED')

#############################################
def command_nick(client, commandSplit):
    if not client.nick:
        if len(commandSplit) == 2 and regex.connection_regex['nick'].match(commandSplit[1]):
            client.nick = commandSplit[1]
        else:
            client.send_line('-E- Il formato del nick è illegale')
    else:
        client.send_line("-E- Nick già inviato ---")

#############################################
def command_user(client, commandSplit):
    if not client.username and client.nick:  
        if len(commandSplit) > 4 and regex.connection_regex['user'].match(commandSplit[1]):
            # visto che realname può contenere spazi tramite la list comprehension otteniamo la lista contenente tutti i segmenti del realname
            realname = commandSplit[4] # successivamente joiniamo questi segmenti insieme con ' '

            if regex.connection_regex['realname'].match(realname):
                client.username = commandSplit[1]
                client.realname = realname
                for flag in {'4' : 'w', '8' : 'i', '12' : 'wi'}.get(commandSplit[2], ''):
                    client.modes.add(flag)
                
                client.registered = True
                client.send_reply('RPL_WELCOME', client.get_ident())
                
            else:
                client.send_line('-E- Il formato del realname è illegale')
        else:
            client.send_line('-E- Il formato dello user è illegale')
    else:
        client.send_line("-E- User già inviato o non è stato inviato prima nick")

#############################################
def command_join(client, commandSplit):
    chanName = commandSplit[1]
    if len(commandSplit) == 2 and regex.connection_regex['chanName'].match(chanName):
        if not chanName in Channel.channels:                   		# Crea il canale se non esiste
            Channel.channels[chanName] = Channel(chanName)
        
        channel = Channel.channels[chanName]
        
        if not client in channel.clients:		# Controlla che il client non sia gia' presente nel canale
            channel.add_client(client)	# Aggiungo il client nella lista di quel canale
            client.joined_channels[chanName] = channel # Aggiungo il canale alla lista di quel client
            join_succesful_msg = ":%s JOIN :%s" % (client.get_ident(), channel.name)
            client.send_line(join_succesful_msg)
            channel.relay(client, join_succesful_msg)
            if channel.topic:
                client.send_reply('RPL_TOPIC', channel.name, channel.topic)
            client.send_reply('RPL_NAMREPLY', channel.scope_flag, channel.name, channel.nicklist_to_string())
            client.send_reply('RPL_ENDOFNAMES', channel.name)
        else:
            client.send_line("-E- User già collegato in questo canale")
    else:
        client.send_line("-E- Invalid channel name")

#############################################
def command_privmsg(client, commandSplit):
    chanName = commandSplit[1]
    if chanName in client.joined_channels.keys():
        msg = commandSplit[2]
        if regex.connection_regex['privmsg'].match(msg):
            channel = Channel.channels[chanName]
            channel.relay(client, ":%s PRIVMSG %s :%s" % (client.get_ident(), channel.name, msg))
        else:
            client.send_line("-E- Invalid privmsg syntax")
    else:
        client.send_reply('ERR_NOSUCHNICK', chanName)

#############################################
def command_quit(client, commandSplit):
    msg = (len(commandSplit)>1 and commandSplit[1]) or "Client Quit"
    client.quit(msg)
