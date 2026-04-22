from get_token import get_access_token

import requests

token = get_access_token()

headers = {
    "Authorization": f"Zoho-oauthtoken {token}"
}

url = "https://projectsapi.zoho.com/restapi/portals/"

response = requests.get(url, headers=headers)


data = response.json()
print(data)