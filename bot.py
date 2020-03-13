from irc import *
import requests
import draw_game
import threading
import databse
from chatter import Chatter
import creds
import twitch_api

draw_game = draw_game.DrawGame()
draw_timer = threading.Timer(30.0, draw_game.timer)  # thread that limits the draw game to 30 seconds by calling timer


def parse_command(msg):
    # separate command from additional argument
    print('space is found in ' + str(msg.find(' ')))  # DOES NOT SUPPORT TWO ARG RIGHT NOW
    if msg.find(' ') != -1:  # check if there are args
        command = msg[1:msg.find(' ')]  # splice the ! and the arg after the command
        arguments = msg[msg.find(' ') + 1:]  # get arg - arg is the word after the command
    else:
        command = msg[1:]  # splice the ! there are not args
        arguments = ''  # no args
    print('arg: ' + arguments + ' command: ' + command)
    return command, arguments


def exe_command(command, username):
    print(command)
    commands = {  # using dict as switch case
        'draw': draw_game.draw_command
    }
    method = commands.get(command[0])
    arg = command[1]
    method(arg, username, irc)


server = 'irc.chat.twitch.tv'

irc = IRC()
channel = creds.channel
nickname = creds.nickname
auth = creds.auth
irc.connect(server, channel, nickname, auth)
irc.send(creds.channel, 'connected FeelsOkayMan')
access_token = twitch_api.authorize()  # add a function to count the time to refresh token
db = databse.database

while 1:
    msg = irc.get_msg()
    text = msg[0]
    username = msg[1]
    user_id = twitch_api.get_id_from_username(username)
    chatter = Chatter(twitch_id=user_id, name=username, points=0, guesses=0)
    db.add(db, chatter)
    if text[:1] == '!':  # if first char is !- than its a command
        command = parse_command(text)
        exe_command(command, username)

