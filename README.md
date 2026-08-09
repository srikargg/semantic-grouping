# Semantic Time-Log Aggregator
### AI-Powered Project Time Analysis Using Vector Embeddings & Cosine Similarity

---

## Overview

Traditional project management tools rely on task names and manual categorization to track time. This creates a fundamental problem — employees often distribute hours across multiple differently-named subtasks to mask estimation overruns, making it impossible for managers to accurately assess true time expenditure on any given activity.

This tool solves that problem by applying **Natural Language Processing (NLP)** and **semantic vector similarity** to automatically analyze the *meaning* of time log notes — not just their surface-level keywords — and intelligently group related work entries regardless of how they were named.

---

## The Problem

In project management, employees are given time estimates for tasks. When actual time exceeds the estimate, a common workaround is to split the work into multiple subtasks with different names, making each individual entry appear on-budget. The result:

- Managers see dozens of small tasks all appearing correctly estimated
- The true cumulative time spent on the original activity is hidden
- Project estimation accuracy degrades over time
- Resource planning and forecasting become unreliable

**Example:**

Task A: "Python file reader setup" — Estimated: 1hr, Actual: 1hr ✓
Task B: "File handler optimization" — Estimated: 1hr, Actual: 1hr ✓
Task C: "File I/O error resolution" — Estimated: 1hr, Actual: 1hr ✓

What actually happened: One task ("Read a file in Python") took 3 hours, split across 3 differently-named entries to hide the overrun.

---

## The Solution

This tool uses a multi-stage AI pipeline to:

1. Extract time log data and notes from Zoho Projects via REST API
2. Clean and preprocess the unstructured text data
3. Generate dense vector embeddings for each note using a Small Language Model (SLM)
4. Apply cosine similarity with hierarchical guardrails to semantically match logs to their true parent tasks
5. Aggregate total hours per semantic group and surface estimation discrepancies

---

## Technical Architecture

### System Pipeline

Zoho Projects API
│
▼
┌─────────────────────┐
│ Data Ingestion │ OAuth 2.0 authentication
│ fetch_timelogs.py │ REST API calls with bearer tokens
└─────────────────────┘
│
▼
┌─────────────────────┐
│ Data Cleaning │ Rule-based filtering
│ clean_data.py │ Removes empty, trivial, and low-signal entries
└─────────────────────┘
│
▼
┌─────────────────────┐
│ Embedding Engine │ SLM: all-MiniLM-L6-v2
│ embed_notes.py │ 384-dimensional dense vector space
└─────────────────────┘
│
▼
┌─────────────────────┐
│ Semantic Matching │ Cosine similarity with hierarchy guardrails
│ match_logs.py │ Task list → Milestone → Project boundary enforcement
└─────────────────────┘
│
▼
┌─────────────────────┐
│ Aggregation │ Hours summation per semantic group
│ aggregate.py │ Variance analysis vs original estimates
└─────────────────────┘
│
▼
JSON / CSV Report

---

## Core Technology

### Small Language Model (SLM) — `all-MiniLM-L6-v2`

Rather than relying on a large generative LLM (GPT, Claude, etc.) which would be slow, expensive, and prone to hallucination for this task, this system uses a purpose-built **Small Language Model** from HuggingFace's Sentence Transformers library.

`all-MiniLM-L6-v2` is a distilled transformer model trained specifically on semantic textual similarity tasks. It maps input sentences into a **384-dimensional vector space** where geometric proximity corresponds to semantic similarity — meaning sentences with similar *meaning* cluster together, regardless of surface-level word overlap.

Key properties:
- 22.7M parameters (lightweight, runs entirely on CPU)
- Trained on 1B+ sentence pairs using contrastive learning
- Mean Pooling over token embeddings to produce fixed-size sentence representations
- Inference time: ~50ms per sentence on standard hardware

### Vector Embeddings

Each time log note is transformed into a dense vector:
"call with Prabhu regarding Zoho card management"
↓ all-MiniLM-L6-v2
[-0.1187, 0.0533, -0.0685, 0.0412, ..., 0.0821] ← 384 dimensions

This vector encodes **semantic meaning**, not keywords. Two sentences that describe the same activity will produce geometrically proximate vectors even with completely different vocabulary.

### Cosine Similarity

Similarity between a log note embedding and a task title embedding is computed using **cosine similarity**:
cos(θ) = (A · B) / (||A|| × ||B||)

Where:
- `A` = embedding vector of the time log note
- `B` = embedding vector of the task title
- `·` = dot product
- `||x||` = L2 norm (Euclidean magnitude)

Cosine similarity measures the **angle** between two vectors in high-dimensional space rather than their magnitude. This makes it robust to variations in note length — a short note and a long note describing the same activity will still score high similarity because they point in the same semantic direction.

