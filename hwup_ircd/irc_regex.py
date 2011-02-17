# -*- coding: utf-8 -*-

import re

connectionRegex = {
        # La password deve essere una stringa di un numero di caratteri compreso tra 5 e 32
        # e non può essere uguale al nick
        'pass'  :   re.compile('^[A-Za-z0-9]{5,32}$'),

        # nick minlung = 1, maxlung = 10
        # non può iniziare con un numero ma solo con caratteri alfabetici opp con ^ _
        'nick'  :   re.compile('^[\b\^A-Za-z_-]{1}[A-Za-z0-9_-]{0,9}$'),

        # user minlung = 1, maxlung = 20
        # e può contenere una qualsiasi sequenza alfanumerica più - e _
        'user'  :   re.compile('^([A-Za-z0-9-_]+){1,20}$'),

        # realname minlung = 1, maxlung = 40
        # e può contenere solo alfabetici e spazi
        'realname'  :   re.compile('^([A-Za-z\s]+){1,40}$'),

        # channel name minlung = 1, maxlung = 20
        # any octet except NUL, BELL, CR, LF, " ", "," and ":"
        'chanName'  :    re.compile('^\#[^\b,:]{1,20}$'),
        
        # privmsg minlung = 1, maxlung = 200
        # deve iniziare necessariamente con i :
        'privmsg'  :   re.compile('^:.{1,200}$'),
}

