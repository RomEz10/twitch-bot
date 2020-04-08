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
    print(response.content)
    token = response.json().get('access_token', 'non')
    print(token)
    refresh_token = response.json().get('refresh_token', 'non')
    timeout = response.json().get('expires_in', 0)
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
                            headers={'Authorization': 'Bearer ' + access_token[0]}).json()
    print('dude ' + str(response))
    username = response.get('data', 'none')
    if username != 'none':
        username = username[0].get('display_name', 'none')  # response is JSON with a list (with one item) in 'data' var
    print('username is: ' + str(username))
    return username


def get_id_from_username(username):
    # using twitch's api to get id from username
    response = requests.get('https://api.twitch.tv/helix/users?login=' + username,
                            headers={'Authorization': 'Bearer ' + access_token[0]}).json()
    print(response)
    user_id = response.get('data', 'none')
    if user_id != 'none':
        user_id = user_id[0].get('id', 'none')  # response is JSON with a list (with one item) in 'data' var
    print('userid is: ' + str(user_id))
    return user_id