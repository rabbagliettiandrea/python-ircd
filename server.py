# -*- coding: utf-8 -*-

import select
import threading
import sys
import traceback
import socket

# Return codes:
ABEND = 1
GRACEFULLY = 0
USERQUIT = 2


class HwIRCserver():

    #############################################
    # Classe Acceptor: accetta le connessioni in entrata e le smista su vari Client
    class Acceptor(threading.Thread):
        def __init__(self, serverSocket, accepted_sockets, accepted_clients, atLeastOneAccepted):
            threading.Thread.__init__(self)
            self.connectedNum = 0                       # Numero di client connessi
            self.serverSocket = serverSocket            # Socket
            self.accepted_sockets = accepted_sockets
            self.accepted_clients = accepted_clients
            self.running = True
            self.atLeastOneAccepted = atLeastOneAccepted
            
        def getNumConnected(self):
            return self.connectedNum

        def run(self):                                  # Funzione principale del thread, chiamata da .start()
            while self.running:                         # Ciclo di accettazione
                try:
                    sock, addr = self.serverSocket.accept() # Attende una connessione in entrata
                    client = HwIRCserver.Client(sock)  # Crea un nuovo Client passandogli il socket su cui comunicare
                    self.accepted_sockets.append(sock) # Aggiunge la socket accettata alla lista delle socket
                    self.accepted_clients[sock] = client    # Lo aggiunge al dizionario dei Client connessi
                    self.connectedNum += 1                  # Aumenta il numero di client connessi
                    self.atLeastOneAccepted.set()
                except Exception, e:
                    traceback.print_exc(e)
                    print 'ACCEPTOR IN. ERROR'
                    self.running = False
        
        def isRunning(self):
            return self.running
        
        def stop(self):
            print "Stopping Acceptor"
            self.running = False

    #############################################
    # Classe Client: gestisce le comunicazioni con un singolo client remoto
    class Client():
        ID = 0                          # ID serve per generare un id per ogni client

        def __init__(self, sock):
            self.__ID = HwIRCserver.Client.ID
            self.__sock = sock
            HwIRCserver.Client.ID += 1

        def getID(self):
            return self.__ID

        def getSock(self):
            return self.__sock

    #############################################
    def __init__(self, host, port):
        self.atLeastOneAccepted = threading.Event()
        self.host = host
        self.port = port
        self.client_list = {}
        self.socket_list = []
        self.running = False
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.acceptor = HwIRCserver.Acceptor(self.serverSocket, self.socket_list, self.client_list, self.atLeastOneAccepted)
        
    #############################################
    def start(self):
        self.serverSocket.bind( (self.host, self.port) )
        self.serverSocket.listen(5)              # Indica quanti client possono al massimo rimanere in coda in attesa dell'accept

        self.running = True
        
        print 'Starting Acceptor...   ',
        self.acceptor.start()
        if self.acceptor.isRunning():
            print 'OK'
        else:
            raise Exception('Acceptor: an exception is occured')
        
        self.atLeastOneAccepted.wait()         # sock_list non può essere una lista vuota, aspetta almeno un client (a quel punto acceptor setta l'event)
        while self.running:                    # ciclo di lettura e scrittura
            ready_to_read, ready_to_write, in_error = select.select(self.socket_list, [], self.socket_list) # il parametro di timeout omesso rende la select bloccante, sarebbe cpukill
            for sock in ready_to_read:
                try:
                    data = sock.recv(1024)
                    print "[%s] %s" % (self.client_list[sock].getID(), data),
                    sock.send('Echo:  %s' % data)
                except Exception as ex:
                    print "Errore nel sock.send(), fermo il client."
                    sock.close()

    #############################################
    def stop(self):
        print "Stopping Server"
        # chiudere tutte le socket.
        for sock in self.socket_list:
            sock.close()
        # Esco dal programma
        if self.acceptor.isAlive() and self.acceptor.isRunning():
            self.acceptor.stop()    # dico all'acceptor di fermarsi
            self.acceptor.join()    # attendo che sia veramente fermo
        self.running = False    # imposto per fermarmi anche io


if __name__ == '__main__':
    # srv = HwIRCserver(socket.gethostname(), 6969) # Map outside LAN
    srv = HwIRCserver('', 6969)
    
    try:
        print 'Server started...   '
        srv.start()
    except KeyboardInterrupt:
        srv.stop()
        print "Server aborted due to CTRL-C signal"
        sys.exit(USERQUIT)
    except Exception as exc:
        print "Server aborted due to exception: ", traceback.print_exc(exc)
        srv.stop()
        sys.exit(ABEND)
    else:
        print "Server ended"
        sys.exit(GRACEFULLY)
