# -*- coding: utf-8 -*-


#############################################
# Super classe ClientException
class ClientException(Exception): 
    pass


#############################################
# Classe NoDataException: lanciata quando il client si disconnette
class NoDataException(ClientException): 
    pass


#############################################
# Classe ReplyException: lanciata in caso di problemi nel socket.send
class ReplyException(ClientException): 
    pass

