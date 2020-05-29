
import asyncio
import websockets
import json
import twitch_api
import creds
import socket
import threading
import helper_methods


class BasePubsub:

    request = {'type': 'LISTEN', 'data': {'topics': ''}}
    ws = ''
    alive = True

    async def open_pubsub(self, topics, emote_guess_game):
        self.request['data']['topics'] = topics
        self.request['data']['auth_token'] = creds.oauth_user_token
        asyncio.create_task(self.validate_tokens_loop())
        refresh_timer = threading.Timer(creds.refresh_timer, twitch_api.refresh_tokens)
        refresh_timer.start()
        print('timer is ' + str(creds.refresh_timer))
        while True:
            # outer loop restarted every time the connection fails
            try:
                if twitch_api.validate_token() is False:  # if token is not valid get a new one
                    print('not valid, refresh.')
                    twitch_api.refresh_tokens()
                refresh_timer.cancel()  # refresh timer is new- validate_token() refreshed the timeout, if its true we
                # have a new token, if its false we have a new timeout so either way we can start a new updated timer
                refresh_timer = threading.Timer(creds.refresh_timer, twitch_api.refresh_tokens)
                refresh_timer.start()
                self.request['data']['auth_token'] = creds.oauth_user_token
                async with websockets.connect('wss://pubsub-edge.twitch.tv') as self.ws:
                    await self.ws.send(json.dumps(self.request))
                    while True:
                        # conditions to break loop:
                        # * ERR_BADAUTH received from twitch, means token has expired
                        # * Exception ConnectionClosed raised by Webhooks
                        # * Websocket closed because token is not valid, closed by validate_tokens_loop()
                        #   raises Exception ConnectionClosedOk
                        # * Exception TimeoutError raised by wait_for, means refresh timer expired and we need a new key
                        #  outer loop never breaks
                        # listener loop
                        if self.request['data']['auth_token'] == creds.oauth_user_token:
                            try:
                                reply = await asyncio.wait_for(self.ws.recv(), timeout=creds.refresh_timer)
                                print(reply)
                                reply_dict = json.loads(reply)
                                if reply_dict.get('data'):  # If doesn't have data its not a reply we want to parse
                                    # "Typically, message is a JSON object that has been escaped and cast into a string"
                                    message = json.loads(reply_dict.get('data').get('message'))
                                    topic = reply_dict.get('data').get('topic')
                                    topic = topic[:topic.find('.')]
                                    # each if is for different topics
                                    if topic == 'whispers':
                                        if message.get('type') == 'whisper_received':
                                            # Some times you get type thread which is not documented.
                                            data = json.loads(message.get('data'))
                                            body = data.get('body')
                                            sent_from = data.get('from_id')
                                            if body[:1] == '!':
                                                command = helper_methods.parse_command(body)
                                                # initiate emote guess command
                                                if command[0] == 'guess':
                                                    print('command is guess')
                                                    await emote_guess_game.game_command(command[1], sent_from)

                                if 'error' in reply_dict and reply_dict['error'] == 'ERR_BADAUTH':
                                    twitch_api.refresh_tokens()
                                    self.request['data']['auth_token'] = creds.oauth_user_token
                                    break  # inner loop
                            except websockets.exceptions.ConnectionClosed:
                                await asyncio.sleep(2)
                                print('connection closed')
                                break  # inner loop
                                # do stuff with reply object
                            except asyncio.TimeoutError:
                                print('timed out')
                                break  # inner loop
                        else:
                            break  # break if token is different from creds.token - means it has refreshed
                if self.alive is False:
                    break
            except socket.gaierror:
                print('socket error')
                # log something
                continue
            except ConnectionRefusedError:
                print('refused')
                # log something else
                continue

    async def validate_tokens_loop(self):
        # if token not valid close connection
        while True:
            if twitch_api.validate_token() is False:
                twitch_api.refresh_tokens()
                self.request['data']['auth_token'] = creds.oauth_user_token
                if self.ws is not '':
                    await self.ws.close()
            await asyncio.sleep(1200)

    async def close_pubsub(self):
        await self.ws.close()
        self.alive = False
