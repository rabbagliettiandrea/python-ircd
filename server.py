# -*- coding: utf-8 -*-

import select
import sys
import socket

import error.client_error
import irc_regex

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
            # Con la select otteniamo la lista dei client che hanno dei dati da inviare (ready_to_read), 
            # che sono pronti a ricevere (ready_to_write), e quelli in errore (in_error)
            ready_to_read, ready_to_write, in_error = select.select(self.socket_list, [], []) # Il parametro di timeout omesso rende la select bloccante, sarebbe cpukill
            #Iteriamo attraverso tutti i client che hanno dati da inviare (quindi il server li deve ricevere)
            for sock in ready_to_read:
                if sock == self.serverSock:			            # Se uno di questi socket è quello del server, significa che un nuovo client si è connesso
                    clientSock = self.serverSock.accept()[0]    # Accettiamo il nuovo client
                    print "- new client accepted"
                    self.client_list[clientSock] = Server.Client(clientSock)	# Lo aggiungiamo alle nostre liste
                    self.socket_list.append(clientSock)
                    print '------ connection count: %s ------' % self.getConnectionCount()
                else:								# Altrimenti, uno dei client ha dati da inviare
                    try:
                        data = sock.recv(256)		# Riceviamo questi dati
                        if not data: 
                            raise error.client_error.NoDataException()			# Se non abbiamo ricevuto dati, solleviamo un'eccezione
                        client = self.client_list[sock]
                        if not client.logged:       # Se il client non si è ancora loggato nella rete
                            # Elaboriamo [pass/]nick/user
                            dataSplit = data.lower().strip().split() # split() suddivide la stringa in una lista d'istruzioni, strip() rimuove il newline finale
                            if dataSplit[0] == "pass": 
                                if not client.password and not client.nick:                          
                                    if irc_regex.getConnectionRegex()['pass'].match(dataSplit[1]):
                                        client.password = dataSplit[1]
                                        sock.send('OK\n')
                                    else:
                                        sock.send('Il formato della password è illegale\n')
                                else:
                                    sock.send("-E- Password già inviata o inviata dopo un nick ---\n")   # ovviamente da mettere secondo lo standard
                            elif dataSplit[0] == "nick":
                                if not client.nick:
                                    if irc_regex.getConnectionRegex()['nick'].match(dataSplit[1]):
                                        client.nick = dataSplit[1]
                                        sock.send('OK\n')
                                    else:
                                        sock.send('Il formato del nick è illegale\n')
                                else:
                                    sock.send(" -E- Nick già inviato ---")                              # ovviamente da mettere secondo lo standard
                            elif dataSplit[0] == "user":
                                if not client.user and client.nick:
                                    if len(dataSplit)>4 and irc_regex.getConnectionRegex()['user'].match(dataSplit[1]) and dataSplit[2] == '0' and dataSplit[3] == '*':
                                        # visto che realname può contenere spazi tramite la list comprehension otteniamo la lista contenente tutti i segmenti del realname
                                        realname = ' '.join([ segm for segm in dataSplit[4:] ]) # successivamente joiniamo questi segmenti insieme con ' '
                                        if irc_regex.getConnectionRegex()['realname'].match(realname):
                                            client.user = dataSplit[1]
                                            client.realname = realname
                                            client.logged = True
                                            client.flags.append(dataSplit[2])
                                            sock.send('OK\n')
                                    else:
                                        sock.send('Il formato dello user è illegale\n')
                                else:
                                    sock.send("-E- User già inviato o non è stato inviato prima nick ---\n")      # ovviamente da mettere secondo lo standard
                            else:
                                sock.send("-E- Comando non valido ---\n")       # ovviamente da mettere secondo lo standard
                        else:
                            # elaboriamo i comandi normali
                            print "[%s] %s" % (self.client_list[sock].ID, data),
                            sock.send('Echo:  %s' % data)
                    except Exception as e:							# Se non abbiamo ricevuto dati, il client si è sconnesso
                        print "Client disconnected:", e
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

