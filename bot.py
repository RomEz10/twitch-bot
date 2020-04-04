from irc import *
import requests
import draw_game
import threading
import databse
from chatter import Chatter
import creds
import twitch_api
import whispers
import asyncio

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


async def exe_command(command, username, chatter):
    print(command)
    commands = {  # using dict as switch case
        'draw': draw_game.draw_command
    }
    if command in commands:
        method = commands.get(command[0])
        arg = command[1]
        await method(arg, username, irc, db, chatter)
    else:
        pass  # command doesn't exist


async def listen_to_chat():
    while True:
        msg = await irc.get_msg()
        text = msg[0]
        username = msg[1]
        user_id = twitch_api.get_id_from_username(username)
        chatter = Chatter(twitch_id=user_id, name=username, points=0, guesses=0)
        db.add(db, chatter)
        if text[:1] == '!':  # if first char is !- than its a command
            command = parse_command(text)
            await exe_command(command, username, chatter)

server = 'irc.chat.twitch.tv'

irc = IRC()
channel = creds.channel
nickname = creds.nickname
auth = creds.auth
connect = irc.connect(server, channel, nickname, auth)
send = irc.send(creds.channel, 'connected FeelsOkayMan')
asyncio.get_event_loop().run_until_complete(connect)
asyncio.get_event_loop().run_until_complete(send)
access_token = twitch_api.authorize()  # add a function to count the time to refresh token
db = databse.DataBase
twitch_api.validate_token()
loop = asyncio.get_event_loop()
gather = asyncio.gather(listen_to_chat(), whispers.listen_to_whispers())
loop.run_until_complete(gather)



