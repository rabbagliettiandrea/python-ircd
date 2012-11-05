# -*- coding: utf-8 -*-

class ClientError(Exception):
    pass

class UnknownCommandError(ClientError): 
    pass