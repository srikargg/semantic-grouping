import requests

from credentials import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN

print(f"DEBUG: Using Client ID: {CLIENT_ID[:10]}...") 
print(f"DEBUG: Using Refresh Token: {REFRESH_TOKEN[:10]}...")

TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"

def get_access_token():

    payload = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(TOKEN_URL, data=payload, headers=headers)
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



