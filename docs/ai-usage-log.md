# AI Usage Log — SkillProof

This log documents the usage of AI tools during the development of SkillProof, fulfilling hackathon transparency and authenticity guidelines.

---

## Log Entries

### Entry 001 — Phase 1: Environment & Schema Foundation
* **Date**: 2026-08-09
* **Phase**: 1 — Project Initialization & Generic Schemas
* **AI Tool Used**: Antigravity AI Coding Assistant (Gemini 3.6 Flash)
* **Tasks Executed**:
  1. Analyzed product requirements and core principles ("Build the interviewer, not the interview").
  2. Designed decoupled architecture separating deterministic backend constraints (min 8 questions, min 4 curriculum days) from non-deterministic LLM interview decision functions.
  3. Synthesized generic JSON schemas and Pydantic models for Curriculum (`Curriculum`, `Module`, `CurriculumDay`, `Topic`), Candidate (`Candidate`, `CompletedMission`, `LearningSignal`), and Interview State (`InterviewSession`, `QuestionAnswerTurn`, `SkillAssessment`).
  4. Generated synthetic demo data for curriculum (5-day AI Engineering course) and 3 candidate personas (Alex, Maya, Sam).
  5. Initialized FastAPI backend structure and Next.js + TypeScript + Tailwind CSS frontend environment.
* **Human Rationale & Control**:
  - Enforced strict backend validation for non-negotiable interview requirements (8 questions, 4 curriculum topics).
  - Selected Pydantic v2 and TypeScript strict interfaces for end-to-end type safety between backend and frontend.

---

### Entry 002 — Phase 2: Build the Interview Brain & Engine Orchestrator
* **Date**: 2026-08-09
* **Phase**: 2 — Core Adaptive AI Interview Brain & Rule Engine
* **AI Tool Used**: Antigravity AI Coding Assistant (Gemini 3.6 Flash)
* **Tasks Executed**:
  1. Implemented structured `InterviewState` manager tracking candidate depth, evidence, misconceptions, knowledge vs expression scores, and deterministic constraint counters (`questionCount >= 8`, `curriculumDaysCovered >= 4`).
  2. Built `InterviewPlanner` to generate initial adaptive assessment strategies based on candidate profiles and curriculum structures.
  3. Built `AnswerEvaluator` to score technical correctness, conceptual depth, relevance, application, and expression clarity, with explicit separation of knowledge and expression.
  4. Implemented misconception detection (e.g. probing assumptions like "RAG eliminates hallucination") and recovery path for "I don't know" responses using non-revealing scaffolds.
  5. Implemented `QuestionGenerator` supporting 6 depth levels (`Recognition` -> `Transfer`), adaptive actions (`GO_DEEPER`, `PROBE`, `REPHRASE`, `RECOVER`, `CHANGE_TOPIC`, `TRANSFER`), and cross-domain transfer to novel real-world domains.
  6. Implemented FastAPI router endpoints (`POST /api/interview/start`, `POST /api/interview/{id}/answer`, `GET /api/interview/{id}/state`, `POST /api/interview/{id}/finish`, `GET /api/interview/{id}/report`).
  7. Built automated test suite (`backend/tests/test_interview_engine.py`) demonstrating a full 8-turn simulated interview trace covering 4 curriculum days.
* **Human Rationale & Control**:
  - Ensured non-negotiable PS2 constraints (minimum 8 questions, minimum 4 curriculum days) remain strictly enforced by the backend engine rather than relying on LLM memory.
  - Implemented structured Pydantic models for evaluation outputs with a deterministic mock fallback engine for reliable automated testing.
