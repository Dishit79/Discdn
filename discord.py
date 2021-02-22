import requests
from __main__ import app


class Oauth(object):
    client_id=app.config['CLIENT_ID']
    client_secret=app.config['CLIENT_SECRET']
    redirect_uri=app.config['REDIRECT_URI']

    discord_login_url=f"https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=identify"
    discord_token_url="https://discord.com/api/oauth2/token"
    discord_api_url="https://discord.com/api"

    @staticmethod
    def discord_authenticate(code):
        data = {
        'client_id': Oauth.client_id,
        'client_secret':  Oauth.client_secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': Oauth.redirect_uri,
        'scope': 'identify'
        }

        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        access_token = requests.post(url=Oauth.discord_token_url, data=data, headers=headers)
        json = access_token.json()

        url = Oauth.discord_api_url+"/users/@me"

        headers = {
        'Authorization': 'Bearer {}'.format(json.get('access_token'))
        }

        user_data = requests.get(url=url,headers=headers)
        user_json = user_data.json()
        return user_json
