import requests
import creds
# Based on https://dev.twitch.tv/docs/authentication/getting-tokens-oauth#oauth-client-credentials-flow
# returns a tuple including an access_token to be used while using twitch-api and time in seconds when it'll expire
# if authentication fails returns non as access token
clientid = creds.clientid
client_secret = creds.client_secret


def authorize():
    response = requests.post('https://id.twitch.tv/oauth2/token?client_id=' + clientid +
                             '&client_secret=' + client_secret +
                             '&grant_type=client_credentials')
    token = response.json().get('access_token', 'non')
    timeout = response.json().get('expires_in', 0)
    return token, timeout
