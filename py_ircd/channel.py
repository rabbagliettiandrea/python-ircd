# -*- coding: utf-8 -*-

class Channel(object):
    
    class InChannelProperty(object):
        def __init__(self, client):
            self.client = client
            self.operator = False
            self.voice = False
        
        def __str__(self):
            prefix = (self.operator and '@') or (self.voice and '%') or ''
            return '%s%s' % (prefix, self.client.nick)
    
    channels = {} # { channame : channel_obj }
    
    def __init__(self, name):
        self.name = name
        self.topic = 'Topicozzo'
        self.flags = set()
        self.scope_flag = '='  # @ is used for secret channels, * for private channels, = for others (public channels)
        self.clients = {} # { client : in_channel_property }
        self.owner = None
        
    def add_client(self, client):
        self.clients[client] = Channel.InChannelProperty(client)

    def nicklist_to_string(self):
        nicklist = []
        for in_channel_property in self.clients.values():
            nicklist.append(str(in_channel_property))
        return ' '.join(nicklist)
    
    def relay(self, sender, line):
        for client in self.clients:
            if not client == sender:
                client.send_line(line)


            
