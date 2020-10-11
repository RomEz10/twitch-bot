import requests
import creds
from urllib.parse import urlencode, quote_plus
import pickle
import offline_lists
import asyncio

# following this doc https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#oauth-client-credentials-flow

client_id = creds.client_id
client_secret = creds.client_secret
ffz_emotes_cached = {}
bttv_emotes_cached = {}
twitch_emotes_cached = {}


def authorize():
    # authorizing the script with twitch-app secret token- need to utilize refresh_tokens()
    response = requests.post('https://id.twitch.tv/oauth2/token?client_id=' + client_id +
                             '&client_secret=' + client_secret +
                             '&grant_type=client_credentials')
    token = response.json().get('access_token', 'non')
    timeout = response.json().get('expires_in', 0)
    return token, timeout


access_token = authorize()


def refresh_tokens():
    # using refresh_token (token passed along with oauth token to get a new oauth token without re-authenticating
    params = {'grant_type': 'refresh_token', 'refresh_token': creds.refresh_token, 'client_id': client_id,
              'client_secret': client_secret}
    response = requests.post('https://id.twitch.tv/oauth2/token?' + urlencode(params, quote_via=quote_plus))
    if response.status_code != 200:
        raise Exception('Response not successful: ' + str(response.status_code))
    else:
        print(response.content)
        response = response.json()
        token = response.get('access_token', 'non')
        print(token)
        refresh_token = response.get('refresh_token', 'non')
        timeout = response.get('expires_in', 0)
        scopes = response.get('scope', [])
        if (token or refresh_token) == 'non':
            raise Exception('no token received')
        else:
            creds.scopes = scopes
            creds.oauth_user_token = token
            creds.refresh_token = refresh_token
            if int(timeout) > 5000:
                timeout = int(timeout) - 2500
                # refresh a little bit before timer expires
            elif int(timeout) > 0:
                timeout = int(timeout) - 600
                # refresh a little bitter before timer expires
            else:
                timeout = 0
            creds.refresh_timer = int(timeout)
            creds_dict = {'oauth_user_token': token, 'refresh_token': refresh_token, 'refresh_timer': int(timeout),
                          'scopes': scopes}
            pickle.dump(creds_dict, open('creds.p', 'wb'))


def validate_token():
    # checking if oauth token still valid with twitch
    response = requests.get('https://id.twitch.tv/oauth2/validate',
                            headers={'Authorization': 'OAuth ' + creds.oauth_user_token})
    if response.status_code == 200:
        # if response is 200 token is valid
        response = response.json()
        timeout = response.get('expires_in', 0)
        scopes = response.get('scopes', [])
        if int(timeout) > 5000:
            timeout = int(timeout) - 2500
            # refresh a little bit before timer expires
        elif int(timeout) > 0:
            timeout = int(timeout) - 600
            # refresh a little bitter before timer expires
        else:
            timeout = 0
        creds.refresh_timer = int(timeout)
        creds.scopes = scopes
        creds_dict = {'oauth_user_token': creds.oauth_user_token, 'refresh_token': creds.refresh_token,
                      'refresh_timer': creds.refresh_timer, 'scopes': creds.scopes}
        pickle.dump(creds_dict, open('creds.p', 'wb'))
        return True
    else:
        return False


def get_username_from_id(user_id):
    # using twitch's api to get username from id
    response = requests.get('https://api.twitch.tv/helix/users?id=' + str(user_id),
                            headers={'Authorization': 'Bearer ' + access_token[0], 'Client-ID': creds.client_id})
    if response.status_code != 200:
        raise Exception('Response not successful: ' + str(response.status_code))
    else:
        response = response.json()
        username = response.get('data', 'none')
        if username != 'none':
            username = username[0].get('login', 'none')  # response is JSON with a list in 'data' var
        print('username is: ' + str(username))
        return username


def get_username_from_id_bulk(user_ids):
    # using twitch's api to get username from id
    # splitting to requests of 100's because twitch limit
    user_names = []
    while len(user_ids) > 0:
        if len(user_ids) > 100:
            user_ids_request = user_ids[:100]
            user_ids = user_ids[100:]
        else:
            user_ids_request = user_ids
            user_ids = []
        url = 'https://api.twitch.tv/helix/users?'
        response = requests.get(url, params=user_ids_request,
                                headers={'Authorization': 'Bearer ' + access_token[0], 'Client-ID': creds.client_id})
        if response.status_code != 200:
            raise Exception('Response not successful: ' + str(response.status_code) + str(response.json()))
        else:
            response = response.json()
            data = response.get('data', 'none')
            if data != 'none':
                for user in data:
                    user_names.append(user.get('login', 'none'))  # response is JSON with a list in 'data' var
        print('usernames are: ' + str(user_names))
        return user_names


