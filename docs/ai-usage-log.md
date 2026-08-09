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

---

### Entry 003 — Phase 3: Adaptive Intelligence & Differentiation
* **Date**: 2026-08-09
* **Phase**: 3 — Adaptive Intelligence, Evidence Confidence, & Observability
* **AI Tool Used**: Antigravity AI Coding Assistant (Gemini 3.6 Flash)
* **Tasks Executed**:
  1. Implemented modular Prompt Architecture (`backend/app/interview/prompts.py`) isolating prompt templates for context, answer evaluation, adaptive question generation, misconception challenge probes, expression scaffolding, cross-domain transfer, and post-interview feedback.
  2. Implemented structured event logger (`backend/app/interview/logger.py`) emitting observable telemetry for all interviewer events (`INTERVIEW_STARTED`, `ANSWER_EVALUATED`, `ACTION_SELECTED`, `EXPRESSION_SCAFFOLD_TRIGGERED`, `MISCONCEPTION_CHALLENGED`, `TRANSFER_TRIGGERED`, `INTERVIEW_COMPLETED`).
  3. Extended `InterviewState` schema with `pendingEvidence` tracking, `knowledge_confidence` / `expression_confidence` calculation, misconception resolution status tracking (`IDENTIFIED`, `PROBED`, `RESOLVED`, `PERSISTS`), and candidate profile vs live interview evidence divergence notes.
  4. Built Expression Scaffolding Recovery path (`EXPRESSION_SCAFFOLD` action) for candidates who demonstrate high technical knowledge but produce informal/unstructured responses.
  5. Implemented Candidate-Tailored Cross-Domain Transfer Engine mapping candidate target role and background to unfamiliar domains (Healthcare, Logistics, E-Commerce, Finance, Cybersecurity).
  6. Enforced `MAX_QUESTIONS = 15` safety guardrail alongside `minQuestions = 8` and `minCurriculumDays = 4`.
  7. Expanded automated test suite (`backend/tests/test_interview_engine.py`) covering Scenarios A through G and executing a 13-step adaptive trace demonstrating all adaptive behaviors end-to-end.
* **Human Rationale & Control**:
  - Established live interview evidence priority over candidate profile signals, ensuring candidate assumptions are treated as initial hypotheses verified or overridden by live evidence.
  - Separated technical knowledge scoring from expression scoring without making inferences on psychological state, accent, or emotional state.

---

### Entry 004 — Phase 5: Evidence Report Engine, Rule Enforcement Fix & Coaching
* **Date**: 2026-08-09
* **Phase**: 5 — Post-Interview Evidence Report, Rule Enforcement Fix & Coaching
* **AI Tool Used**: Antigravity AI Coding Assistant (Gemini 3.6 Flash)
* **Tasks Executed**:
  1. Implemented authoritative completion rule fix (`backend/app/interview/engine.py`): sessions reaching `maxQuestions == 15` without mandatory coverage (8 questions & 4 curriculum days) are strictly flagged as `interviewStatus = "incomplete"` (`completionReason = "mandatory_coverage_not_reached"`) rather than falsely reporting a compliant completed interview.
  2. Created dedicated Report Service Module (`backend/app/report/`) featuring `ReportAggregator` and `ReportGenerator` with a transparent score weighting strategy (Knowledge 30%, Reasoning 20%, Application 20%, Expression 15%, Transfer 15%).
  3. Implemented Collapsible Topic Evidence Expanders ("Why?") linking scores directly to source questions (`Q2`, `Q5`, `Q9`) and quotes, while explicitly marking unassessed topics as `"Not Assessed"` rather than penalizing candidate with a 0 score.
  4. Built Answer Refinement & Coaching engine (`/report/[id]/answers`) providing Before vs. After answer comparisons, structural diff callouts (`+ Direct opening`, `- Unnecessary repetition`), delivery coaching formulas, and personalized Technical Delivery Playbook formulas.
  5. Created UI components (`EvidenceExpander.tsx`, `TopicEvidenceMap.tsx`, `DepthLadderVisualizer.tsx`) and polished candidate UI for 390px mobile responsiveness.
  6. Built Phase 5 test suite (`backend/tests/test_report_engine.py`) verifying valid completion, incomplete status rule fix, evidence question linking, misconception lifecycles, and answer refinement diffs.
* **Human Rationale & Control**:
  - Fixed interview completion rule logic to prevent false-positive completions when max questions limit is reached.
  - Ensured all report insights and score breakdowns are strictly evidence-backed without fabricating psychological or emotional conclusions.

---

### Entry 005 — Refinements: Setup, Flexible Category Selection, Job Description Analyzer & Navigation
* **Date**: 2026-08-09
* **Phase**: Refinements — Flexible Topic Selection, JD Analyzer, & Navigation Safety
* **AI Tool Used**: Antigravity AI Coding Assistant (Gemini 3.6 Flash)
* **Tasks Executed**:
  1. Replaced rigid 3-persona selection with flexible setup experience ("What do you want to be challenged on?"). Built `CategorySelector.tsx` featuring 4 expandable category accordions (Core CS, Frameworks & Development, Technical / Emerging Tech, Programming Languages) and Target Role selection.
  2. Added "Interview me for a specific job" tab featuring `JobDescriptionInput.tsx` for pasting Job Descriptions. Built Job Description Analyzer (`backend/app/interview/jd_analyzer.py`) extracting required skills, languages, frameworks, cloud tools, databases, and roles, and tracking JD requirement coverage (`✓ Strong`, `✓ Demonstrated`, `△ Developing`, `○ Not assessed`).
  3. Displayed **Job Description Readiness Matrix** on discovery report (`/report/[id]`) when operating in JD mode.
  4. Removed artificial `Day 1 -> Day 2 -> Day 3` increment badges from the active interview header (`JourneyTracker.tsx`), replacing them with actual topic/concept exploration context (`Exploring: Spring Boot → Dependency Injection`).
  5. Implemented navigation safety controls (`LeaveInterviewModal.tsx`): added `← Back to Home` links on report pages and confirmation modal when navigating away from active interviews (`"Leave this interview? Progress will be saved."`).
  6. Added `"Continue where you left off"` recent session card on the landing page (`/`) for returning candidates.
  7. Extended `StartInterviewRequest` schema maintaining 100% backward compatibility.
  8. Created automated test suite (`backend/tests/test_jd_mode.py`) verifying JD skill extraction, JD mode session initialization, and custom topic/role selection.
* **Human Rationale & Control**:
  - Preserved internal PS2 backend curriculum day tracking (`minQuestions = 8`, `minCurriculumDays = 4`) while correcting the candidate UI to present genuine topic context rather than artificial day increments.
  - Supported both Learning Journey mode and Job Description mode without creating duplicate interview engines.
