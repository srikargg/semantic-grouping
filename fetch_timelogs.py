import requests
from get_token import get_access_token

token = get_access_token()

headers = {"Authorization": f"Zoho-oauthtoken {token}"}

url = "https://projectsapi.zoho.com/api/v3/portal/771456286/projects/1918757000010163111/timelogs"

params = {
    "view_type": "customdate",
    "start_date": "2025-01-01",
    "end_date": "2025-06-30",
    "module": '{"type":"task"}'
}

response = requests.get(url, headers=headers, params=params)
data = response.json()
print(data)