def get_id_from_username(username):
    # using twitch's api to get id from username
    # expects to get a dict with {'id': [int, int...]
    print('https://api.twitch.tv/helix/users?login=' + username + str(access_token[0]))
    response = requests.get('https://api.twitch.tv/helix/users?login=' + username,
                            headers={'Authorization': 'Bearer ' + access_token[0], 'Client-ID': creds.client_id})
    if response.status_code != 200:
        raise Exception('Response not successful: ' + str(response.status_code) + ' ' + str(response.json()))
    else:
        response = response.json()
        print(response)
        user_id = response.get('data', 'none')
        if user_id != 'none':
            user_id = user_id[0].get('id', 'none')  # response is JSON with a list (with one item) in 'data' var
        print('userid is: ' + str(user_id))
        return user_id


def get_id_from_username_bulk(user_names):
    # using twitch's api to get username from id
    # splitting to requests of 100's because twitch limit
    ids = []
    while len(user_names) > 0:
        if len(user_names) > 100:
            user_names_request = user_names[:100]
            user_names = user_names[100:]
        else:
            user_names_request = user_names
            user_names = []
        url = 'https://api.twitch.tv/helix/users?'
        response = requests.get(url, params=user_names_request,
                                headers={'Authorization': 'Bearer ' + access_token[0], 'Client-ID': creds.client_id})
        if response.status_code != 200:
            raise Exception('Response not successful: ' + str(response.status_code) + str(response.json()))
        else:
            response = response.json()
            data = response.get('data', 'none')
            if data != 'none':
                for user in data:
                    ids.append(user.get('id', 'none'))  # response is JSON with a list in 'data' var
        print('twitch ids are: ' + str(ids))
        return ids


def get_bttv_emotes(username):
    # gets both channel shared and global emotes, inserting them into dict with 'shared_emotes' and 'global_emotes'
    # 'global_emotes' as keys
    # if response code is not 200 something went wrong, currently don't care to figure out what went wrong

    # gonna include response json

    # getting channel + shared emotes
    response = requests.get('https://api.betterttv.net/3/cached/users/twitch/' + get_id_from_username(username))
    channel_emotes = []
    shared_emotes = []
    if response.status_code == 200:
        print('raw bttv channel emotes: ' + str(response.json()))
        response = response.json()
        channel_emotes = response.get('channelEmotes')
        shared_emotes = response.get('sharedEmotes')
    # getting global emotes
    global_emotes = []
    response = requests.get('https://api.betterttv.net/3/cached/emotes/global')
    if response.status_code == 200:
        print('raw bttv global emotes: ' + str(response.json()))
        global_emotes = response.json()
    # merging both into dict
    emotes_sets = [channel_emotes, shared_emotes, global_emotes]
    emotes_sets_names = ['channel_emotes', 'shared_emotes', 'global_emotes']
    emotes = dict()
    for i in range(0, len(emotes_sets)):
        # going through emotes sets
        emotes_array = []
        for emote in emotes_sets[i]:
            # in each emote set get only the name of the emote
            emote_name = emote.get('code')
            emotes_array.append(emote_name)
        emotes[emotes_sets_names[i]] = emotes_array
    bttv_emotes_cached[username] = emotes
    return emotes


def get_ffz_emotes(username):
    # gets both channel emotes and global, inserting both into dict with 'channel_emotes' and 'global_emotes' as keys
    # gonna include response json
    # if response code is not 200 something went wrong, currently don't care to figure out what went wrong

    # getting channel emotes:
    response = requests.get('https://api.frankerfacez.com/v1/room/' + username)
    channel_emotes = []
    if response.status_code == 200:
        print('raw ffz channel emotes: ' + str(response.json()))
        response = response.json()
        channel_emote_set_value = response.get('room').get('set')
        channel_emotes = response.get('sets').get(str(channel_emote_set_value)).get('emoticons')
    # getting global emotes:
    response = requests.get('https://api.frankerfacez.com/v1/set/global')
    global_emotes = []
    if response.status_code == 200:
        print('raw ffz global emotes: ' + str(response.json()))
        response = response.json()
        emotes_set_3 = response.get('sets').get('3').get('emoticons')
        emotes_set_4330 = response.get('sets').get('4330').get('emoticons')
        global_emotes = emotes_set_3 + emotes_set_4330
    # merging both into dict
    emotes_sets = [channel_emotes, global_emotes]
    emotes_sets_names = ['channel_emotes', 'global_emotes']
    emotes = dict()
    for i in range(0, len(emotes_sets)):
        # going through emotes sets
        emotes_array = []
        for emote in emotes_sets[i]:
            # in each emote set get only the name of the emote
            emote_name = emote.get('name')
            emotes_array.append(emote_name)
        emotes[emotes_sets_names[i]] = emotes_array
    ffz_emotes_cached[username] = emotes
    return emotes


