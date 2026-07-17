import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

print("Loading model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded!")


titles = [
    "Sprint and project management calls",
    "Zoho tasks, cards, and time logging",
    "Client requirements, dashboards, and reporting discussions",
    "Technical and analytical work",
    "Testing, validation, and quality assurance",
    "Knowledge transfer and team training"
]


print("\nConverting titles to vectors...")
title_embeddings = model.encode(titles)
print(f"Done! {len(titles)} titles converted")


with open("embedded_logs.json", "r") as f:
    embedded_logs = json.load(f)

print(f"Loaded {len(embedded_logs)} embedded logs")


results = []

for log in embedded_logs:

    note_embedding = np.array(log["embedding"])
    

    note_embedding = note_embedding.reshape(1, -1)
    

    scores = cosine_similarity(note_embedding, title_embeddings)[0]
    
    best_match_index = scores.argmax()
    best_match_title = titles[best_match_index]
    best_match_score = scores[best_match_index]
    
    results.append({
        "hours": log["hours"],
        "notes": log["notes"],
        "matched_title": best_match_title,
        "similarity_score": round(float(best_match_score), 4)
    })

print("\n--- MATCHING RESULTS ---")
for r in results:
    print(f"\nNote: {r['notes']}")
    print(f"Matched to: {r['matched_title']}")
    print(f"Score: {r['similarity_score']}")

with open("matched_logs.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nSaved {len(results)} matched logs to matched_logs.json")