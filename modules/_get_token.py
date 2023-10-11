import requests
import json

def _get_token(client_id, client_secret, base_url):
    token_url = base_url + 'as/token.oauth2'
    data = {
        "grant_type": "client_credentials",
        "scope": "connect.api.read connect.api.write",
    }
    response = requests.post(token_url, auth=(client_id, client_secret), data=data)
    token_json = response.json()
    token = token_json.get("access_token")
    return token