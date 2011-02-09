# -*- coding: utf-8 -*-

import select
import sys
import socket

# Return codes:
ABEND = 1
GRACEFULLY = 0
USERQUIT = 2


class Server():

    #############################################
    # Classe Client: gestisce le comunicazioni con un singolo client remoto
    class Client():
        ID = 0                      # ID serve per generare un id per ogni client

        def __init__(self, sock):
            self.ID = Server.Client.ID
            self.sock = sock
            self.logged = False     # Fin quando il client non invia la sequenza [pass->]nick->user
            self.user = None
            self.nick = None
            self.realName = None
            self.password = None
            self.flags = []         # Flag attivi per quell'utente
            Server.Client.ID += 1


    #############################################
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_list = {}
        self.socket_list = [self.serverSock]

    #############################################
    def getConnectionCount(self):
        return len(self.client_list)

    #############################################
    def start(self):
        print "Starting Server"
        self.serverSock.bind( (self.host, self.port) )
        self.serverSock.listen(5)   # Indica quanti client possono al massimo rimanere in coda in attesa dell'accept

        while True:                 # ciclo di lettura e scrittura
        	# Con la select otteniamo la lista dei client che hanno dei dati da inviare (ready_to_read), che sono pronti a ricevere (ready_to_write), e quelli in errore (in_error)
            ready_to_read, ready_to_write, in_error = select.select(self.socket_list, [], self.socket_list) # Il parametro di timeout omesso rende la select bloccante, sarebbe cpukill
            #Iteriamo attraverso tutti i client che hanno dati da inviare (quindi il server li deve ricevere)
            for sock in ready_to_read:
                if sock == self.serverSock:			# Se uno di questi socket è quello del server, significa che un nuovo client si è connesso
                    clientSock = self.serverSock.accept()[0]	# Accettiamo il nuovo client
                    print " - new client accepted"
                    self.client_list[clientSock] = Server.Client(clientSock)	# Lo aggiungiamo alle nostre liste
                    self.socket_list.append(clientSock)
                    print '------ connection count: %s ------' % self.getConnectionCount()
                else:								# Altrimenti, uno dei client ha dati da inviare
                    try:
                        data = sock.recv(256)		# riceviamo questi dati
                        if not data: raise			# Se non abbiamo ricevuto dati, alziamo un'eccezione

                        client = self.client_list[sock]
                        if not client.logged:           # se il client non si è ancora loggato nella rete
                            #elaboriamo pass/nick/user
                            if data[:4].lower() == "pass":
                                if not client.password and not client.nick:
                                    client.password = data[4:]  # legge password
                                else:
                                    sock.send(" -E- Password già inviata o inviata dopo un nick ---")                       # ovviamente da mettere secondo lo standard
                            elif data[:4].lower() == "nick":
                                if not client.nick:
                                    client.nick = data[4:]      # legge nick
                                else:
                                    sock.send(" -E- Nick già inviato ---")                                                  # ovviamente da mettere secondo lo standard
                            elif data[:4].lower() == "user":
                                if not client.user and (client.nick or client.password):
                                    # legge e elabora stringa user
                                else:
                                    sock.send(" -E- User già inviato o non è stato inviato prima nick o password ---")      # ovviamente da mettere secondo lo standard
                            else:
                                sock.send(" -E- Comando non valido ---")       # ovviamente da mettere secondo lo standard
                        else
                            # elaboriamo i comandi normali
                            print "[%s] %s" % (self.client_list[sock].getID(), data),
                            sock.send('Echo:  %s' % data)
                    except:							# Se non abbiamo ricevuto dati, il client si è sconnesso
                        print "Client disconnected"
                        sock.close()
                        self.socket_list.remove(sock)	# Lo rimuoviamo dalle lista
                        del self.client_list[sock]
                        print '------ connection count: %s ------' % self.getConnectionCount()

    #############################################
    def stop(self):
        print "Stopping Server"
        # chiudere tutte le socket
        for sock in self.socket_list:
            sock.close()
    
    #############################################
    def restart(self):
        print "Restarting Server"
        self.stop()
        self.__init__(self.host, self.port)
        self.start()
    
   
if __name__ == '__main__':
    if '--listen-outside' in sys.argv:
        srv = Server('', 6969) # Map either localhost and LAN 
    else:
        srv = Server('127.0.0.1', 6969) # Map in LAN

    try:
        print 'Server started...   '
        srv.start()
    except KeyboardInterrupt:	# Sollevata quando si preme CTRL+C
        srv.stop()
        print "Server aborted due to CTRL-C signal"
        sys.exit(USERQUIT)
    except SystemExit: # Viene sollevata alla chiamata di sys.exit()
        print "Server ended"
        sys.exit(GRACEFULLY)
    except Exception as ex:
        print "Server aborted due to exception: ", ex
        srv.stop()
        sys.exit(ABEND)

