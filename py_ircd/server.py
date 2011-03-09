# -*- coding: utf-8 -*-

import select
import socket

from py_ircd import irc_commands
from py_ircd import client

from py_ircd.utils import *
from py_ircd.error import client_errors

class Server(object):
    
    #############################################
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._running = False
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setblocking(0)
        self.client_list = {}
        self.socket_list = [self.server_sock]
        self.channel_list = {}

    #############################################
    def getConnectionCount(self):
        return len(self.client_list)

    #############################################
    def acceptNewClient(self):
        clientSock = self.server_sock.accept()[0]    # Accettiamo il nuovo client
        clientSock.setblocking(0)
        print_log("new client accepted")
        self.client_list[clientSock] = client.Client(clientSock, self.host)	# Lo aggiungiamo alle nostre liste
        self.socket_list.append(clientSock)
        print_log('connection count: %s' % self.getConnectionCount())

    #############################################
    def disconnectClient(self, client, quit_msg):
        if client.registered:
            client.quit_irc(quit_msg)
        client.sock.close()
        self.socket_list.remove(client.sock)    # Lo rimuoviamo dalla lista
        del self.client_list[client.sock]
        print_log("%s disconnected: '%s'"% (client, quit_msg))
        print_log('connection count: %s' % self.getConnectionCount())

    #############################################
    def start(self):
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(5)   # Indica quanti client possono al massimo rimanere in coda in attesa dell'accept (backlog)
        self._running = True
        print_log('Server started')
        
        while self._running:                 # ciclo di lettura e scrittura
            # Con la select otteniamo la lista dei client che hanno dei dati da inviare (ready_to_read),
            # che sono pronti a ricevere (ready_to_write), e quelli in errore (in_error)
            ready_to_read, ready_to_write, in_error = select.select(self.socket_list, [], []) # Il parametro di timeout omesso rende la select bloccante, sarebbe cpukill
            
            #Iteriamo attraverso tutti i client che hanno dati da inviare (quindi il server li deve ricevere)
            for sock in ready_to_read:
                if sock == self.server_sock:			            # Se uno di questi socket è quello del server, significa che un nuovo client si è connesso
                    self.acceptNewClient()
                else:
                    client = self.client_list[sock]								
                    try:                            # Altrimenti, uno dei client ha dati da inviare
                        data = sock.recv(256)		# Riceviamo questi dati
                        if not data:
                            raise client_errors.NoDataException()            # Se non abbiamo ricevuto dati, solleviamo un'eccezione
                        command_list = data.lower().splitlines()   # il client può inviare più comandi alla volta divisi da '\n'
                        for command in command_list:
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
                            irc_commands.get_command(commandSplit[0])(client, commandSplit, self)
                            print_log("|M| %s: %s" % (client, command.strip()))
                    
                    except client_errors.ClientException as e:
                        print_exc(exc=e, msg=client)
                        self.disconnectClient(client, 'Connection interrupted')
                    except Exception:
                        raise

    #############################################        
    def stop(self):
        print_log("Stopping Server")
        self._running = False
#        closing_sock = socket.create_connection((self.host, self.port)) # per sbloccare l'eventuale accept
        to_close = self.socket_list[:]
        del self.socket_list[:]
        for sock in to_close:
            sock.close()

    #############################################
    def restart(self):
        print_log("Restarting Server")
        if not self._running:
            self.stop()
        self.__init__(self.host, self.port)
        self.start()

    #############################################
    def is_running(self):
        return self._running