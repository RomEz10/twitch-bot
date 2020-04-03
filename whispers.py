
import asyncio
import websockets
import json
import twitch_api


async def get_whisper(token, userid):
    uri = 'wss://pubsub-edge.twitch.tv'
    request = json.dumps({'type': 'LISTEN', 'data': {'topics': ['whispers.' + str(userid)],
                                                                            'auth_token': token}})
    async with websockets.connect(uri) as websocket:
        print(request)
        await websocket.send(request)
        response = await websocket.recv()
        error = json.JSONDecoder().decode(response)['error']
        if error:
            if error == 'ERR_BADAUTH':  # Need to verify token validity with https://id.twitch.tv/oauth2/validate
                print('ERR_BADAUTH ' + error)
                if twitch_api.validate_token() is False:
                    twitch_api.refresh_token()
            else:
                print(error)
        else:
            print(response)
            answer = await websocket.recv()
            return answer
