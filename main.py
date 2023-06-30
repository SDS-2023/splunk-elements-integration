import requests
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


def get_token(client_id, client_secret, token_url):
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)
    print("Token: ", token["access_token"])
    return token


def api_connect(token):
    api_endpoint = 'https://api.connect-stg.fsapi.com/whoami/v1/whoami'

    # Make a request to the API
    headers = {'Authorization': f'Bearer {token["access_token"]}'}
    response = requests.get(api_endpoint, headers=headers)

    # Process the API response
    if response.status_code == 200:
        data = response.json()
        print("Organizarion id: ", data['organizationId'])
        return data['organizationId']
    else:
        print('Token Request Failed:', response.text)


def get_events(token, organizationId, engine, timestamp):
    api_endpoint = 'https://api.connect-stg.fsapi.com/security-events/v1/security-events?'
    organizationId = "organizationId=" + organizationId
    engine = "&engine=" + engine
    timestamp = "&serverTimestampStart=" + timestamp
    full_endpoint = api_endpoint + organizationId + engine + timestamp
    print(full_endpoint)
    headers = {'Authorization': f'Bearer {token["access_token"]}'}
    response = requests.get(full_endpoint, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print('Token Request Failed:', response.text)


file = open("dane.txt", "r")
file = file.read().split("\n")
client_id = file[0]
client_secret = file[1]

print(client_id, client_secret)
token_url = 'https://api.connect-stg.fsapi.com/as/token.oauth2'  # Replace with the actual token URL
token = get_token(client_id, client_secret, token_url)

organization_id = api_connect(token)

# Fill in the desired timestamp and engine
timestamp = "2022-08-01T00:00:00Z"
engine = "edr"
get_events(token, organization_id, engine, timestamp)
