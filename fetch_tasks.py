import requests
from get_token import get_access_token

token = get_access_token()


headers = {"Authorization": f"Zoho-oauthtoken {token}"}
url = "https://projectsapi.zoho.com/restapi/portal/771456286/projects/YOUR_PROJECT_ID/tasks/"

response = requests.get(url, headers=headers)
data = response.json()
print(data)