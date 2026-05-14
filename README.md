# Internship Project 1 — Zoho Semantic Time-Log Grouper

## What This Does
A Python tool that connects to Zoho Projects via API, pulls time log notes,
and uses an LLM to semantically group related tasks — revealing true time
spent on activities regardless of how they were named.

## Business Value
Improves estimation accuracy by detecting when employees split work across
multiple differently-named tasks to hide time overruns.

## Tech Stack
- Python
- Zoho Projects API (OAuth 2.0)
- LLM API (Claude / OpenAI)

## Project Structure
- get_token.py        # OAuth authentication with Zoho
- README.md           # You are here
- .gitignore          # Keeps credentials off GitHub

## Progress
- [x] Phase 1: OAuth Authentication
- [x] Phase 2: Data Extraction
- [ ] Phase 3: Data Cleaning
- [ ] Phase 4: AI Semantic Grouping
- [ ] Phase 5: Report Generation
