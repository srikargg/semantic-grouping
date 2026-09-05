import json
from collections import defaultdict


with open("matched_logs.json", "r") as f:
    matched_logs = json.load(f)

print(f"Loaded {len(matched_logs)} matched logs")


def time_to_minutes(time_str):
    parts = time_str.strip().split(":")
    if len(parts) != 2:
        return 0
    hours = int(parts[0])
    minutes = int(parts[1])
    return (hours * 60) + minutes


def minutes_to_time(total_minutes):
    hours = total_minutes // 60 
    minutes = total_minutes % 60 

    return f"{hours:02d}:{minutes:02d}"


groups = defaultdict(list)

for log in matched_logs:
    matched_task = log["matched_task"]
    groups[matched_task].append(log)

print(f"Found {len(groups)} unique matched tasks")


report = []

for task_name, logs in groups.items():
    total_minutes = sum(time_to_minutes(log["hours"]) for log in logs)
    
    total_time = minutes_to_time(total_minutes)
    
    owners = list(set(log["owner"] for log in logs))
    
    log_count = len(logs)
    
    matched_count = sum(1 for log in logs if log["match_status"] == "matched")
    kept_count = sum(1 for log in logs if log["match_status"] == "kept_original")
    
    report.append({
        "matched_task": task_name,
        "total_hours": total_time,
        "total_minutes": total_minutes,
        "log_count": log_count,
        "matched_count": matched_count,
        "kept_original_count": kept_count,
        "owners": owners
    })


report.sort(key=lambda x: x["total_minutes"], reverse=True)

print("\n--- AGGREGATION REPORT ---")
for item in report:
    print(f"\nTask: {item['matched_task']}")
    print(f"Total hours: {item['total_hours']}")
    print(f"Number of logs: {item['log_count']}")
    print(f"Owners: {', '.join(item['owners'])}")

with open("report.json", "w") as f:
    json.dump(report, f, indent=2)

print(f"\nSaved report to report.json")