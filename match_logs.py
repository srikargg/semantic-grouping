import json
import numpy as np
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from get_token import get_access_token


print("Loading model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded!")

token = get_access_token()
headers = {"Authorization": f"Zoho-oauthtoken {token}"}

PORTAL_ID = "771456286"
PROJECT_ID = "1918757000000658005"

print("\nFetching all tasks from Zoho...")

all_tasks = []
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
        name = task.get("name", "").strip()
        if name and len(name) > 3:
            all_tasks.append({
                "task_id": str(task.get("id", "")),
                "task_name": name,
                "tasklist_id": str(task.get("tasklist", {}).get("id", "")),
                "tasklist_name": task.get("tasklist", {}).get("name", ""),
                "milestone_id": str(task.get("milestone", {}).get("id", ""))
            })
    
    page += 1

print(f"Total tasks loaded: {len(all_tasks)}")


print("\nEmbedding all task names...")
task_names = [t["task_name"] for t in all_tasks]
task_embeddings = model.encode(task_names)
print(f"Done! {len(task_names)} task embeddings created")


with open("embedded_logs.json", "r") as f:
    embedded_logs = json.load(f)

print(f"\nLoaded {len(embedded_logs)} embedded logs")


THRESHOLD = 0.5



results = []

for log in embedded_logs:
    note_embedding = np.array(log["embedding"]).reshape(1, -1)
    log_tasklist_id = log["tasklist_id"]
    

    tasklist_indices = [
        i for i, t in enumerate(all_tasks)
        if t["tasklist_id"] == log_tasklist_id
    ]
    

    if not tasklist_indices:
        tasklist_indices = list(range(len(all_tasks)))
        guardrail_level = "project"
    else:
        guardrail_level = "tasklist"
    

    filtered_embeddings = task_embeddings[tasklist_indices]
    filtered_tasks = [all_tasks[i] for i in tasklist_indices]
    

    scores = cosine_similarity(note_embedding, filtered_embeddings)[0]
    

    top_3_indices = scores.argsort()[::-1][:3]
    top_3_matches = []
    for idx in top_3_indices:
        top_3_matches.append({
            "task": filtered_tasks[idx]["task_name"],
            "score": round(float(scores[idx]), 4)
        })
    
    best_score = float(scores.max())
    best_task = filtered_tasks[scores.argmax()]["task_name"]
    

    if best_score >= THRESHOLD:
        matched_task = best_task
        match_status = "matched"
    else:
        matched_task = log["original_task_name"]
        match_status = "kept_original"
    
    results.append({
        "hours": log["hours"],
        "notes": log["notes"],
        "original_task": log["original_task_name"],
        "matched_task": matched_task,
        "match_status": match_status,
        "best_score": round(best_score, 4),
        "guardrail_level": guardrail_level,
        "top_3_matches": top_3_matches
    })


matched = [r for r in results if r["match_status"] == "matched"]
kept = [r for r in results if r["match_status"] == "kept_original"]

print(f"\n--- RESULTS SUMMARY ---")
print(f"Total logs processed: {len(results)}")
print(f"Successfully matched: {len(matched)}")
print(f"Kept original task: {len(kept)}")
print(f"Threshold used: {THRESHOLD}")

print(f"\n--- SAMPLE RESULTS ---")
for r in results[:5]:
    print(f"\nNote: {r['notes'][:60]}...")
    print(f"Original task: {r['original_task']}")
    print(f"Matched task: {r['matched_task']}")
    print(f"Score: {r['best_score']} | Status: {r['match_status']}")


with open("matched_logs.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nSaved {len(results)} results to matched_logs.json")