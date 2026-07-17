import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ---- LOAD THE MODEL ----
# Same model as yesterday
# This time it won't download - it's already cached on your laptop
print("Loading model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded!")

# ---- DEFINE YOUR TITLES ----
# These are the categories YOU identified from reading the notes
# Left side of the comparison
titles = [
    "Sprint and project management calls",
    "Zoho tasks, cards, and time logging",
    "Client requirements, dashboards, and reporting discussions",
    "Technical and analytical work",
    "Testing, validation, and quality assurance",
    "Knowledge transfer and team training"
]

# ---- CONVERT TITLES TO VECTORS ----
# Same process as yesterday but for titles instead of notes
# Each title becomes a vector of 384 numbers
print("\nConverting titles to vectors...")
title_embeddings = model.encode(titles)
print(f"Done! {len(titles)} titles converted")

# ---- READ YOUR EMBEDDED LOGS ----
# Open the file we saved yesterday
# It has all 47 notes with their vectors already saved
with open("embedded_logs.json", "r") as f:
    embedded_logs = json.load(f)

print(f"Loaded {len(embedded_logs)} embedded logs")

# ---- COMPARE EACH LOG TO EACH TITLE ----
# This is the core of Day 13
# For each note we calculate cosine similarity against all 4 titles
# Then we pick the title with the highest score
results = []

for log in embedded_logs:
    # Get the note's vector - it's saved as a list so convert to numpy array
    # numpy is a math library - cosine_similarity needs numpy arrays not lists
    note_embedding = np.array(log["embedding"])
    
    # cosine_similarity needs 2D arrays so we reshape
    # -1 means "figure out this dimension automatically"
    note_embedding = note_embedding.reshape(1, -1)
    
    # Calculate similarity score against ALL titles at once
    # scores will be a list of 4 numbers - one per title
    scores = cosine_similarity(note_embedding, title_embeddings)[0]
    
    # Find which title had the highest score
    best_match_index = scores.argmax()
    best_match_title = titles[best_match_index]
    best_match_score = scores[best_match_index]
    
    # Save the result
    results.append({
        "hours": log["hours"],
        "notes": log["notes"],
        "matched_title": best_match_title,
        "similarity_score": round(float(best_match_score), 4)
    })

# ---- PRINT THE RESULTS ----
print("\n--- MATCHING RESULTS ---")
for r in results:
    print(f"\nNote: {r['notes']}")
    print(f"Matched to: {r['matched_title']}")
    print(f"Score: {r['similarity_score']}")

# ---- SAVE RESULTS ----
with open("matched_logs.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nSaved {len(results)} matched logs to matched_logs.json")