# -*- coding: utf-8 -*-

import irc_regex
import irc_entity

import string

# Le funzioni per gestire i comandi richiesti dal client

#############################################
def command_unknown(client, dataSplit, server):
    client.reply("-E- Comando non valido\n")       # ovviamente da mettere secondo lo standard

#############################################
def command_pass(client, dataSplit, server):
    if not client.password and not client.nick:
        if irc_regex.connectionRegex['pass'].match(dataSplit[1]):
            client.password = dataSplit[1]
            client.reply('OK\n')
        else:
            client.reply('-E- Il formato della password è illegale\n')
    else:
        client.reply("-E- Password già inviata o inviata dopo un nick\n")

#############################################
def command_nick(client, dataSplit, server):
    if not client.nick:
        if irc_regex.connectionRegex['nick'].match(dataSplit[1]) and len(dataSplit) == 2:
            client.nick = dataSplit[1]
            client.reply('OK\n')
        else:
            client.reply('-E- Il formato del nick è illegale\n')
    else:
        client.reply("-E- Nick già inviato ---\n")

#############################################
def command_user(client, dataSplit, server):
    if not client.user and client.nick:
        if len(dataSplit) > 4 and irc_regex.connectionRegex['user'].match(dataSplit[1]) and (dataSplit[2] in ('0', '4', '8', '12')):
            # visto che realname può contenere spazi tramite la list comprehension otteniamo la lista contenente tutti i segmenti del realname
            #realname = (' '.join(segm for segm in dataSplit[4 : ])).strip(':') # successivamente joiniamo questi segmenti insieme con ' '
            realname = (string.join(dataSplit[4 : ], ' ')).strip(':') # successivamente joiniamo questi segmenti insieme con ' '

            if irc_regex.connectionRegex['realname'].match(realname):
                client.user = dataSplit[1]
                client.realname = realname
                client.logged = True

                for Ch in {'4' : 'w', '8' : 'i', '12' : 'wi'}.get(dataSplit[2], ''):
                    client.flags.add(Ch)

                client.reply('OK, logged in\n')
            else:
                client.reply('-E- Il formato del realname è illegale\n')
        else:
            client.reply('-E- Il formato dello user è illegale\n')
    else:
        client.reply("-E- User già inviato o non è stato inviato prima nick\n")

#############################################
def command_join(client, dataSplit, server):
    chanName = dataSplit[1]
    if irc_regex.connectionRegex['chanName'].match(chanName):
        if not chanName in server.channel_list:                   		# Crea il canale se non esiste
            server.channel_list[chanName] = irc_entity.Channel(chanName)

        if not client in server.channel_list[chanName].client_list:		# Controlla che il client non sia gia' presente nel canale
            server.channel_list[chanName].client_list.append(client)	# Aggiungo il client nella lista di quel canale
            client.join_channel_list[chanName] = server.channel_list[chanName] # Aggiungo il canale alla lista di quel client
            client.reply("Ok, joined channel " + chanName + "\n")
        else:
            client.reply("-E- Client già collegato in questo canale\n")
    else:
        client.reply("-E- Invalid channel name\n")

#############################################
def command_privmsg(client, dataSplit, server):
    chanName = dataSplit[1]						# ottengo il nome del canale
    if chanName in client.join_channel_list.keys():	# se esiste il canale
        client.join_channel_list[chanName].relay(client, string.join(dataSplit[2:], ' ').strip(':') )	# chiamo relay per inviare il messaggio a tutti i client del canale
    else:
        client.reply("-E- Invalid channel name\n")

#############################################
def command_quit(client, dataSplit, server):
    #Avviso tutti i canali a cui è collegato il client che il client si scollega
    quitMsg = "none"
    if len(dataSplit) >= 2:
        quitMsg = (string.join(dataSplit[1:], ' ')).strip(':')
    # Scollego il client
    server.disconnectClient(client, quitMsg)

#############################################
def get(name):
    return globals().get('command_' + name, command_unknown)

