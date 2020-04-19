import requests
import creds
from urllib.parse import urlencode, quote_plus
import pickle

# following this doc https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#oauth-client-credentials-flow

client_id = creds.client_id
client_secret = creds.client_secret


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
        if (token or refresh_token) == 'non':
            raise Exception('no token received')
        else:
            creds.whispers_token = token
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
            creds_dict = {'whispers_token': token, 'refresh_token': refresh_token, 'refresh_timer': int(timeout)}
            pickle.dump(creds_dict, open('creds.p', 'wb'))


def validate_token():
    # checking if oauth token still valid with twitch
    response = requests.get('https://id.twitch.tv/oauth2/validate',
                            headers={'Authorization': 'OAuth ' + creds.whispers_token})
    if response.status_code == 200:
        # if response is 200 token is valid
        timeout = response.json().get('expires_in', 0)
        if int(timeout) > 5000:
            timeout = int(timeout) - 2500
            # refresh a little bit before timer expires
        elif int(timeout) > 0:
            timeout = int(timeout) - 600
            # refresh a little bitter before timer expires
        else:
            timeout = 0
        creds.refresh_timer = int(timeout)
        creds_dict = {'whispers_token': creds.whispers_token, 'refresh_token': creds.refresh_token,
                      'refresh_timer': creds.refresh_timer}
        pickle.dump(creds_dict, open('creds.p', 'wb'))
        return True
    else:
        return False


def get_username_from_id(user_id):
    # using twitch's api to get username from id
    response = requests.get('https://api.twitch.tv/helix/users?id=' + user_id,
                            headers={'Authorization': 'Bearer ' + access_token[0]})
    if response.status_code != 200:
        raise Exception('Response not successful: ' + str(response.status_code))
    else:
        response = response.json()
        print('dude ' + str(response))
        username = response.get('data', 'none')
        if username != 'none':
            username = username[0].get('display_name', 'none')  # response is JSON with a list in 'data' var
        print('username is: ' + str(username))
        return username


def get_id_from_username(username):
    # using twitch's api to get id from username
    response = requests.get('https://api.twitch.tv/helix/users?login=' + username,
                            headers={'Authorization': 'Bearer ' + access_token[0]})
    if response.status_code != 200:
        raise Exception('Response not successful: ' + str(response.status_code))
    else:
        response = response.json()
        print(response)
        user_id = response.get('data', 'none')
        if user_id != 'none':
            user_id = user_id[0].get('id', 'none')  # response is JSON with a list (with one item) in 'data' var
        print('userid is: ' + str(user_id))
        return user_id


def get_bttv_emotes(username):
    # gets both channel shared and global emotes, inserting them into dict with 'shared_emotes' and 'global_emotes'
    # 'global_emotes' as keys
    # if list inside dict is empty http response wasn't with status_code 200. check with if <list>:

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
    return emotes


def get_ffz_emotes(username):
    # gets both channel emotes and global, inserting both into dict with 'channel_emotes' and 'global_emotes' as keys
    # gonna include response json
    # if list inside dict is empty http response wasn't with status_code 200. check with if <list>:

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
    return emotes


def get_twitch_emotes(username):
    # gets both channel emotes and global, inserting both into dict with 'channel_emotes' and 'global_emotes' as keys
    # gonna include response json
    # if list inside dict is empty http response wasn't with status_code 200. check with if <list>:

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
    global_emotes = []
    if response.status_code == 200:
        print('raw twitch global emotes: ' + str(response.json()))
        global_emotes = response.json().get('emoticon_sets').get('0')
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
    return emotes

