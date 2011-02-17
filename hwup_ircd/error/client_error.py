# -*- coding: utf-8 -*-

from hwup_ircd.util import log_exc


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


#############################################
def handleClientException(srv, e, client):
    try:
        raise(e)
    except ClientException:
        log_exc(e, client)

