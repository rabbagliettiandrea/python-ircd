# -*- coding: utf-8 -*-

import select
import socket

from hwup_ircd import irc_entity
from hwup_ircd import irc_command

from hwup_ircd.util import *
from hwup_ircd.error import client_error

class Server(object):
    
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
        print_log("new client accepted")
        self.client_list[clientSock] = irc_entity.Client(clientSock)	# Lo aggiungiamo alle nostre liste
        self.socket_list.append(clientSock)
        print_log('connection count: %s' % self.getConnectionCount())

    #############################################
    def disconnectClient(self, client, msg='Quit'):
        # Rimuovo il client dai canali 
        for chan in client.joinChannel_list.values():
            chan.client_list.remove(client)
            chan.relay(client, "Quitting (Message: " + msg + ")")

        print_log('Client disconnected (' + msg + ')')
        client.sock.close()

        self.socket_list.remove(client.sock)	# Lo rimuoviamo dalla lista
        del self.client_list[client.sock]
        print_log('connection count: %s' % self.getConnectionCount())

    #############################################
    def start(self):
        self.serverSock.bind((self.host, self.port))
        self.serverSock.listen(5)   # Indica quanti client possono al massimo rimanere in coda in attesa dell'accept (backlog)
        print_log('Server started')
        
        while True:                 # ciclo di lettura e scrittura
            # Con la select otteniamo la lista dei client che hanno dei dati da inviare (ready_to_read),
            # che sono pronti a ricevere (ready_to_write), e quelli in errore (in_error)
            ready_to_read, ready_to_write, in_error = select.select(self.socket_list, [], []) # Il parametro di timeout omesso rende la select bloccante, sarebbe cpukill
            #Iteriamo attraverso tutti i client che hanno dati da inviare (quindi il server li deve ricevere)
            for sock in ready_to_read:
                if sock == self.serverSock:			            # Se uno di questi socket è quello del server, significa che un nuovo client si è connesso
                    self.acceptNewClient()
                else:
                    client = self.client_list[sock]								
                    try:                            # Altrimenti, uno dei client ha dati da inviare
                        data = sock.recv(256)		# Riceviamo questi dati
                        if not data:
                            raise client_error.NoDataException()            # Se non abbiamo ricevuto dati, solleviamo un'eccezione
                        command_list = data.lower().split('\n')[:-1]   # il client può inviare più comandi alla volta divisi da '\n'
                        for command in command_list:
                            commandSplit = command.split()
                            irc_command.get(commandSplit[0])(client, commandSplit, self)
                            print_log("|M| %s: %s" % (client, command.strip()))
                    except client_error.ClientException as e:
                        print_exc(exc=e, msg=client, debug=False)
                        self.disconnectClient(client)
                    except Exception:
                        raise

    #############################################
    def stop(self):
        print_log("Stopping Server")
        for sock in self.socket_list:
            sock.close()

    #############################################
    def restart(self):
        print_log("Restarting Server")
        self.stop()
        self.__init__(self.host, self.port)
        self.start()
