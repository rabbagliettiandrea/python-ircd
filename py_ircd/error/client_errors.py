# -*- coding: utf-8 -*-

class ClientException(Exception):
    pass

class NotRegisteredException(ClientException): 
    
    def __init__(self):
        self.message = self.__class__.__name__
    
    def __str__(self):
        return self.message