# -*- coding: utf-8 -*-

import select
import socket

import irc_entity
import irc_regex
from util import log
from error import client_error


class Server():

    #############################################
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_list = {}
        self.socket_list = [self.serverSock]
        self.channel_list = {}

    #############################################
    def getConnectionCount(self):
        return len(self.client_list)

    #############################################
    def acceptNewClient(self):
        clientSock = self.serverSock.accept()[0]    # Accettiamo il nuovo client
        log("-L- new client accepted")
        self.client_list[clientSock] = irc_entity.Client(clientSock)	# Lo aggiungiamo alle nostre liste
        self.socket_list.append(clientSock)
        log('-L- - connection count: %s' % self.getConnectionCount())

    #############################################
    def notLoggedCommand_unknown(self, client, dataSplit):
        client.send("-E- Comando non valido\n")       # ovviamente da mettere secondo lo standard

    #############################################
    def notLoggedCommand_pass(self, client, dataSplit):
      if not client.password and not client.nick:
          if irc_regex.connectionRegex['pass'].match(dataSplit[1]):
              client.password = dataSplit[1]
              client.send('OK\n')
          else:
              client.send('-E- Il formato della password è illegale\n')
      else:
          client.send("-E- Password già inviata o inviata dopo un nick\n")   # ovviamente da mettere secondo lo standard

    #############################################
    def notLoggedCommand_nick(self, client, dataSplit):
      if not client.nick:
          if irc_regex.connectionRegex['nick'].match(dataSplit[1]):
              client.nick = dataSplit[1]
              client.send('OK\n')
          else:
              client.send('-E- Il formato del nick è illegale\n')
      else:
          client.send("-E- Nick già inviato ---\n")                              # ovviamente da mettere secondo lo standard

    #############################################
    def notLoggedCommand_user(self, client, dataSplit):
        if not client.user and client.nick:
            if len(dataSplit) > 4 and irc_regex.connectionRegex['user'].match(dataSplit[1]) and (dataSplit[2] in ('0', '4', '8', '12')):
                # visto che realname può contenere spazi tramite la list comprehension otteniamo la lista contenente tutti i segmenti del realname
                realname = (' '.join(segm for segm in dataSplit[4 : ])).strip(':') # successivamente joiniamo questi segmenti insieme con ' '
                if irc_regex.connectionRegex['realname'].match(realname):
                    client.user = dataSplit[1]
                    client.realname = realname
                    client.logged = True

                    for Ch in {'4' : 'w', '8' : 'i', '12' : 'wi'}.get(dataSplit[2], ''):
                        client.flags.add(Ch)

                    client.send('OK, logged in\n')
                else:
                    client.send('-E- Il formato del realname è illegale\n')
            else:
                client.send('-E- Il formato dello user è illegale\n')
        else:
            client.send("-E- User già inviato o non è stato inviato prima nick\n")      # ovviamente da mettere secondo lo standard

    #############################################
    def loggedCommand_unknown(self, client, dataSplit):
        pass # Nothing to do!

    #############################################
    def loggedCommand_join(self, client, dataSplit):
        chanName = dataSplit[1]
        if irc_regex.connectionRegex['chanName'].match(chanName):
            if not chanName in self.channel_list:                    # Crea il canale se non esiste
                self.channel_list[chanName] = irc_entity.Channel(chanName)
        
            if not client in self.channel_list[chanName].client_list:  # Controlla che il client non sia gia' presente nel canale
                self.channel_list[chanName].client_list.append(client)
            else:
                client.send("-E- Client già collegato in questo canale\n")
        else:
            client.send("-E- Invalid channel name\n")

    #############################################
    def disconnectClient(self, client):
        #log("-L- Client disconnected:", e)
        client.sock.close()

        self.socket_list.remove(sock)	# Lo rimuoviamo dalla lista
        del self.client_list[client.sock]
        log('-L- - connection count:', self.getConnectionCount())

    #############################################
    def handleException(self, e, client):
        pass # ancora non so

    #############################################
    def handleClientException(self, e, client):
        try:
            e
        except client_error.NoDataException, client_error.SendException:
            log(client, e)
            self.disconnectClient(client)


    #############################################
    def start(self):
        log("-L- Starting Server")
        self.serverSock.bind((self.host, self.port))
        self.serverSock.listen(5)   # Indica quanti client possono al massimo rimanere in coda in attesa dell'accept

        while True:                 # ciclo di lettura e scrittura
            # Con la select otteniamo la lista dei client che hanno dei dati da inviare (ready_to_read),
            # che sono pronti a ricevere (ready_to_write), e quelli in errore (in_error)
            ready_to_read, ready_to_write, in_error = select.select(self.socket_list, [], []) # Il parametro di timeout omesso rende la select bloccante, sarebbe cpukill
            #Iteriamo attraverso tutti i client che hanno dati da inviare (quindi il server li deve ricevere)
            for sock in ready_to_read:
                if sock == self.serverSock:			            # Se uno di questi socket è quello del server, significa che un nuovo client si � connesso
                    self.acceptNewClient()
                else:								# Altrimenti, uno dei client ha dati da inviare
                    try:
                        data = sock.recv(256)		# Riceviamo questi dati
                        if not data:
                            raise error.client_error.NoDataException()			# Se non abbiamo ricevuto dati, solleviamo un'eccezione
                        dataSplit = data.lower().strip().split() # split() suddivide la stringa in una lista d'istruzioni, strip() rimuove il newline finale

                        client = self.client_list[sock]
                        if not client.logged:       # Se il client non si è ancora loggato nella rete
                            # Elaboriamo [pass/]nick/user
                            selector = getattr(self, 'notLoggedCommand_' + dataSplit[0], self.notLoggedCommand_unknown)
                            selector(sock, client, dataSplit)
                        else:
                            # elaboriamo i comandi normali
                            log("-M- [%s] %s: %s" % (self.client_list[sock].ID, self.client_list[sock].nick, data),)
                            Selector = getattr(self, 'loggedCommand_' + dataSplit[0], self.loggedCommand_unknown)
                            Selector(sock, client, dataSplit)
                    except client_error.ClientException as e:
                        self.handleClientException(e, sock)
                    except Exception as e:
                        self.handleException(e, sock)

    #############################################
    def stop(self):
        log("-L- Stopping Server")
        # chiudere tutte le socket
        for sock in self.socket_list:
            sock.close()

    #############################################
    def restart(self):
        log("-L- Restarting Server")
        self.stop()
        self.__init__(self.host, self.port)
        self.start()
