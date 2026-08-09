# SkillProof — Adaptive AI Technical Interviewer

> **Know it. Show it. Prove it.**
> 
> *Build the interviewer, not the interview.*

SkillProof is an adaptive AI technical interviewer that continuously evaluates candidate responses, detects technical depth and misconceptions, provides scaffolding when candidates struggle, and evaluates cross-domain technical transfer.

Unlike rigid question-bank software or static LLM wrappers, SkillProof combines **deterministic backend constraints** (mandating minimum question counts, curriculum coverage, session boundaries, and scoring rules) with **adaptive LLM reasoning** (for adaptive depth progression, scaffold generation, misconception detection, and post-interview answer refinement).

---

## Key Features & Product Principles

1. **Adaptive Depth Skill Ladder**: Evaluates candidates across Recognition, Understanding, Application, Engineering, System Design, and Transfer.
2. **Recovery & Scaffolding Path**: When a candidate struggles, the interviewer rephrases or breaks down questions without revealing answers or penalizing early.
3. **Knowledge vs. Expression Distinction**: Separates raw conceptual knowledge from technical communication fluency.
4. **Misconception Probing**: Identifies technically meaningful misconceptions (e.g., "RAG eliminates hallucinations") and probes underlying assumptions.
5. **Cross-Domain Transfer Assessment**: Tests whether candidates can transfer core technical concepts into novel real-world domains (logistics, healthcare, finance).
6. **Deterministic Constraint Enforcement**: Ensures at least 8 questions across at least 4 curriculum topics/days deterministically at the engine level.
7. **Post-Interview Answer Refiner**: Transforms candidate answers into interview-ready formats while preserving their core ideas.

---

## Architecture Overview

```text
               SkillProof Architecture
               
Curriculum Schema + Candidate Learning Signals
                       │
                       ▼
             Interview Engine (FastAPI)
      ┌────────────────────────────────┐
      │ Deterministic State Machine     │
      │ ├── Question Counter (Min 8)   │
      │ ├── Day Coverage (Min 4 Days)  │
      │ └── Session & State Manager    │
      └────────────────────────────────┘
                       │
                       ▼
         LLM Engine (Configurable Provider)
      ├── Adaptive Question Generation
      ├── Answer Analysis & Depth Scaffolding
      ├── Misconception Detection
      └── Post-Interview Report Generator
                       │
                       ▼
          SkillProof UI (Next.js & Tailwind)
      ├── / (Landing Page)
      ├── /interview/[id] (Adaptive Interview Mode)
      └── /report/[id] (Comprehensive Feedback & Refiner)
```

---

## Environment Setup & Requirements

* **Node.js**: v18+
* **Python**: v3.10+
* **FastAPI / Uvicorn**
* **Next.js 14/15**

---

## Getting Started

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

# Run FastAPI Server
uvicorn app.main:app --reload --port 8000
```

Backend health check will be available at: `http://localhost:8000/api/health`

### 2. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local

# Run Next.js Dev Server
npm run dev
```

Frontend interface will be available at: `http://localhost:3000`

---

## Generic Schemas & Synthetic Data

SkillProof is decoupled from specific curricula. Demo synthetic data is located in `data/`:
* `data/sample_curriculum.json`: Generic 5-day AI Systems curriculum.
* `data/sample_candidates.json`: Synthetic candidate learning profiles (Alex, Maya, Sam).

---

## Project Structure

```text
SkillProof/
├── docs/
│   └── ai-usage-log.md        # AI transparent usage log
├── data/
│   ├── sample_curriculum.json # Synthetic curriculum demo data
│   └── sample_candidates.json # Synthetic candidate demo data
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── config.py          # Settings and environment validation
│   │   └── schemas/           # Pydantic schemas (curriculum, candidate, interview)
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/                   # Next.js App Router & React components
    ├── package.json
    └── .env.example
```

---

## License

Created for the Hackathon.
