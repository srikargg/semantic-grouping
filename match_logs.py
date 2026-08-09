import json
import numpy as np
import requests  
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from get_token import get_access_token 

print("Loading model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded")

token = get_access_token()
headers = {"Authorization": f"Zoho-oauthtoken {token}"}

print("\nFetching real tasks from Zoho...")
url = "https://projectsapi.zoho.com/api/v3/portal/771456286/projects/1918757000000658005/tasks"

response = requests.get(url, headers=headers)
data = response.json()
print("Keys:", data.keys() if isinstance(data, dict) else "its a list, length: " + str(len(data)))

titles = []
for task in data["tasks"]:
    if "name" in task:
        titles.append(task["name"])

print(f"Found {len(titles)} real tasks")
print("Sample tasks:")
for t in titles[:5]:
    print(f"  - {t}")


print("\nConverting titles to vectors...")
title_embeddings = model.encode(titles)
print(f"Done {len(titles)} titles converted")


with open("embedded_logs.json", "r") as f:
    embedded_logs = json.load(f)

print(f"Loaded {len(embedded_logs)} embedded logs")


results = []

for log in embedded_logs:
    note_embedding = np.array(log["embedding"])
    note_embedding = note_embedding.reshape(1, -1)
    scores = cosine_similarity(note_embedding, title_embeddings)[0]
    

    top_3_indices = scores.argsort()[::-1][:3]

    top_3_matches = []
    for idx in top_3_indices:
        top_3_matches.append({
            "task": titles[idx],
            "score": round(float(scores[idx]), 4)
        })

    results.append({
        "hours": log["hours"],
        "notes": log["notes"],
        "best_match": titles[scores.argmax()],
        "best_score": round(float(scores.max()), 4),
        "top_3_matches": top_3_matches
    })

print("\n--- MATCHING RESULTS ---")
for r in results:
    print(f"\nNote: {r['notes']}")
    print(f"Best match: {r['best_match']} (score: {r['best_score']})")

with open("matched_logs.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nSaved {len(results)} matched logs to matched_logs.json")