import requests
# from urllib2 import Request, urlopen
from requests_jwt import JWTAuth
import json


playload = {
    'username': 'test',
    'password': 'test1234'
}
base_url = 'https://www.tourzan.com/api/v1/'
api_auth = base_url+'api-token-auth/'
chats = base_url+'tours/'

auth = requests.post(api_auth, playload)
auth = auth.json()
print(auth)

# auth = json.loads(requests.post(api_auth, json=playload).content)
payload = {'content-type': 'application/json'}

JWT = JWTAuth(auth['token'])
res = requests.get(chats, auth=JWT)
print (res.status_code) #returning 401 consistently