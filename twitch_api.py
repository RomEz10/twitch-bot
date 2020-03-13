import requests
import creds

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
