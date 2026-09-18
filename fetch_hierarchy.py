import requests
import json
from get_token import get_access_token

token = get_access_token()
headers = {"Authorization": f"Zoho-oauthtoken {token}"}

PORTAL_ID = "771456286"

# ---- ALL 33 ACTIVE PROJECT IDs ----
PROJECT_IDS = [
    "1918757000014095003",
    "1918757000013919141",
    "1918757000013797043",
    "1918757000011643045",
    "1918757000010163111",
    "1918757000009851029",
    "1918757000009359081",
    "1918757000008931003",
    "1918757000008623257",
    "1918757000008192035",
    "1918757000008181009",
    "1918757000007702119",
    "1918757000007204067",
    "1918757000006840195",
    "1918757000006496096",
    "1918757000006371537",
    "1918757000005662375",
    "1918757000005341005",
    "1918757000004860863",
    "1918757000004634049",
    "1918757000004412216",
    "1918757000004412007",
    "1918757000004377027",
    "1918757000004377007",
    "1918757000003369145",
    "1918757000003339093",
    "1918757000002795005",
    "1918757000002687132",
    "1918757000000764025",
    "1918757000000685005",
    "1918757000000658005",
    "1918757000000556065",
    "1918757000000296005"
]

# ---- PULL TASKS FROM ALL PROJECTS ----
print("Fetching tasks from all projects...")
task_lookup = {}
total_tasks = 0

for PROJECT_ID in PROJECT_IDS:
    print(f"\nProject {PROJECT_ID}...")
    page = 1
    project_tasks = 0
    
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
                "project_id": PROJECT_ID,
                "tasklist_id": tasklist_id,
                "tasklist_name": tasklist_name,
                "milestone_id": milestone_id,
                "milestone_name": milestone_name,
                "estimated_hours": estimated_hours
            }
            project_tasks += 1
        
        page += 1
    
    total_tasks += project_tasks
    print(f"  Tasks: {project_tasks}")

print(f"\nTotal tasks across all projects: {total_tasks}")

# ---- PULL TIME LOGS FROM ALL PROJECTS ----
# ---- PULL TIME LOGS FROM ALL PROJECTS ----
print("\nFetching time logs from all projects...")
enriched_logs = []

# Two date ranges to cover the full year 2024
# Zoho only allows 6 months max per request so we split into two
date_ranges = [
    ("2024-01-01", "2024-06-30"),
    ("2024-07-01", "2024-12-31"),
]

for PROJECT_ID in PROJECT_IDS:
    print(f"Logs from project {PROJECT_ID}...")
    project_logs = 0
    
    # Loop through BOTH date ranges for each project
    # This is the key change — we now make 2 requests per project instead of 1
    for start_date, end_date in date_ranges:
        logs_url = f"https://projectsapi.zoho.com/api/v3/portal/{PORTAL_ID}/projects/{PROJECT_ID}/timelogs"
        params = {
            "view_type": "customdate",
            "start_date": start_date,
            "end_date": end_date,
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
                project_logs += 1
    
    if project_logs > 0:
        print(f"  Logs: {project_logs}")

print(f"\nTotal logs across all projects: {len(enriched_logs)}")

with open("enriched_logs.json", "w") as f:
    json.dump(enriched_logs, f, indent=2)

print(f"Saved {len(enriched_logs)} enriched logs to enriched_logs.json")