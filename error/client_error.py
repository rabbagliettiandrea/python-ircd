# -*- coding: utf-8 -*-

#############################################
# Classe NoDataException: raisata quando il client si disconnette
class NoDataException(Exception): 
            
    def __str__(self): # invocato automagicamente
        return repr(self)
    