Score interpretation:
| Score | Meaning |
|-------|---------|
| 0.9 - 1.0 | Near-identical meaning |
| 0.7 - 0.9 | Strong semantic match |
| 0.5 - 0.7 | Moderate match |
| 0.3 - 0.5 | Weak match |
| 0.0 - 0.3 | No meaningful relationship |

### Why Cosine Over Other Metrics

| Metric | Formula | Weakness For This Use Case |
|--------|---------|---------------------------|
| Cosine Similarity | angle between vectors | None — length invariant |
| Euclidean Distance | √Σ(aᵢ-bᵢ)² | Sensitive to vector magnitude, penalizes longer notes |
| Dot Product | Σ(aᵢ×bᵢ) | Not normalized, biased toward longer texts |
| Manhattan Distance | Σ\|aᵢ-bᵢ\| | High dimensional noise, poor semantic signal |

Cosine similarity was selected because time log notes vary significantly in length and verbosity. A one-line note and a five-line note describing the same meeting should score high similarity — cosine handles this correctly while other metrics would penalize the length difference.

---

## Hierarchical Guardrail System

A critical design decision in this system is enforcing **organizational boundaries** during matching. Without guardrails, cosine similarity could match a log from one project to a task in a completely different project — even with a high score — because the semantic content overlaps (e.g. two different teams discussing the same technology).

The guardrail system enforces matching within this hierarchy:
Project (boundary level 3)
└── Milestone (boundary level 2)
└── Task List (boundary level 1 — tightest)
└── Task ← match candidates
└── Time Log (note to be matched)

Matching precedence:
1. First attempt matching within the **same Task List**
2. If no match above threshold → expand to **same Milestone**
3. If no match above threshold → expand to **same Project**
4. If no match above threshold → flag as **Unmatched** (original task preserved)

This prevents cross-project contamination and ensures matches are contextually meaningful within the organizational structure.

---

## OAuth 2.0 Authentication Flow

Client Credentials + Refresh Token
│
▼
POST https://accounts.zoho.com/oauth/v2/token
│
▼
Access Token (TTL: 3600s)
│
▼
Authorization: Zoho-oauthtoken <access_token>
│
▼
Zoho Projects REST API

Credentials are stored in a `.env` file and loaded at runtime using `python-dotenv`. Access tokens are regenerated automatically on each run since they expire after 1 hour.

---

## Data Pipeline Detail

### Stage 1 — Extraction
Pulls from Zoho Projects API v3:
- Portal metadata
- Project list with IDs
- Task hierarchy (milestones → task lists → tasks)
- Time logs with notes, hours, and task associations

### Stage 2 — Cleaning (`clean_data.py`)
Filters out low-signal entries:
- Empty notes
- Notes under 10 characters
- Known garbage phrases ("Status call", "Idle time", "Done")
- Entries with no semantic content

Reduction: ~100 raw logs → 47 meaningful entries (53% noise reduction)

### Stage 3 — Embedding (`embed_notes.py`)
- Loads `all-MiniLM-L6-v2` locally via HuggingFace
- Encodes all 47 cleaned notes into 384-dim vectors
- Saves embeddings to `embedded_logs.json` to avoid recomputation

### Stage 4 — Matching (`match_logs.py`)
- Fetches real task names from Zoho API dynamically
- Encodes task names into the same 384-dim vector space
- Computes pairwise cosine similarity matrix
- Applies hierarchical guardrails
- Returns top-3 candidate matches per log with scores
- Flags low-confidence matches below threshold

### Stage 5 — Aggregation (`aggregate.py`)
- Groups matched logs by semantic category
- Sums total hours per group
- Compares against original Zoho task estimates
- Flags variance exceeding defined tolerance

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| API Integration | Zoho Projects REST API v3 |
| Authentication | OAuth 2.0 with refresh token rotation |
| ML Model | `sentence-transformers/all-MiniLM-L6-v2` |
| Similarity Metric | Cosine Similarity via `scikit-learn` |
| Vector Operations | NumPy |
| Credential Management | python-dotenv |
| Output Formats | JSON, CSV |
| Version Control | Git / GitHub |

---

## Project Structure

internship-project-1/
│
├── get_token.py # OAuth 2.0 token generation
├── fetch_timelogs.py # Zoho API data extraction
├── clean_data.py # NLP preprocessing & noise filtering
├── embed_notes.py # SLM vector embedding generation
├── match_logs.py # Cosine similarity matching engine
├── aggregate.py # Hours aggregation & variance analysis
│
├── .env # Credentials (git-ignored)
├── .gitignore
└── README.md

## Progress
- [x] Phase 1: OAuth Authentication
- [x] Phase 2: Data Extractions
- [x] Phase 3: Data Cleaning
- [ ] Phase 4: AI Semantic Grouping
- [ ] Phase 5: Report Generation

