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
