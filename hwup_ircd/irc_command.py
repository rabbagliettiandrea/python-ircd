# -*- coding: utf-8 -*-

from hwup_ircd.const import irc_regex
from hwup_ircd import irc_entity

# Funzioni per gestire i comandi richiesti dal client

#############################################
def command_unknown(client, dataSplit, server=None):
    client.reply("-E- Comando non valido")       # ovviamente da mettere secondo lo standard

#############################################
def command_pass(client, dataSplit, server=None):
    if not client.password and not client.nick:
        if len(dataSplit)==2 and irc_regex.connectionRegex['pass'].match(dataSplit[1]):
            client.password = dataSplit[1]
            client.reply('OK')
        else:
            client.reply('-E- Il formato della password è illegale')
    else:
        client.reply("-E- Password già inviata o inviata dopo un nick")

#############################################
def command_nick(client, dataSplit, server=None):
    if not client.nick:
        if len(dataSplit) == 2 and irc_regex.connectionRegex['nick'].match(dataSplit[1]):
            client.nick = dataSplit[1]
            client.reply('OK')
        else:
            client.reply('-E- Il formato del nick è illegale')
    else:
        client.reply("-E- Nick già inviato ---")

#############################################
def command_user(client, dataSplit, server=None):
    if not client.user and client.nick:
        if len(dataSplit) > 4 and irc_regex.connectionRegex['user'].match(dataSplit[1]) and (dataSplit[2] in ('0', '4', '8', '12')) and dataSplit[3] == '*':
            # visto che realname può contenere spazi tramite la list comprehension otteniamo la lista contenente tutti i segmenti del realname
            realname = ' '.join(dataSplit[4 : ]).strip(':') # successivamente joiniamo questi segmenti insieme con ' '

            if irc_regex.connectionRegex['realname'].match(realname):
                client.user = dataSplit[1]
                client.realname = realname
                client.logged = True

                for flag in {'4' : 'w', '8' : 'i', '12' : 'wi'}.get(dataSplit[2], ''):
                    client.flags.add(flag)

                client.reply('OK, logged in')
            else:
                client.reply('-E- Il formato del realname è illegale')
        else:
            client.reply('-E- Il formato dello user è illegale')
    else:
        client.reply("-E- User già inviato o non è stato inviato prima nick")

#############################################
def command_join(client, dataSplit, server):
    chanName = dataSplit[1]
    if len(dataSplit) == 2 and irc_regex.connectionRegex['chanName'].match(chanName):
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
def command_privmsg(client, dataSplit, server):
    chanName = dataSplit[1]
    if chanName in client.joinChannel_list.keys():
        if irc_regex.connectionRegex['privmsg'].match(dataSplit[2]):
            server.channel_list[chanName].relay(client, ' '.join(dataSplit[2:]).strip(':') )
        else:
            client.reply("-E- Invalid privmsg syntax")
    else:
        client.reply("-E- Invalid channel name")

#############################################
def command_quit(client, dataSplit, server):
    # Avviso tutti i canali a cui è collegato il client che il client si scollega
    quitMsg = "Quit"
    if len(dataSplit) > 1:
        quitMsg = ' '.join(dataSplit[1 : ]).strip(':')
    # Scollego il client
    server.disconnectClient(client, quitMsg)

#############################################
def get(name):
    return globals().get('command_' + name, command_unknown)

