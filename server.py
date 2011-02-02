import select
import threading
import sys
import traceback
import socket
import signal


class HwIRCserver(threading.Thread):

    #############################################
    # Classe Acceptor: accetta le connessioni in entrata e le smista su vari Client
    class Acceptor(threading.Thread):
        def __init__(self, serverSocket, accepted_clients ):
            threading.Thread.__init__(self)
            self.connectedNum = 0                       # Numero di client connessi
            self.serverSocket = serverSocket            # Socket
            self.accepted_clients = accepted_clients
            self.running = True

            print 'Starting acceptor...   ',
            try:
                self.start()
                print 'OK'
            except Exception as ex:
                print traceback.print_exc(ex)
                sys.exit(1)

        def getNumConnected(self):
            return self.connectedNum

        def run(self):                                  # Funzione principale del thread, chiamata da .start()
            while True:                                 # Ciclo di accettazione
                sock, addr = self.serverSocket.accept() # Attende una connessione in entrata
                self.client = HwIRCserver.Client(sock)  # Crea un nuovo Client passandogli il socket su cui comunicare
                self.accepted_clients[sock] = self.client    # Lo aggiunge al dizionario dei Client connessi
                self.connectedNum += 1                  # Aumenta il numero di client connessi
        
        def stop(self):
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
        threading.Thread.__init__(self)

        self.host = host
        self.port = port

        print 'Starting Server...   ',
        try:
            self.start()
            print 'OK'
        except Exception as ex:
            print traceback.print_exc(ex)
            sys.exit(1)

    def __del__(self):
        stop()

    #############################################
    def run(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind( (self.host, self.port) )
        self.serverSocket.listen(5)              # Indica quanti client possono al massimo rimanere in coda in attesa dell'accept

        self.running = True
        self.client_list = {}
        self.acceptor = HwIRCserver.Acceptor(self.serverSocket, self.client_list)

        while self.running:                     # ciclo di lettura e scrittura
            sock_list = self.client_list.keys()
            if sock_list:
                ready_to_read, ready_to_write, in_error = select.select(sock_list, sock_list, sock_list)
                for sock in ready_to_read:
                    data = sock.recv(1024)
                    print "[%s] %s" % (self.client_list[sock].getID(), data),
                    if sock in ready_to_write:
                        try:
                            sock.send('Echo:  %s' % data)
                        except Exception as ex:
                            

    #############################################
    def stop(self):
        # chiudere tutte le socket.
        sock_list = self.client_list.keys()
        for sock in sock_list:
            sock.close()
        # Esco dal programma
        self.acceptor.stop()    # dico all'acceptor di fermarsi
        join(acceptor)          # attendo che sia veramente fermo
        self.running = False    # imposto per fermarmi anche io


if __name__ == '__main__':

    def segnaleUscita(signum, stack):
        print "Interrupt ricevuto (%s)" % signum
        srv1.stop()
        threading.join(srv1)
        print "Il server e' terminato per via di un interrupt"
        sys.exit(0)

    signal.signal(signal.SIGINT, segnaleUscita)
    srv1 = HwIRCserver(socket.gethostname(), 6969)
    threading.Thread.join(srv1)
    print "Il Server e' terminato dal main"
    sys.exit(0)






