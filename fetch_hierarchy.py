import requests
import json
from get_token import get_access_token

token = get_access_token()
headers = {"Authorization": f"Zoho-oauthtoken {token}"}

PORTAL_ID = "771456286"
PROJECT_ID = "1918757000000658005"

print("Fetching tasks with hierarchy info...")

task_lookup = {}
page = 1

while True:
    url = f"https://projectsapi.zoho.com/api/v3/portal/{PORTAL_ID}/projects/{PROJECT_ID}/tasks"
    params = {"page": page, "per_page": 100}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    tasks = data.get("tasks", [])

    if not tasks:
        break

    for task in tasks:
        task_id = str(task.get("id", ""))
        task_name = task.get("name", "")

        tasklist = task.get("tasklist", {})
        tasklist_id = str(tasklist.get("id", ""))
        tasklist_name = tasklist.get("name", "")

        milestone = task.get("milestone", {})
        milestone_id = str(milestone.get("id", ""))
        milestone_name = milestone.get("name", "")

        owners_and_work = task.get("owners_and_work", {})
        estimated_hours = owners_and_work.get("total_work", "00:00")

        task_lookup[task_id] = {
            "task_name": task_name,
            "tasklist_id": tasklist_id,
            "tasklist_name": tasklist_name,
            "milestone_id": milestone_id,
            "milestone_name": milestone_name,
            "estimated_hours": estimated_hours
        }

    page += 1

print(f"Total tasks fetched: {len(task_lookup)}")

print("\nFetching time logs...")

enriched_logs = []

logs_url = f"https://projectsapi.zoho.com/api/v3/portal/{PORTAL_ID}/projects/{PROJECT_ID}/timelogs"
params = {
    "view_type": "customdate",
    "start_date": "2024-01-01",
    "end_date": "2024-06-30",
    "module": '{"type":"task"}'
}

logs_response = requests.get(logs_url, headers=headers, params=params)
logs_data = logs_response.json()

for day in logs_data.get("time_logs", []):
    for log in day.get("log_details", []):
        notes = log.get("notes", "").strip()
        hours = log.get("log_hour", "")

        owner = log.get("owner", {})
        owner_name = owner.get("name", "Unknown")

        module_detail = log.get("module_detail", {})
        original_task_id = str(module_detail.get("id", ""))
        original_task_name = module_detail.get("name", "")

        hierarchy = task_lookup.get(original_task_id, {})

        enriched_logs.append({
            "hours": hours,
            "notes": notes,
            "owner": owner_name,
            "project_id": PROJECT_ID,
            "original_task_id": original_task_id,
            "original_task_name": original_task_name,
            "estimated_hours": hierarchy.get("estimated_hours", "00:00"),
            "tasklist_id": hierarchy.get("tasklist_id", ""),
            "tasklist_name": hierarchy.get("tasklist_name", ""),
            "milestone_id": hierarchy.get("milestone_id", ""),
            "milestone_name": hierarchy.get("milestone_name", "")
        })

print(f"Total logs: {len(enriched_logs)}")

with open("enriched_logs.json", "w") as f:
    json.dump(enriched_logs, f, indent=2)

print(f"Saved {len(enriched_logs)} enriched logs to enriched_logs.json")