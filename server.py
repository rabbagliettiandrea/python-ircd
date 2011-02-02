import select
import threading
import sys
import traceback
from socket import socket, gethostname, AF_INET, SOCK_STREAM


def start_multiserver(host, port):
    
    class Acceptor(threading.Thread):
        def __init__(self, serverSocket, accepted):
            threading.Thread.__init__(self)
            
            self.serverSocket = serverSocket
            self.accepted = accepted
            
            print 'Starting acceptor..   ',
            try:
                self.start()
                print 'OK'
            except Exception as ex:
                print traceback.print_exc(ex)
                sys.exit(1)
    
        def run(self):
            while True:
                sock, addr = self.serverSocket.accept()
                self.accepted.append(sock)
                
        
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind( (host, port) )
    serverSocket.listen(5)
    
    client_list = []
    acceptor = Acceptor(serverSocket, client_list)
    while True:
        if client_list:
            ready_to_read, ready_to_write, in_error = select.select(client_list, client_list, client_list)
            for client in ready_to_read:
                while True:
                    data = client.recv(1024)
                    print data,
                    if not data: break
                    client.send('Echo:  %s' % data)
                client.close()

                
            
if __name__ == '__main__':
    start_multiserver(gethostname(), 6969)
    