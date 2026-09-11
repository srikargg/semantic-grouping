import json
import csv
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
    total_actual_minutes = sum(time_to_minutes(log["hours"]) for log in logs)
    total_actual_time = minutes_to_time(total_actual_minutes)
    
    estimated_time = "00:00"
    for log in logs:
        est = log.get("estimated_hours", "00:00")
        if est and est != "00:00":
            estimated_time = est
            break
    
    estimated_minutes = time_to_minutes(estimated_time)
    
    if estimated_minutes == 0:
        variance_status = "NO ESTIMATE"
    else:
        variance_minutes = total_actual_minutes - estimated_minutes
        variance_time = minutes_to_time(abs(variance_minutes))
        
        if variance_minutes > 0:
            variance_status = f"OVER by {variance_time}"
        elif variance_minutes < 0:
            variance_status = f"UNDER by {variance_time}"
        else:
            variance_status = "EXACTLY ON ESTIMATE"
    
    owners = list(set(log["owner"] for log in logs))
    log_count = len(logs)
    matched_count = sum(1 for log in logs if log["match_status"] == "matched")
    kept_count = sum(1 for log in logs if log["match_status"] == "kept_original")
    
    report.append({
        "matched_task": task_name,
        "total_actual_hours": total_actual_time,
        "estimated_hours": estimated_time,
        "variance": variance_status,
        "log_count": log_count,
        "matched_count": matched_count,
        "kept_original_count": kept_count,
        "owners": owners
    })

report.sort(key=lambda x: time_to_minutes(x["total_actual_hours"]), reverse=True)

print("\n--- AGGREGATION REPORT ---")
for item in report:
    print(f"\nTask: {item['matched_task']}")
    print(f"Actual: {item['total_actual_hours']} | Estimated: {item['estimated_hours']}")
    print(f"Variance: {item['variance']}")
    print(f"Logs: {item['log_count']} | Owners: {', '.join(item['owners'])}")

with open("report.json", "w") as f:
    json.dump(report, f, indent=2)

print(f"\nSaved report to report.json")

with open("report.csv", "w", newline="") as f:
    
    fieldnames = [
        "matched_task",
        "total_actual_hours", 
        "estimated_hours",
        "variance",
        "log_count",
        "matched_count",
        "kept_original_count",
        "owners"
    ]
    

    writer = csv.DictWriter(f, fieldnames=fieldnames)
    
    writer.writeheader()
    
    for item in report:
        writer.writerow({
            "matched_task": item["matched_task"],
            "total_actual_hours": item["total_actual_hours"],
            "estimated_hours": item["estimated_hours"],
            "variance": item["variance"],
            "log_count": item["log_count"],
            "matched_count": item["matched_count"],
            "kept_original_count": item["kept_original_count"],
            "owners": ", ".join(item["owners"])
        })

print("Saved report to report.csv")