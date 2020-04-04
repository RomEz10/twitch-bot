
import asyncio
import websockets
import json
import twitch_api
import creds




async def initialize_whispers(self, user_id):
    self.websocket = ''
    self.user_id = user_id
    token = creds.whispers_token
    print('the token used in initialize_whispers is: ' + token)
    self.request = {'type': 'LISTEN', 'data': {'topics': ['whispers.' + str(user_id)],
                                                                                'auth_token': token}}
    print('request: ' + str(self.request))
    async with websockets.connect(self.uri) as self.websocket:
        print('why is it not')
        await self.websocket.send(json.dumps(self.request))

async def get_whisper(self):
    print('in get whisper')
    response = await self.websocket.recv()
    print('after response')
    print(json.JSONDecoder().decode(response))
    error = json.JSONDecoder().decode(response)['error']
    if error:
        if error == 'ERR_BADAUTH':  # Need to verify token validity with https://id.twitch.tv/oauth2/validate
            print('ERR_BADAUTH')
            if twitch_api.validate_token() is False:
                twitch_api.refresh_token()
                print('validate false')
                self.request['auth_token'] = creds.whispers_token
                await self.websocket.send(json.dumps(self.request))
                print('cmon babababaa')
                return await self.get_whisper()
            else:
                print('Token is valid auth still failed')
                await asyncio.new_event_loop().run_until_complete(self.get_whisper())
                #await self.initialize_whispers(self.user_id)
                #asyncio.get_event_loop().run_until_complete(self.initialize_whispers(self.user_id))
                self.request['data']['auth_token'] = creds.whispers_token
                print(self.request)
                return
        else:
            print('Error ' + error)
            return
    else:
        return json.JSONDecoder().decode(response)


async def listen_to_whispers():
    request = {'type': 'LISTEN', 'data': {'topics': ['whispers.' + str(416678221)],
                                               'auth_token': creds.whispers_token}}
    async with websockets.connect('wss://pubsub-edge.twitch.tv') as websocket:
        await websocket.send(json.dumps(request))
        replay = await websocket.recv()
        print(replay)
        replay_dict = json.JSONDecoder().decode(replay)
        if 'error' in replay_dict and replay_dict['error'] == 'ERR_BADAUTH':
            twitch_api.refresh_token()
            await listen_to_whispers()
            return
        else:
            while True:
                replay = await websocket.recv()
                replay_dict = json.JSONDecoder().decode(replay)
                if 'error' in replay_dict and replay_dict['error'] == 'ERR_BADAUTH':
                    twitch_api.refresh_token()
                    request['data']['auth_token'] = creds.whispers_token
                    async with websockets.connect('wss://pubsub-edge.twitch.tv') as websocket:
                        await websocket.send(json.dumps(request))
                        replay = await websocket.recv()
                        print(replay)
                else:
                    print(replay)
