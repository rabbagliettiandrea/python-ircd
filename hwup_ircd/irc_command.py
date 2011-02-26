# -*- coding: utf-8 -*-

from hwup_ircd.const import irc_regex
from hwup_ircd import irc_entity
from hwup_ircd.const import irc_replies
from hwup_ircd.util import print_warn

# Funzioni per gestire i comandi richiesti dal client

#############################################
def command_unknown(client, commandSplit, server=None):
    reply_msg = irc_replies.dict['ERR_UNKNOWNCOMMAND'][1](commandSplit[0])
    
    print_warn("%s: %s" % (client, reply_msg) )
    client.reply(reply_msg)
    
    
#############################################
def command_pass(client, commandSplit, server=None):
    if not client.password and not client.nick:
        if len(commandSplit)==2 and irc_regex.connectionRegex['pass'].match(commandSplit[1]):
            client.password = commandSplit[1]
        else:
            client.reply(irc_replies.dict['ERR_NEEDMOREPARAMS'][1](commandSplit[0]))
    else:
        client.reply(irc_replies.dict['ERR_ALREADYREGISTRED'][1]())

#############################################
def command_nick(client, commandSplit, server=None):
    if not client.nick:
        if len(commandSplit) == 2 and irc_regex.connectionRegex['nick'].match(commandSplit[1]):
            client.nick = commandSplit[1]
        else:
            client.reply('-E- Il formato del nick è illegale')
    else:
        client.reply("-E- Nick già inviato ---")

#############################################
def command_user(client, commandSplit, server=None):
    if not client.user and client.nick:
        if len(commandSplit) > 4 and irc_regex.connectionRegex['user'].match(commandSplit[1]) and (commandSplit[2] in ('0', '4', '8', '12')) and commandSplit[3] == '*':
            # visto che realname può contenere spazi tramite la list comprehension otteniamo la lista contenente tutti i segmenti del realname
            realname = ' '.join(commandSplit[4 : ]).strip(':') # successivamente joiniamo questi segmenti insieme con ' '

            if irc_regex.connectionRegex['realname'].match(realname):
                client.user = commandSplit[1]
                client.realname = realname
                client.registered = True

                for flag in {'4' : 'w', '8' : 'i', '12' : 'wi'}.get(commandSplit[2], ''):
                    client.flags.add(flag)
                client.reply(irc_replies.dict['RPL_WELCOME'][1](client.nick, client.user, client.host))
            else:
                client.reply('-E- Il formato del realname è illegale')
        else:
            client.reply('-E- Il formato dello user è illegale')
    else:
        client.reply("-E- User già inviato o non è stato inviato prima nick")

#############################################
def command_join(client, commandSplit, server):
    chanName = commandSplit[1]
    if len(commandSplit) == 2 and irc_regex.connectionRegex['chanName'].match(chanName):
        if not chanName in server.channel_list:                   		# Crea il canale se non esiste
            server.channel_list[chanName] = irc_entity.Channel(chanName)

        if not client in server.channel_list[chanName].client_list:		# Controlla che il client non sia gia' presente nel canale
            server.channel_list[chanName].client_list.append(client)	# Aggiungo il client nella lista di quel canale
            client.joinChannel_list[chanName] = server.channel_list[chanName] # Aggiungo il canale alla lista di quel client
            client.reply("Ok, joined channel " + chanName)
        else:
            client.reply("-E- Client già collegato in questo canale")
    else:
        client.reply("-E- Invalid channel name")

#############################################
def command_privmsg(client, commandSplit, server):
    chanName = commandSplit[1]
    if chanName in client.joinChannel_list.keys():
        if irc_regex.connectionRegex['privmsg'].match(commandSplit[2]):
            server.channel_list[chanName].relay(client, ' '.join(commandSplit[2:]).strip(':') )
        else:
            client.reply("-E- Invalid privmsg syntax")
    else:
        client.reply("-E- Invalid channel name")

#############################################
def command_quit(client, commandSplit, server):
    # Avviso tutti i canali a cui è collegato il client che il client si scollega
    quitMsg = "Quit"
    if len(commandSplit) > 1:
        quitMsg = ' '.join(commandSplit[1 : ]).strip(':')
    # Scollego il client
    server.disconnectClient(client, quitMsg)

#############################################
def get(name):
    return globals().get('command_' + name, command_unknown)

