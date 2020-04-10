
import asyncio
import websockets
import json
import twitch_api
import creds
import socket
import threading

request = {'type': 'LISTEN', 'data': {'topics': ['whispers.' + str(416678221)]}}
ws = ''


async def listen_to_whispers():
    request['data']['auth_token'] = creds.whispers_token
    asyncio.create_task(validate_tokens_loop())
    refresh_timer = threading.Timer(creds.refresh_timer, twitch_api.refresh_tokens)
    refresh_timer.start()
    print('timer is ' + str(creds.refresh_timer))
    while True:
        # outer loop restarted every time the connection fails
        try:
            if twitch_api.validate_token() is False:  # if token is not valid get a new one
                print('not valid, refresh.')
                twitch_api.refresh_tokens()
            refresh_timer.cancel()  # refresh timer is new- validate_token() refreshed the timeout, if its true we have
            # a new token, if its false we have a new timeout so either way we can start a new updated timer
            refresh_timer = threading.Timer(creds.refresh_timer, twitch_api.refresh_tokens)
            refresh_timer.start()
            request['data']['auth_token'] = creds.whispers_token
            global ws
            async with websockets.connect('wss://pubsub-edge.twitch.tv') as ws:
                await ws.send(json.dumps(request))
                while True:
                    # conditions to break loop:
                    # * ERR_BADAUTH received from twitch, means token has expired
                    # * Exception ConnectionClosed raised by Webhooks
                    # * Websocket closed because token is not valid, closed by validate_tokens_loop()
                    #   raises Exception ConnectionClosedOk
                    # * Exception TimeoutError raised by wait_for, means our refresh timer expired and we need a new key
                    #  outer loop never breaks
                    # listener loop
                    if request['data']['auth_token'] == creds.whispers_token:
                        try:
                            reply = await asyncio.wait_for(ws.recv(), timeout=creds.refresh_timer)
                            print(reply)
                            reply_dict = json.JSONDecoder().decode(reply)
                            if 'error' in reply_dict and reply_dict['error'] == 'ERR_BADAUTH':
                                twitch_api.refresh_tokens()
                                request['data']['auth_token'] = creds.whispers_token
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
        except socket.gaierror:
            print('socket error')
            # log something
            continue
        except ConnectionRefusedError:
            print('refused')
            # log something else
            continue


async def validate_tokens_loop():
    # if token not valid close connection
    while True:
        if twitch_api.validate_token() is False:
            twitch_api.refresh_tokens()
            request['data']['auth_token'] = creds.whispers_token
            if ws is not '':
                await ws.close()
        await asyncio.sleep(1200)
