import json
from sentence_transformers import SentenceTransformer


print("Loading model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded!")


with open("enriched_logs.json", "r") as f:
    enriched_logs = json.load(f)

print(f"Loaded {len(enriched_logs)} enriched logs")


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

useful_logs = [log for log in enriched_logs if is_useful(log["notes"])]
print(f"Filtered to {len(useful_logs)} useful logs")

notes = [log["notes"] for log in useful_logs]

print("Converting notes to vectors...")
embeddings = model.encode(notes)
print("Done!")


results = []
for i, log in enumerate(useful_logs):
    results.append({
        "hours": log["hours"],
        "notes": log["notes"],
        "owner": log.get("owner", "Unknown"),  # ADD THIS
        "original_task_id": log["original_task_id"],
        "original_task_name": log["original_task_name"],
        "tasklist_id": log["tasklist_id"],
        "tasklist_name": log["tasklist_name"],
        "milestone_id": log["milestone_id"],
        "milestone_name": log["milestone_name"],
        "embedding": embeddings[i].tolist()
    })

with open("embedded_logs.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nSaved {len(results)} embedded logs to embedded_logs.json")
print("\nSample:")
print(f"  Notes: {results[0]['notes']}")
print(f"  Task list: {results[0]['tasklist_name']}")
print(f"  Embedding length: {len(results[0]['embedding'])}")