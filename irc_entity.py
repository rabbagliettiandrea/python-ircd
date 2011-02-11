# -*- coding: utf-8 -*-


#############################################
# Classe Channel: gestisce tutte le informazioni su un canale
class Channel():
    
    def __init__(self, name):
        self.name = name
        self.topic = None
        self.flags = set()
        self.client_list = []
        self.owner = None
       
 
#############################################
# Classe Client: gestisce le comunicazioni con un singolo client remoto
class Client():
    ID = 0                      # ID serve per generare un id per ogni client

    def __init__(self, sock):
        self.ID = Client.ID
        self.sock = sock
        self.logged = False     # Fin quando il client non invia la sequenza [pass->]nick->user
        self.user = None
        self.nick = None
        self.realName = None
        self.password = None
        self.flags = set()         # Flag attivi per quell'utente
        Client.ID += 1