def get_twitch_emotes(username):
    # gets both channel emotes and global, inserting both into dict with 'channel_emotes' and 'global_emotes' as keys
    # gonna include response json
    # if response code is not 200 something went wrong, currently don't care to figure out what went wrong

    # getting channel emotes:
    # not using official twitch api because they require emote_set id which cannot be obtained for channel id/name
    response = requests.get('https://api.twitchemotes.com/api/v4/channels/' + get_id_from_username(username))
    channel_emotes = []
    if response.status_code == 200:
        print('raw twitch channel emotes: ' + str(response.json()))
        channel_emotes = response.json().get('emotes')
    # getting global emotes:
    # using the older v5 api to get these because newer twitch api have this yet. emote_sets = 0 means global emotes
    response = requests.get('https://api.twitch.tv/kraken/chat/emoticon_images?emotesets=0',
                            headers={'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': creds.client_id})
    global_emotes = []  # unused but kept for consistency
    if response.status_code == 200:
        print('raw twitch global emotes: ' + str(response.json().get('emoticon_sets').get('0')))
        global_emotes = response.json().get('emoticon_sets').get('0')
        offline_lists.offline_twitch_global_emotes_list = global_emotes  # update global emotes offline list
    else:
        print(str(response.status_code))
        global_emotes = offline_lists.offline_twitch_global_emotes_list  # list contains global emotes if fetching fails
    # merging both into dict
    emotes_sets = [channel_emotes, global_emotes]
    emotes_sets_names = ['channel_emotes', 'global_emotes']
    emotes = dict()
    for i in range(0, len(emotes_sets)):
        # going through emotes sets
        emotes_array = []
        for emote in emotes_sets[i]:
            # in each emote set get only the name of the emote
            emote_name = emote.get('code')
            emotes_array.append(emote_name)
        emotes[emotes_sets_names[i]] = emotes_array
    twitch_emotes_cached[username] = emotes
    return emotes


def get_all_emotes(username):
    # getting all emotes this channel might have and returning it as a list
    # if its the first time running or some are not cached for some reason load it
    # TODO: add a filter. e.g if user only want twitch emotes and not 3rd party thing
    if username in ffz_emotes_cached:
        ffz_emotes = ffz_emotes_cached[username]
    else:
        ffz_emotes = get_ffz_emotes(username)
    if username in bttv_emotes_cached:
        bttv_emotes = bttv_emotes_cached[username]
    else:
        bttv_emotes = get_bttv_emotes(username)
    if username in twitch_emotes_cached:
        twitch_emotes = twitch_emotes_cached[username]
    else:
        twitch_emotes = get_twitch_emotes(username)
    all_emotes_dict = [ffz_emotes, bttv_emotes, twitch_emotes]
    all_emotes_list = []
    for emotes in all_emotes_dict:
        for emotes_set in emotes.keys():
            all_emotes_list += emotes.get(emotes_set)
    return all_emotes_list


def get_chatters(username):
    response = requests.get('https://tmi.twitch.tv/group/user/' + username + '/chatters')
    if response.status_code == 200:
        all_chatters = []
        chatters = response.json().get('chatters')
        for chatter_role in chatters.keys():
            all_chatters.append(chatters.get(chatter_role))


def refresh_emotes(username):
    # Refreshing cached emotes from all services
    get_bttv_emotes(username)
    get_ffz_emotes(username)
    get_twitch_emotes(username)


bot_in_channel = True


async def bot_joined_channel(username):
    # When the bot joins a channel it starts a timer to refresh emotes
    while bot_in_channel:
        refresh_emotes(username)
        await asyncio.sleep(600)
