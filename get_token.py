import requests
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"

def get_access_token():

    params = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }

    response = requests.post(TOKEN_URL, data=params)
    data = response.json()

    if "access_token" in data:
        print("\nResponse:")
        print(data)
        return data["access_token"]
    else:
        print("\nError:")
        print(data)
        return None
    
if __name__ == "__main__":
    token = get_access_token()
    print("\nYour token:")
    print(token)



