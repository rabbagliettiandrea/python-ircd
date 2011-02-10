# -*- coding: utf-8 -*-

import re

__regexConnection = {
        # La password deve essere una stringa di un numero di caratteri compreso tra 5 e 32 
        # e non può essere uguale al nick      
        'pass'  :   re.compile('^[A-Za-z0-9]{5,32}$'),

        # nick minlung = 1, maxlung = 10
        # non può iniziare con un numero ma solo con caratteri alfabetici opp con ^ _ 
        'nick'  :   re.compile('^[\^A-Za-z_-]{1}[A-Za-z0-9_-]{0,9}$'),

        # user minlung = 1, maxlung = 20
        # e può contenere una qualsiasi sequenza alfanumerica più - e _
        'user'  :   re.compile('^([A-Za-z0-9-_]+){1,20}$'),

        # realname minlung = 1, maxlung = 40
        # e può contenere solo alfabetici e spazi
        'realname'  :   re.compile('^([A-Za-z\s]+){1,40}$'), 
}

def getConnectionRegex():
    return __regexConnection

