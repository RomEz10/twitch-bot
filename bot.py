from irc import *
import requests
from authorization import authorize
import draw_game
import threading
import databse
from chatter import Chatter
import creds

draw_game = draw_game.DrawGame()
draw_timer = threading.Timer(30.0, draw_game.timer)  # thread that limits the draw game to 30 seconds by calling timer


def parseCommand(msg):
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


def draw(arg):
    if draw_game.on_going is True:  # if a game is currently running
        if draw_game.answer(arg) is True:
            draw_timer.cancel()  # if answer was right cancel the timer and end the game
    if arg == 'start':  # command argument was start to initiate a game
        draw_game.on_going = True
        draw_game.start_game()  # generate draw object
        draw_timer.start()  # start the timeout timer
    print(draw_game.on_going)
    print(draw_game.draw)
    return 'draw'

def exeCommand(command):
    print(command)
    commands = {
        'draw': draw
    }
    commanda = commands.get(command[0])
    print(commanda(command[1]))


server = 'irc.chat.twitch.tv'

irc = IRC()
channel = creds.channel
nickname = creds.nickname
auth = creds.auth
irc.connect(server, channel, nickname, auth)
irc.send(creds.channel, 'connected FeelsOkayMan')
access_token = authorize()  # add a function to count the time to refresh token
db = databse.database

while 1:
    text = irc.get_text().decode('utf-8')
    print('raw: ' + text)
    msg = text[text.rfind(':')+1:-2]  # parse the IRC string to get the message -2 removes the \r\n in the end of a msg
    username = text[text.find(':')+1:text.find('!')]
    print(msg + ' sent by ' + username)
    response = requests.get('https://api.twitch.tv/helix/users?login=' + username,
                            headers={'Authorization': 'Bearer ' + access_token[0]}).json()
    print(response)
    user_id = response.get('data', 'none')
    if user_id != 'none':
        user_id = user_id[0].get('id', 'none')  # response is JSON with a list (with one item) inside 'data' var
    print('userid is: ' + str(user_id))
    chatter = Chatter(twitch_id=user_id, name=username, points=0, guesses=0)
    db.session.add(chatter)  # add a chatter to the database- only POC for now, gonna add chatters only if they get the correct answer
    db.session.commit()
    if msg[:1] == '!':  # if first char is !- than its a command
        command = parseCommand(msg)
        exeCommand(command)

