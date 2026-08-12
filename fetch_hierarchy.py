import requests
import json
from get_token import get_access_token

# ---- GET TOKEN ----
token = get_access_token()
headers = {"Authorization": f"Zoho-oauthtoken {token}"}

PORTAL_ID = "771456286"
PROJECT_ID = "1918757000000658005"

# ---- STEP 1: PULL ALL TASKS WITH PAGINATION ----
# Zoho only returns 100 tasks per page
# We loop through all pages until there are no more tasks
print("Fetching tasks with hierarchy info...")

task_lookup = {}
page = 1
first_page_tasks = []  # Saved for the debug print below

while True:
    url = f"https://projectsapi.zoho.com/api/v3/portal/{PORTAL_ID}/projects/{PROJECT_ID}/tasks"
    params = {
        "page": page,
        "per_page": 100
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    tasks = data.get("tasks", [])
    
    # Save first page for debug printing later
    if page == 1:
        first_page_tasks = tasks
    
    # If no tasks returned, we've gone through all pages
    if not tasks:
        print(f"No more tasks on page {page}, stopping")
        break
    
    print(f"Page {page}: found {len(tasks)} tasks")
    
    for task in tasks:
        task_id = str(task.get("id", ""))
        task_name = task.get("name", "")
        
        tasklist = task.get("tasklist", {})
        tasklist_id = str(tasklist.get("id", ""))
        tasklist_name = tasklist.get("name", "")
        
        milestone = task.get("milestone", {})
        milestone_id = str(milestone.get("id", ""))
        milestone_name = milestone.get("name", "")
        
        task_lookup[task_id] = {
            "task_name": task_name,
            "tasklist_id": tasklist_id,
            "tasklist_name": tasklist_name,
            "milestone_id": milestone_id,
            "milestone_name": milestone_name
        }
    
    # Move to next page
    page += 1

print(f"Total tasks fetched: {len(task_lookup)}")

# ---- DEBUG PRINTS ----
if first_page_tasks:
    print("\nFirst task raw fields:")
    print(first_page_tasks[0].keys())
    print("\nFull first task:")
    print(json.dumps(first_page_tasks[0], indent=2))

test_id = "1918757000005401215"
print(f"\nDoes task {test_id} exist in lookup? {test_id in task_lookup}")
print(f"Total tasks in lookup: {len(task_lookup)}")


# ---- STEP 2: PULL TIME LOGS ----
print("\nFetching time logs...")

logs_url = f"https://projectsapi.zoho.com/api/v3/portal/{PORTAL_ID}/projects/{PROJECT_ID}/timelogs"
params = {
    "view_type": "customdate",
    "start_date": "2024-01-01",
    "end_date": "2024-06-30",
    "module": '{"type":"task"}'
}

logs_response = requests.get(logs_url, headers=headers, params=params)
logs_data = logs_response.json()


# ---- STEP 3: JOIN LOGS WITH HIERARCHY INFO ----
enriched_logs = []

for day in logs_data.get("time_logs", []):
    for log in day.get("log_details", []):
        notes = log.get("notes", "").strip()
        hours = log.get("log_hour", "")
        
        module_detail = log.get("module_detail", {})
        original_task_id = str(module_detail.get("id", ""))
        original_task_name = module_detail.get("name", "")
        
        hierarchy = task_lookup.get(original_task_id, {})
        
        enriched_logs.append({
            "hours": hours,
            "notes": notes,
            "original_task_id": original_task_id,
            "original_task_name": original_task_name,
            "tasklist_id": hierarchy.get("tasklist_id", ""),
            "tasklist_name": hierarchy.get("tasklist_name", ""),
            "milestone_id": hierarchy.get("milestone_id", ""),
            "milestone_name": hierarchy.get("milestone_name", "")
        })

print(f"Enriched {len(enriched_logs)} logs with hierarchy info")


# ---- STEP 4: SAVE ----
with open("enriched_logs.json", "w") as f:
    json.dump(enriched_logs, f, indent=2)

print("\nSample log with hierarchy:")
if enriched_logs:
    sample = enriched_logs[0]
    print(f"  Notes: {sample['notes']}")
    print(f"  Original task: {sample['original_task_name']}")
    print(f"  Task list: {sample['tasklist_name']}")
    print(f"  Milestone: {sample['milestone_name']}")

print(f"\nSaved to enriched_logs.json")