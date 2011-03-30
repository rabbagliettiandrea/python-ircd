# -*- coding: utf-8 -*-

from py_ircd.const.regex import command_regex
from py_ircd.channel import Channel


def get_command(name):
    return globals().get('command_' + name, command_unknown)

def command_unknown(client, lineSplit):
    client.send('ERR_UNKNOWNCOMMAND', lineSplit[0])

def command_pass(client, lineSplit):
    if len(lineSplit) == 1 or not command_regex['pass'].match(lineSplit[1]):
        client.send('ERR_NEEDMOREPARAMS', lineSplit[0])
    if client.registered:
        client.send('ERR_ALREADYREGISTRED')
    
    client.password = lineSplit[1]

def command_nick(client, lineSplit):
    if len(lineSplit) == 1:
        client.send('ERR_NONICKNAMEGIVEN')
    if 'r' in client.modes:
        client.send('ERR_RESTRICTED')
    if not command_regex['nick'].match(lineSplit[1]):
        client.send('ERR_ERRONEUSNICKNAME', lineSplit[1])
    
    client.nick = lineSplit[1]
    
def command_user(client, lineSplit):
    if client.registered or not client.nick:  
        client.send('ERR_ALREADYREGISTRED')
    if len(lineSplit) < 4 or not command_regex['user'].match(lineSplit[1]) \
                          or not command_regex['realname'].match(lineSplit[4]):
        client.send('ERR_NEEDMOREPARAMS', lineSplit[0])
    
    client.username = lineSplit[1]
    client.realname = lineSplit[4]
    for flag in {'4':'w', '8':'i', '12':'wi'}.get(lineSplit[2], ''):
        client.modes.add(flag)
    client.registered = True
    client.send('RPL_WELCOME', client.get_ident())

def command_join(client, lineSplit):
    tojoin_list = [chan_name for chan_name in lineSplit[1].split(',') if chan_name]

    if len(lineSplit) < 2:
        client.send('ERR_NEEDMOREPARAMS', lineSplit[0])
        
    for chan_name in tojoin_list:
        if not command_regex['chan_name'].match(chan_name):
            client.send('ERR_NOSUCHCHANNEL', chan_name)
        
        if not chan_name in Channel.channels:
            Channel.channels[chan_name] = channel = Channel(chan_name)
        else:
            channel = Channel.channels[chan_name]
        if not channel in client.joined_channels:
            channel.add_client(client)	# Aggiungo il client nella lista di quel canale
            client.joined_channels[chan_name] = channel # Aggiungo il canale alla lista di quel client
            join_succesful_msg = ":%s JOIN :%s" % (client.get_ident(), channel.name)
            client.send(join_succesful_msg)
            channel.relay(client, join_succesful_msg)
            if channel.topic:
                client.send('RPL_TOPIC', channel.name, channel.topic)
            client.send('RPL_NAMREPLY', channel.scope_flag, channel.name, channel.nicklist_to_string())
            client.send('RPL_ENDOFNAMES', channel.name)


def command_privmsg(client, lineSplit):
    if len(lineSplit) < 3:
        if ''.join(lineSplit).find(':') == -1:
            client.send('ERR_NOTEXTTOSEND')
        else:
            client.send('ERR_NORECIPIENT', 'PRIVMSG')
    
    target = lineSplit[1]
    msg = lineSplit[2]
    found = False
    if target[0] in '#&!+' and target in client.joined_channels.keys():
        found = True
        channel = Channel.channels[target]
        channel.relay(client, ":%s PRIVMSG %s :%s" % (client.get_ident(), channel.name, msg))
    else:
        for client in client.factory.client_list:
            if target == client.nick:
                found = True
                client.send(":%s PRIVMSG %s :%s" % (client.get_ident(), target, msg))
                break
    if not found:
        client.send('ERR_NOSUCHNICK', target)


def command_quit(client, lineSplit):
    msg = (len(lineSplit)>1 and lineSplit[1]) or "Client quit"
    client.quit(msg)
