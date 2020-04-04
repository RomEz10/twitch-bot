import requests
import creds
from urllib.parse import urlencode, quote_plus
# following this doc https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#oauth-client-credentials-flow

clientid = creds.clientid
client_secret = creds.client_secret


def authorize():
    response = requests.post('https://id.twitch.tv/oauth2/token?client_id=' + clientid +
                             '&client_secret=' + client_secret +
                             '&grant_type=client_credentials')
    token = response.json().get('access_token', 'non')
    timeout = response.json().get('expires_in', 0)
    return token, timeout


access_token = authorize()


def refresh_token():
    params = {'grant_type': 'refresh_token', 'refresh_token': creds.refresh_token, 'client_id': clientid,
              'client_secret': client_secret}
    response = requests.post('https://id.twitch.tv/oauth2/token?' + urlencode(params, quote_via=quote_plus))
    print(response.content)
    token = response.json().get('access_token', 'non')
    print(token)
    refresh_token = response.json().get('refresh_token', 'non')
    if (token or refresh_token) == 'non':
        raise Exception('no token received')
    else:
        creds.whispers_token = token
        creds.refresh_token = refresh_token


def validate_token():
    response = requests.get('https://id.twitch.tv/oauth2/validate',
                            headers={'Authorization': 'OAuth ' + creds.whispers_token})
    print('in validate ' + str(response.status_code))
    if response.status_code == 200:
        return True
    else:
        return False


def get_username_from_id(user_id):
    response = requests.get('https://api.twitch.tv/helix/users?id=' + user_id,
                            headers={'Authorization': 'Bearer ' + access_token[0]}).json()
    print('dude ' + str(response))
    username = response.get('data', 'none')
    if username != 'none':
        username = username[0].get('display_name', 'none')  # response is JSON with a list (with one item) inside 'data' var
    print('username is: ' + str(username))
    return username


def get_id_from_username(username):
    response = requests.get('https://api.twitch.tv/helix/users?login=' + username,
                            headers={'Authorization': 'Bearer ' + access_token[0]}).json()
    print(response)
    user_id = response.get('data', 'none')
    if user_id != 'none':
        user_id = user_id[0].get('id', 'none')  # response is JSON with a list (with one item) inside 'data' var
    print('userid is: ' + str(user_id))
    return user_id