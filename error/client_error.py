# -*- coding: utf-8 -*-


class NoDataException(Exception): # raisata quando il client si disconnette
            
    def __str__(self): # invocato automagicamente
        return repr(self)
    