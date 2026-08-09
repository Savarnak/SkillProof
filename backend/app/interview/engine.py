from typing import Optional, List, Dict, Tuple, Any
import uuid
import json
import datetime
from pathlib import Path

from app.schemas.curriculum import Curriculum, Topic, CurriculumDay
from app.schemas.candidate import Candidate
from app.interview.schemas import (
    InterviewState, QuestionTurn, AnswerEvaluation, TopicAssessment,
    AdaptiveAction, InterviewDecision, MisconceptionItem, SessionStatus, InterviewReport, TopicStatus
)
from app.interview.state import session_store
from app.interview.planner import InterviewPlanner
from app.interview.evaluator import answer_evaluator
from app.interview.question_generator import question_generator
from app.interview.logger import interview_logger

from app.interview.jd_analyzer import jd_analyzer
from app.memory.service import candidate_memory_service
import logging

logger = logging.getLogger("SkillProof.Engine")

class InterviewEngine:
    """Core Orchestrator for SkillProof Adaptive AI Technical Interviewer Engine."""

    def __init__(self):
        self.session_store = session_store
        self._curriculum_cache: Optional[Curriculum] = None
        self._candidates_cache: Dict[str, Candidate] = {}
        self._load_demo_data()

    def _load_demo_data(self):
        """Loads sample curriculum and candidates strictly from backend/data/ package directory."""
        from app.data_loader import load_sample_curriculum, load_sample_candidates
        
        cdata, curr_file, curr_ok = load_sample_curriculum()
        if curr_ok and cdata:
            self._curriculum_cache = Curriculum(**cdata)
            logger.info(f"[CURRICULUM_LOADED] Loaded curriculum from {curr_file}")
        else:
            logger.error(f"[CURRICULUM_ERROR] Failed to load curriculum from {curr_file}")

        cands, cand_file, cand_ok = load_sample_candidates()
        if cand_ok and cands:
            for c in cands:
                cand_obj = Candidate(**c)
                self._candidates_cache[cand_obj.candidate_id] = cand_obj
            logger.info(f"[CANDIDATES_LOADED] Loaded {len(cands)} candidates from {cand_file}")
        else:
            logger.error(f"[CANDIDATES_ERROR] Failed to load candidates from {cand_file}")

    def get_all_topics(self) -> List[Tuple[CurriculumDay, Topic]]:
        """Returns flattened list of (CurriculumDay, Topic) tuples."""
        if not self._curriculum_cache:
            raise ValueError("Curriculum data not loaded")
        result = []
        for module in self._curriculum_cache.modules:
            for day in module.days:
                for topic in day.topics:
                    result.append((day, topic))
        return result

    def _find_topic_and_day(self, topic_id: str) -> Tuple[CurriculumDay, Topic]:
        all_t = self.get_all_topics()
        for day, topic in all_t:
            if topic.topic_id == topic_id:
                return day, topic
        return all_t[0]

    def start_interview(
        self,
        candidate_id: str,
        curriculum_id: str = "curr_ai_eng_v1",
        min_questions: int = 8,
        min_curriculum_days: int = 4,
        max_questions: int = 15,
        selected_topics: List[str] = [],
        selected_categories: List[str] = [],
        target_role: Optional[str] = None,
        job_description: Optional[str] = None,
        mode: str = "learning_journey"
    ) -> Tuple[InterviewState, str]:
        """
        Initializes an interview session, builds candidate strategy plan,
        and generates the first question. Supports both learning journey and JD modes.
        """
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        state = self.session_store.create_session(
            session_id=session_id,
            candidate_id=candidate_id,
            curriculum_id=curriculum_id,
            min_questions=min_questions,
            min_curriculum_days=min_curriculum_days
        )
        state.maxQuestions = max_questions
        state.selectedTopics = selected_topics
        state.selectedCategories = selected_categories
        state.targetRole = target_role
        state.jobDescription = job_description
        state.interviewMode = mode

        candidate = self._candidates_cache.get(
            candidate_id,
            Candidate(
                candidate_id=candidate_id,
                name="Demo Candidate",
                email="demo@skillproof.internal",
                is_synthetic_demo=True,
                background_summary="Generic engineering background",
                target_role=target_role or "Senior AI Systems Engineer"
            )
        )
        if target_role:
            candidate.target_role = target_role

        # If JD mode or job description is provided, run JD Analyzer
        if job_description or mode == "job_description":
            state.interviewMode = "job_description"
            jd_res = jd_analyzer.analyze_jd(job_description or "")
            if not state.targetRole:
                state.targetRole = jd_res.extracted_role
                candidate.target_role = jd_res.extracted_role
            state.jdRequirementCoverage = [item.model_dump() for item in jd_res.requirements_map]
            if not state.selectedTopics:
                state.selectedTopics = jd_res.required_skills

        curriculum = self._curriculum_cache
        if not curriculum:
            raise ValueError("Curriculum data unavailable")

        # Retrieve longitudinal candidate memory
        memory_ctx = candidate_memory_service.get_relevant_context(
            candidate_id=candidate.candidate_id,
            selected_topics=state.selectedTopics,
            target_role=state.targetRole,
            job_description=state.jobDescription
        )

        # Create initial plan & pending evidence list
        topics_map, global_pending_ev, start_topic_id, start_day_id, start_depth = InterviewPlanner.create_initial_plan(
            candidate=candidate,
            curriculum=curriculum,
            selected_topics=state.selectedTopics,
            target_role=state.targetRole,
            job_description=state.jobDescription,
            memory_context=memory_ctx
        )

        start_topic_obj = topics_map[start_topic_id]
        start_day = CurriculumDay(day_id=start_topic_obj.day_id, day_number=start_topic_obj.day_number, title=f"Day {start_topic_obj.day_number}: {start_topic_obj.topic_name}", topics=[])
        start_topic = Topic(topic_id=start_topic_obj.topic_id, name=start_topic_obj.topic_name, description=f"Core concepts of {start_topic_obj.topic_name}", learning_objectives=start_topic_obj.pending_evidence_list)
        pending_item = start_topic_obj.pending_evidence_list[0] if start_topic_obj.pending_evidence_list else None

        # Generate Question 1
        q_text, decision = question_generator.generate_question(
            action=AdaptiveAction.GO_DEEPER,
            topic=start_topic,
            day=start_day,
            target_depth=start_depth,
            candidate=candidate,
            pending_evidence_item=pending_item
        )

        # Memory-Aware Opening if previous historical interviews exist
        if memory_ctx.total_previous_interviews > 0 and memory_ctx.recurring_gaps:
            gap_topic = memory_ctx.recurring_gaps[0].topic
            if gap_topic.lower() in start_topic.name.lower():
                q_text = f"Welcome back. In a previous session, we explored {gap_topic} and noted an area to gather deeper practical evidence. Let's start there: {q_text}"

        # Update State
        state.interviewStatus = SessionStatus.IN_PROGRESS
        state.topicsAssessed = topics_map
        state.pendingEvidence = global_pending_ev
        state.currentTopic = start_topic_id
        state.currentDayId = start_day_id
        state.currentDepth = start_depth
        state.questionCount = 1
        state.curriculumDaysCovered = [start_day.day_number]
        state.coveredDayIds = [start_day.day_id]

        turn_1 = QuestionTurn(
            turn_index=1,
            question_id=f"q_1_{uuid.uuid4().hex[:6]}",
            topic_id=start_topic_id,
            day_id=start_day.day_id,
            day_number=start_day.day_number,
            depth_level=start_depth,
            question_text=q_text,
            decision=decision,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )

        state.conversationHistory.append(turn_1)

        # Log event
        log_entry = interview_logger.log_event("INTERVIEW_STARTED", session_id, {
            "candidate_id": candidate_id,
            "starting_topic": start_topic_id,
            "starting_depth": start_depth
        })
        state.eventLogs.append(log_entry)

        self.session_store.update_session(state)

        return state, q_text

    def submit_answer(
        self,
        session_id: str,
        candidate_answer: str
    ) -> Tuple[InterviewState, Optional[str]]:
        """
        Evaluates candidate answer for active turn, updates topic assessment & evidence,
        checks deterministic constraints, decides next action, and generates next question.
        """
        state = self.session_store.get_session(session_id)
        if not state:
            raise ValueError(f"Session '{session_id}' not found")

        if state.interviewStatus == SessionStatus.COMPLETED:
            raise ValueError("Interview session is already completed.")

        current_turn = state.conversationHistory[-1]
        current_turn.candidate_answer = candidate_answer

        topic_assessment = state.topicsAssessed[current_turn.topic_id]

        # 1. Evaluate Answer
        eval_result, updated_assessment, new_misconceptions = answer_evaluator.process_answer(
            question_text=current_turn.question_text,
            answer_text=candidate_answer,
            topic_assessment=topic_assessment,
            current_depth=current_turn.depth_level,
            turn_index=current_turn.turn_index,
            existing_misconceptions=state.misconceptions
        )

        current_turn.evaluation = eval_result
        state.topicsAssessed[current_turn.topic_id] = updated_assessment

        # Handle Expression Scaffolding Flag
        if eval_result.isExpressionUnclear:
            updated_assessment.expression_recovery_used = True

        # Collect Evidence & Misconceptions
        for ev in eval_result.evidence:
            if ev not in state.skillEvidence:
                state.skillEvidence.append(ev)
            # Remove from global pending evidence if present
            if ev in state.pendingEvidence:
                state.pendingEvidence.remove(ev)

        for str_item in eval_result.strengths:
            if str_item not in state.strengths:
                state.strengths.append(str_item)

        for gap_item in eval_result.missingConcepts:
            if gap_item not in state.knowledgeGaps:
                state.knowledgeGaps.append(gap_item)

        for issue in eval_result.expressionIssues:
            if issue not in state.expressionGaps:
                state.expressionGaps.append(issue)

        for misc in new_misconceptions:
            state.misconceptions.append(misc)

        # Detect Candidate Profile vs Live Evidence Divergence
        candidate = self._candidates_cache.get(state.candidateId)
        if candidate:
            completed_days = {m.day_id for m in candidate.completed_missions}
            if current_turn.day_id in completed_days and eval_result.technicalCorrectness < 0.30:
                div_note = f"Day {current_turn.day_number} ({current_turn.topic_id}): Profile listed mission as completed, but candidate demonstrated insufficient evidence."
                if div_note not in state.profileVsEvidenceDivergence:
                    state.profileVsEvidenceDivergence.append(div_note)
            elif current_turn.day_id not in completed_days and eval_result.technicalCorrectness > 0.85:
                div_note = f"Day {current_turn.day_number} ({current_turn.topic_id}): Profile listed no completion signal, but candidate demonstrated strong mastery."
                if div_note not in state.profileVsEvidenceDivergence:
                    state.profileVsEvidenceDivergence.append(div_note)

        # 2. Check Deterministic Backend Constraints & Max Questions
        state.canConclude = (
            (state.questionCount >= state.minQuestions and len(state.curriculumDaysCovered) >= state.minCurriculumDays) or
            state.questionCount >= state.maxQuestions
        )

        # 3. Decide Next Action & Target Topic
        misconception_flagged = len(eval_result.misconceptions) > 0
        
        all_topics = self.get_all_topics()

        next_action, next_topic_id, next_depth, reason_code, pending_item = question_generator.decide_next_action(
            eval_result_action=eval_result.recommendedNextAction,
            is_expression_unclear=eval_result.isExpressionUnclear,
            current_topic_assessment=updated_assessment,
            total_questions=state.questionCount,
            covered_days_count=len(state.curriculumDaysCovered),
            covered_days_list=state.curriculumDaysCovered,
            all_topics=all_topics,
            misconception_flagged=misconception_flagged
        )

        if next_action == AdaptiveAction.TRANSFER and current_turn.topic_id not in state.transferChallengesUsed:
            state.transferChallengesUsed.append(current_turn.topic_id)

        if next_topic_id in state.topicsAssessed:
            tass = state.topicsAssessed[next_topic_id]
            next_day = CurriculumDay(day_id=tass.day_id, day_number=tass.day_number, title=f"Day {tass.day_number}: {tass.topic_name}", topics=[])
            next_topic = Topic(topic_id=tass.topic_id, name=tass.topic_name, description=f"Core concepts of {tass.topic_name}", learning_objectives=tass.pending_evidence_list)
        else:
            next_day, next_topic = self._find_topic_and_day(next_topic_id)
            state.topicsAssessed[next_topic_id] = TopicAssessment(
                topic_id=next_topic_id,
                topic_name=next_topic.name,
                day_id=next_day.day_id,
                day_number=next_day.day_number,
                depth=next_depth,
                knowledge=0.0,
                expression=0.0,
                application=0.0,
                knowledge_confidence=0.5,
                expression_confidence=0.5,
                status=TopicStatus.NEEDS_MORE_EVIDENCE,
                evidence=[],
                pending_evidence_list=next_topic.learning_objectives or [f"Demonstrate understanding of {next_topic.name}"],
                misconceptions=[],
                expression_recovery_used=False
            )

        # Update covered days list
        if next_day.day_number not in state.curriculumDaysCovered:
            state.curriculumDaysCovered.append(next_day.day_number)
        if next_day.day_id not in state.coveredDayIds:
            state.coveredDayIds.append(next_day.day_id)

        # Increment answered question count for completed turn
        state.questionCount += 1

        # Re-check completion criteria after day tracking & question count update
        state.canConclude = (
            (state.questionCount >= state.minQuestions and len(state.curriculumDaysCovered) >= state.minCurriculumDays) or
            state.questionCount >= state.maxQuestions
        )

        # Auto-complete interview if mandatory coverage (8 questions & 4 topics) is reached
        if state.canConclude and state.questionCount >= state.minQuestions:
            state.interviewStatus = SessionStatus.COMPLETED
            state.completionReason = "mandatory_coverage_reached"
            log_entry = interview_logger.log_event(
                session_id,
                "INTERVIEW_COMPLETED",
                {
                    "total_questions": state.questionCount,
                    "days_covered": len(state.curriculumDaysCovered),
                    "status": "completed",
                    "reason": state.completionReason
                }
            )
            state.eventLogs.append(log_entry)
            self.session_store.update_session(state)
            return state, None

        # 4. Generate Next Question
        asked_q_texts = [t.question_text for t in state.conversationHistory]
        prev_t_assessment = state.topicsAssessed.get(current_turn.topic_id)
        prev_topic_name = prev_t_assessment.topic_name if prev_t_assessment else current_turn.topic_id

        next_question_text, decision = question_generator.generate_question(
            action=next_action,
            topic=next_topic,
            day=next_day,
            target_depth=next_depth,
            candidate=candidate,
            pending_evidence_item=pending_item,
            previous_answer=candidate_answer,
            asked_questions=asked_q_texts,
            previous_topic_name=prev_topic_name
        )

        state.currentTopic = next_topic_id
        state.currentDayId = next_day.day_id
        state.currentDepth = next_depth
        next_turn_index = state.questionCount + 1

        next_turn = QuestionTurn(
            turn_index=next_turn_index,
            question_id=f"q_{next_turn_index}_{uuid.uuid4().hex[:6]}",
            topic_id=next_topic_id,
            day_id=next_day.day_id,
            day_number=next_day.day_number,
            depth_level=next_depth,
            question_text=next_question_text,
            decision=decision,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )

        state.conversationHistory.append(next_turn)

        # Log event
        log_entry = interview_logger.log_event("ANSWER_EVALUATED", session_id, {
            "turn_index": current_turn.turn_index,
            "action_selected": next_action.value,
            "next_topic": next_topic_id,
            "technical_correctness": eval_result.technicalCorrectness
        })
        state.eventLogs.append(log_entry)

        self.session_store.update_session(state)

        return state, next_question_text

    def finish_interview(self, session_id: str) -> InterviewState:
        """
        Concludes interview session. Enforces deterministic backend constraints.
        If mandatory coverage (8 questions & 4 days) is met, sets status to COMPLETED.
        If maxQuestions (15) is hit without mandatory coverage, sets status to INCOMPLETE.
        """
        state = self.session_store.get_session(session_id)
        if not state:
            raise ValueError(f"Session '{session_id}' not found")

        has_mandatory_coverage = (
            state.questionCount >= state.minQuestions and
            len(state.curriculumDaysCovered) >= state.minCurriculumDays
        )

        if has_mandatory_coverage:
            state.interviewStatus = SessionStatus.COMPLETED
            state.completionReason = "mandatory_coverage_reached"
            
            # Store longitudinal candidate memory
            cand_obj = self._candidates_cache.get(state.candidateId) or Candidate(
                candidate_id=state.candidateId,
                name="Candidate",
                email="candidate@skillproof.internal",
                is_synthetic_demo=False,
                background_summary="",
                target_role=state.targetRole or "Software Engineer",
                completed_missions=[]
            )
            try:
                candidate_memory_service.store_interview_memories(state, cand_obj)
            except Exception as e:
                interview_logger.log_event("MEMORY_UNAVAILABLE", session_id, {"error": str(e)})
        elif state.questionCount >= state.maxQuestions:
            state.interviewStatus = SessionStatus.INITIALIZED  # Marked incomplete
            state.completionReason = "mandatory_coverage_not_reached"
        else:
            raise ValueError(
                f"Cannot finish interview: Deterministic constraints not met. "
                f"Questions asked: {state.questionCount}/{state.minQuestions}, "
                f"Curriculum Days covered: {len(state.curriculumDaysCovered)}/{state.minCurriculumDays}"
            )

        log_entry = interview_logger.log_event("INTERVIEW_COMPLETED", session_id, {
            "total_questions": state.questionCount,
            "days_covered": len(state.curriculumDaysCovered),
            "status": state.interviewStatus,
            "reason": state.completionReason
        })
        state.eventLogs.append(log_entry)
        self.session_store.update_session(state)
        return state

    def generate_report(self, session_id: str) -> InterviewReport:
        """Generates comprehensive post-interview assessment report."""
        state = self.session_store.get_session(session_id)
        if not state:
            raise ValueError(f"Session '{session_id}' not found")

        candidate = self._candidates_cache.get(
            state.candidateId,
            Candidate(
                candidate_id=state.candidateId,
                name="Candidate",
                email="candidate@skillproof.internal",
                is_synthetic_demo=True,
                background_summary="",
                target_role="Senior AI Systems Engineer"
            )
        )

        curr_title = self._curriculum_cache.title if self._curriculum_cache else "AI Systems"

        # Calculate averages across assessed topics
        assessed = [t for t in state.topicsAssessed.values() if t.knowledge > 0.0 or len(t.evidence) > 0]
        if assessed:
            avg_knowledge = round(sum(t.knowledge for t in assessed) / len(assessed), 2)
            avg_expression = round(sum(t.expression for t in assessed) / len(assessed), 2)
        else:
            avg_knowledge = 0.5
            avg_expression = 0.5

        transfer_status = f"Demonstrated cross-domain transfer to {len(state.transferChallengesUsed)} real-world scenarios" if len(state.transferChallengesUsed) > 0 else "Concept transfer not attempted"

        refinements = []
        for turn in state.conversationHistory:
            if turn.candidate_answer and turn.evaluation and turn.evaluation.technicalCorrectness > 0.4:
                tass = state.topicsAssessed.get(turn.topic_id)
                tname = tass.topic_name if tass else turn.topic_id
                polished = f"{turn.candidate_answer.strip().rstrip('.')} — Specifically, for {tname}, I would structure the explanation around core architecture, trade-offs, and failure handling."
                refinements.append({
                    "question": turn.question_text,
                    "originalAnswer": turn.candidate_answer,
                    "whatWasGood": ", ".join(turn.evaluation.strengths) or "Clear core attempt",
                    "whatCouldImprove": ", ".join(turn.evaluation.missingConcepts + turn.evaluation.expressionIssues) or "Add more system design detail",
                    "interviewReadyVersion": polished,
                    "howToDeliver": "Deliver directly starting with the high-level architecture before detailing components."
                })

        return InterviewReport(
            interviewId=state.interviewId,
            candidateName=candidate.name,
            curriculumTitle=curr_title,
            totalQuestionsAsked=state.questionCount,
            uniqueDaysCovered=len(state.curriculumDaysCovered),
            overallKnowledgeScore=avg_knowledge,
            overallExpressionScore=avg_expression,
            demonstratedStrengths=state.strengths[:5] or ["Solid foundational technical knowledge"],
            knowledgeGaps=state.knowledgeGaps[:5],
            expressionGaps=state.expressionGaps[:5],
            misconceptionsFound=state.misconceptions,
            profileDivergenceNotes=state.profileVsEvidenceDivergence,
            topicSummaries=state.topicsAssessed,
            transferAbility=transfer_status,
            answerRefinementSuggestions=refinements[:3],
            summaryFeedback=f"Candidate evaluated across {state.questionCount} questions covering {len(state.curriculumDaysCovered)} curriculum days. Overall knowledge score: {avg_knowledge}, expression score: {avg_expression}."
        )

interview_engine = InterviewEngine()
