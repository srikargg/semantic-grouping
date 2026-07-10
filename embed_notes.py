import json
from sentence_transformers import SentenceTransformer

print("Loading model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded!")

with open("clean_logs.json", "r") as f:
    clean_logs = json.load(f)


print(f"\nLoaded {len(clean_logs)} clean logs")

notes = [log["notes"] for log in clean_logs]


print(f"Extracted {len(notes)} notes for embedding")
print("\nFirst 3 notes:")
for note in notes[:3]:
    print(f"  - {note}")

print("\nConverting notes to vectors...")
embeddings = model.encode(notes)
print("Done!")


print(f"\nExample note: '{notes[0]}'")
print(f"Vector length: {len(embeddings[0])} numbers")
print(f"First 5 numbers of vector: {embeddings[0][:5]}")


results = []
for i, log in enumerate(clean_logs):
    results.append({
        "hours": log["hours"],
        "notes": log["notes"],
        "embedding": embeddings[i].tolist()
    })

with open("embedded_logs.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nSaved {len(results)} embedded logs to embedded_logs.json")