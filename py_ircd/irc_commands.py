# -*- coding: utf-8 -*-

from py_ircd.const.regex import command_regex
from py_ircd.channel import Channel


def get_command(name):
    return globals().get('command_'+name, command_unknown)


def command_unknown(client, lineSplit):
    client.send_n_raise('ERR_UNKNOWNCOMMAND', lineSplit[0])


def command_pass(client, lineSplit):
    if len(lineSplit) == 1 or not command_regex['pass'].match(lineSplit[1]):
        client.send_n_raise('ERR_NEEDMOREPARAMS', lineSplit[0])
    if client.registered:
        client.send_n_raise('ERR_ALREADYREGISTRED')
    
    client.password = lineSplit[1]


def command_nick(client, lineSplit):
    if len(lineSplit) == 1:
        client.send_n_raise('ERR_NONICKNAMEGIVEN')
    if 'r' in client.modes:
        client.send_n_raise('ERR_RESTRICTED')
    if not command_regex['nick'].match(lineSplit[1]):
        client.send_n_raise('ERR_ERRONEUSNICKNAME', lineSplit[1])
    
    client.nick = lineSplit[1]


def command_user(client, lineSplit):
    if client.registered or not client.nick:  
        client.send_n_raise('ERR_ALREADYREGISTRED')
    if len(lineSplit) < 4 or not command_regex['user'].match(lineSplit[1]) \
                          or not command_regex['realname'].match(lineSplit[4]):
        client.send_n_raise('ERR_NEEDMOREPARAMS', lineSplit[0])
    
    client.username = lineSplit[1]
    client.realname = lineSplit[4]
    for flag in {'4':'w', '8':'i', '12':'wi'}.get(lineSplit[2], ''):
        client.modes.add(flag)
    client.registered = True
    client.factory.clients[client.nick] = client
    client.send('RPL_WELCOME', client.get_ident())


def command_join(client, lineSplit):
    if len(lineSplit)<2:
        client.send_n_raise('ERR_NEEDMOREPARAMS', lineSplit[0])
    
    if lineSplit[1] == '0':
        for channel in client.joined_channels.values():
            client.part(channel)
        return
    
    tojoin_list = [chan_name for chan_name in lineSplit[1].split(',') if chan_name]
    key_list = len(lineSplit)>2 and lineSplit[2].split(',')
        
    for chan_name in tojoin_list:
        if not command_regex['chan_name'].match(chan_name):
            client.send_n_raise('ERR_NOSUCHCHANNEL', chan_name)
        
        if chan_name not in Channel.channels:
            Channel.channels[chan_name] = channel = Channel(chan_name)
        else:
            channel = Channel.channels[chan_name]
        
        if not channel in client.joined_channels:
            
            if 'k' in channel.modes:
                if key_list and len(key_list):
                    key = key_list.pop()
                    if channel.key != key:
                        client.send_n_raise('ERR_BADCHANNELKEY', chan_name)
                else:
                    client.send_n_raise('ERR_BADCHANNELKEY', chan_name)
                    
            channel.add_client(client)	# Aggiungo il client nella lista di quel canale
            client.joined_channels[chan_name] = channel # Aggiungo il canale alla lista di quel client
            join_succesful_msg = ":%s JOIN :%s" % (client.get_ident(), channel.name)
            client.send(join_succesful_msg)
            channel.relay(client, join_succesful_msg)
            if channel.topic:
                client.send('RPL_TOPIC', channel.name, channel.topic)
            client.send('RPL_NAMREPLY', channel.scope_flag, channel.name, channel.nicklist_to_string())
            client.send('RPL_ENDOFNAMES', channel.name)


def command_part(client, lineSplit):
    if len(lineSplit) < 2:
        client.send_n_raise('ERR_NEEDMOREPARAMS', lineSplit[0])
    
    part_msg = None
    if len(lineSplit) > 2:
        part_msg = lineSplit[2]
    
    topart_list = lineSplit[1].split(',')
    
    for chan_name in topart_list:
        if chan_name not in Channel.channels:
            client.send_n_raise('ERR_NOSUCHCHANNEL', chan_name)
        if chan_name not in client.joined_channels:
            client.send_n_raise('ERR_NOTONCHANNEL', chan_name)
        
        channel = client.joined_channels[chan_name]
        if part_msg:
            client.part(channel, part_msg)
        else:
            client.part(channel)
        
        
def command_privmsg(client, lineSplit):
    if len(lineSplit) < 3:
        if ':' not in ''.join(lineSplit[2:]):
            client.send_n_raise('ERR_NOTEXTTOSEND')
        else:
            client.send_n_raise('ERR_NORECIPIENT', 'PRIVMSG')
    
    target = lineSplit[1]
    msg = lineSplit[2]
    
    if target[0] in '#&!+':
        if target not in client.joined_channels:
            client.send_n_raise('ERR_CANNOTSENDTOCHAN', target)
        if target not in Channel.channels:
            client.send_n_raise('ERR_NOSUCHNICK', target)
        target_ob = Channel.channels[target]
        send_func = target_ob.relay
    else:
        if target not in client.factory.clients:
            client.send_n_raise('ERR_NOSUCHNICK', target)
        target_ob = client.factory.clients[target]
        send_func = target_ob.send
    
    send_func(target_ob, ":%s PRIVMSG %s :%s" % (client.get_ident(), target, msg))
        
        
def command_quit(client, lineSplit):
    msg = (len(lineSplit)>1 and lineSplit[1]) or "Client quit"
    client.quit(msg)
    
    
def command_mode(client, lineSplit):
    if len(lineSplit) < 2:
        client.send_n_raise('ERR_NEEDMOREPARAMS', lineSplit[0])
     
    target = lineSplit[1]  
        
    if len(lineSplit) == 2:
        if target[0] in '#&!+':
            if target not in Channel.channels:
                client.send_n_raise('ERR_NOSUCHNICK', target)
            channel = Channel.channels[target]
            client.send('RPL_CHANNELMODEIS', target, '+' + ''.join(channel.modes))
            client.send('RPL_CREATIONTIME', target, channel.creation_date)
        else:
            if target not in client.factory.clients:
                client.send_n_raise('ERR_NOSUCHNICK', target)
            if target != client.nick:
                client.send_n_raise('ERR_USERSDONTMATCH')
            client.send('RPL_UMODEIS', '+' + ''.join(client.factory.clients[target].modes)) 
    else:
        # FIN QUI E' TUTTO OK!
        if lineSplit[2][0] not in '+-':
            modes = '+' + lineSplit[2][:3] # [:3] prende solo i primi 3 mode
        else:
            modes = lineSplit[2][:4]

        if target[0] in '#&!+': # is a channel
            pass #TODO
    #        if modes[0] == '+':
    #            Channel.channels[target].modes.update(modes[1:])
    #        else:
    #            Channel.channels[target].modes.difference_update(modes[1:])
        else: # is an user
            if not set(modes[1:]).issubset('aiwrs'):
                client.send_n_raise('ERR_UMODEUNKNOWNFLAG')
            if client.nick != target:
                client.send_n_raise('ERR_USERSDONTMATCH')
    
            if 'a' in modes: # ignora richieste di +/-a (si può settare solo tramite /away)
                if len(modes[1:]) == 0:
                    return
                modes = modes.replace('a', '')

            if modes[0] == '+':
                client.modes.update(modes[1:])
            else:
                client.modes.difference_update(modes[1:])
            client.send(":%s MODE %s :%s" % (client.nick, client.nick, modes))