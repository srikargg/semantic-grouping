import requests
import json
from get_token import get_access_token

token = get_access_token()

headers = {"Authorization": f"Zoho-oauthtoken {token}"}

url = "https://projectsapi.zoho.com/api/v3/portal/771456286/projects/1918757000000658005/timelogs"

params = {
    "view_type": "customdate",
    "start_date": "2024-01-01",
    "end_date": "2024-06-30",
    "module": '{"type":"task"}'
}

response = requests.get(url, headers=headers, params=params)
data = response.json()


GARBAGE_NOTES = [
    "status call",
    "status update call", 
    "idletime",
    "idle time",
    "-",
    ""
]

def is_useful(note):
    
    if not note or note.strip() == "":
        return False
    
    if len(note.strip()) < 10:
        return False
    
    if note.strip().lower() in GARBAGE_NOTES:
        return False
    return True


clean_logs = []

for day in data.get("time_logs", []):
    for log in day.get("log_details", []):
        notes = log.get("notes", "")
        hours = log.get("log_hour", "")
        
        
        if is_useful(notes):
            clean_logs.append({
                "hours": hours,
                "notes": notes.strip()
            })

print(f"Total logs before cleaning: counting...")
print(f"Total useful logs after cleaning: {len(clean_logs)}")
print("\nSample of clean notes:")
for log in clean_logs[:10]:
    print(f"Hours: {log['hours']} | Notes: {log['notes']}")


with open("clean_logs.json", "w") as f:
    json.dump(clean_logs, f, indent=2)

print(f"\nSaved {len(clean_logs)} clean logs to clean_logs.json")