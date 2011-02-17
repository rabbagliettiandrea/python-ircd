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

#############################################
def handleClientException(srv, e, client):
    import client_error
    from util import log_exc
    try:
        raise(e)
    except client_error.NoDataException:
        log_exc('NoDataException: %s' % client, e)
        srv.disconnectClient(client)
    except client_error.ReplyException:
        log_exc('ReplyException: %s' % client, e)
        srv.disconnectClient(client)
    except:
        log_exc('ClientException: %s' % client, e)

