# -*- coding: utf-8 -*-

import re

command_regex = {
        # La password deve essere una stringa di un numero di caratteri compreso tra 5 e 32
        # e non può essere uguale al nick
        'pass'  :   re.compile('^[A-Za-z0-9]{5,32}$'),

        # nick minlung = 1, maxlung = 10
        # non può iniziare con un numero ma solo con caratteri alfabetici opp con ^ _
        'nick'  :   re.compile('^[\^A-Za-z_-][A-Za-z0-9_-]{0,19}$'),

        # user minlung = 1, maxlung = 20
        # e può contenere una qualsiasi sequenza alfanumerica più - e _
        'user'  :   re.compile('^([A-Za-z0-9-_]+){1,20}$'),

        # realname minlung = 1, maxlung = 40
        # e può contenere solo alfabetici e spazi
        'realname'  :   re.compile('^([\\\\A-Za-z0-9-_\s]+){1,40}$'),

        # channel name minlung = 1, maxlung = 20
        # any octet except NUL, BELL, CR, LF, " ", "," and ":"
        'chan_name'  :    re.compile('^[&#+!][^\s,:]{1,50}$'),
        
}

util_regex = {
        # utile per sostituire un comando del genere: 'JOIN #chan1, #chan2,   #chan3 ,#chan4
        # ad uno così formato: 'JOIN #chan1,#chan2,#chan3
        'subcommaspace'  :    re.compile('\s*,\s*')
              
}