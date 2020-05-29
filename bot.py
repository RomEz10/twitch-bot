from irc import *
import draw_game
import databse
from chatter import Chatter
import creds
import twitch_api
import asyncio
import pickle
from pathlib import Path
import emote_guess_game
import base_pubsub
from helper_methods import parse_command


async def exe_command(command, username, chatter):
    print(command)
    commands = {  # using dict as switch case
        'draw': draw_game.game_command
    }
    if command[0] in commands:
        method = commands.get(command[0])
        arg = command[1]
        await method(arg, username, db, chatter)
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
        elif emote_guess.on_going is True:
            await emote_guess.check_answer(text, username, db, chatter)

server = 'irc.chat.twitch.tv'
creds_p = Path('creds.p')
if creds_p.is_file():
    print('its a file')
    creds_dict = pickle.load(open('creds.p', 'rb'))
    creds.oauth_user_token = creds_dict['oauth_user_token']
    creds.refresh_token = creds_dict['refresh_token']
    creds.refresh_timer = creds_dict['refresh_timer']
    creds.scopes = creds_dict['scopes']
irc = IRC()
channel = creds.channel
nickname = creds.nickname
auth = creds.auth
twitch_api.refresh_tokens()
pubsub_client = base_pubsub.BasePubsub()
connect = irc.connect(server, channel, nickname, auth)
send = irc.send(creds.channel, 'connected FeelsOkayMan')
asyncio.get_event_loop().run_until_complete(connect)
asyncio.get_event_loop().run_until_complete(send)
draw_game = draw_game.DrawGame(irc)
emote_guess = emote_guess_game.EmoteGuessGame(irc)
db = databse.DataBase
twitch_api.validate_token()
loop = asyncio.get_event_loop()
pubsub_scopes = ['whispers.' + str(416678221)]  # add more scopes as new list item
gather = asyncio.gather(listen_to_chat(), pubsub_client.open_pubsub(pubsub_scopes, emote_guess))
loop.run_until_complete(gather)
