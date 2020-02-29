from irc import *


def parseCommand(msg):
    # separate command from additional argument
    print('space is found in ' + str(msg.find(' ')))
    if msg.find(' ') != -1:  # check if there are args
        command = msg[1:msg.find(' ')]  # splice the ! and the arg after the command
        arguments = msg[msg.find(' ') + 1:]  # get arg - arg is the word after the command
    else:
        command = msg[1:]  # splice the ! there are not args
        arguments = ''  # no args
    print('arg: ' + arguments + ' command: ' + command)
    return command, arguments

def draw():
    return 'draw'

def exeCommand(command):
    print(command)
    commands = {
        'draw': draw
    }
    commanda = commands.get(command[0])
    print(commanda())

channel = ''
server = 'irc.chat.twitch.tv'
nickname = ''
auth = ''
irc = IRC()
irc.connect(server, channel, nickname, auth)
irc.send(channel, 'connected FeelsOkayMan')
while 1:
    text = irc.get_text().decode('utf-8')
    print(text)
    msg = text[text.rfind(':')+1:-2] #parse the IRC string to get the message '-2' removes the \r\n in the end of a message
    print(msg)
    if  msg[:1] == '!': #if first char is !- than its a command
        command = parseCommand(msg)
        exeCommand(command)

    if "PRIVMSG" in text and channel in text and "hello" in text:
        irc.send(channel, "Hello!")
