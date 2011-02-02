import select
import threading
import sys
import traceback
import socket


def start_multiserver(host, port):

    # Classe Acceptor: accetta le connessioni in entrata e le smista su vari Client
    class Acceptor(threading.Thread):
        def __init__(self, serverSocket, accepted_clients ):
            threading.Thread.__init__(self)
            
            self.connectedNum = 0                       # Numero di client connessi
            self.serverSocket = serverSocket            # Socket
            self.accepted_clients = accepted_clients
            
            print 'Starting acceptor..   ',
            try:
                self.start()
                print 'OK'
            except Exception as ex:
                print traceback.print_exc(ex)
                sys.exit(1)
    
        def getNumConnected(self):
            return self.connectedNum
        
        def run(self):                                  # Funzione principale del thread, chiamata da .start()
            while True:
                sock, addr = self.serverSocket.accept() # Attende una connessione in entrata
                client = Client(sock)                   # Crea un nuovo Client passandogli il socket su cui comunicare
                self.accepted_clients[sock] = client    # Lo aggiunge al dizionario dei Client connessi
                self.connectedNum += 1                  # Aumenta il numero di client connessi


    # Classe Client: gestisce le comunicazioni con un singolo client remoto
    class Client():
        ID = 0                          # ID serve per generare un id per ogni client
        
        def __init__(self, sock):
            self.__ID = Client.ID
            self.__sock = sock
            Client.ID += 1
        
        def getID(self):
            return self.__ID
        
        def getSock(self):
            return self.__sock
        
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind( (host, port) )
    serverSocket.listen(5)

    client_list = {}
    acceptor = Acceptor(serverSocket, client_list)

    while True:
        sock_list = client_list.keys()
    	if sock_list:
            ready_to_read, ready_to_write, in_error = select.select(sock_list, sock_list, sock_list)
            for sock in ready_to_read:
                data = sock.recv(1024)
                print "[%s] %s" % (client_list[sock].getID(), data),
                if sock in ready_to_write: sock.sendall('Echo:  %s' % data)




if __name__ == '__main__':
    start_multiserver(socket.gethostname(), 6969)
    
