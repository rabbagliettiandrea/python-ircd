# -*- coding: utf-8 -*-

#############################################
# Super classe ClientException
class ClientException(Exception): 

    def __str__(self):
        return 'ClientException'


#############################################
# Classe NoDataException: lanciata quando il client si disconnette
class NoDataException(ClientException): 

    def __str__(self): # invocato automagicamente
        return super(), 'NoDataException:', repr(self)


#############################################
# Classe SendException: lanciata in caso di problemi nel socket.send
class SendException(ClientException): 

    def __str__(self): # invocato automagicamente
        return super(), 'SendException', repr(self)
