
import asyncio
import websockets
import json
import twitch_api
import creds
import socket


async def listen_to_whispers():
    while True:
        # outer loop restarted every time the connection fails
        try:
            if twitch_api.validate_token() is False:
                print('not valid, refresh.')
                twitch_api.refresh_token()
            request = {'type': 'LISTEN', 'data': {'topics': ['whispers.' + str(416678221)],
                                                  'auth_token': creds.whispers_token}}
            async with websockets.connect('wss://pubsub-edge.twitch.tv') as ws:
                await ws.send(json.dumps(request))
                while True:
                    # listener loop
                    try:
                        reply = await asyncio.wait_for(ws.recv(), timeout=None)
                        print(reply)
                        reply_dict = json.JSONDecoder().decode(reply)
                        if 'error' in reply_dict and reply_dict['error'] == 'ERR_BADAUTH':
                            twitch_api.refresh_token()
                            request['data']['auth_token'] = creds.whispers_token
                            break
                    except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
                        try:
                            pong = await ws.ping()
                            await asyncio.wait_for(pong, timeout=10)
                            continue
                        except:
                            await asyncio.sleep(2)
                            break  # inner loop
                    # do stuff with reply object
        except socket.gaierror:
            # log something
            continue
        except ConnectionRefusedError:
            # log something else
            continue
