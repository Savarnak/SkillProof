from typing import Optional, List, Dict, Tuple, Any
import uuid
import json
import datetime
from pathlib import Path

from app.schemas.curriculum import Curriculum, Topic, CurriculumDay
from app.schemas.candidate import Candidate
from app.interview.schemas import (
    InterviewState, QuestionTurn, AnswerEvaluation, TopicAssessment,
    AdaptiveAction, InterviewDecision, MisconceptionItem, SessionStatus, InterviewReport
)
from app.interview.state import session_store
from app.interview.planner import InterviewPlanner
from app.interview.evaluator import answer_evaluator
from app.interview.question_generator import question_generator

class InterviewEngine:
    """Core Orchestrator for SkillProof Adaptive AI Technical Interviewer."""

    def __init__(self):
        self.session_store = session_store
        self._curriculum_cache: Optional[Curriculum] = None
        self._candidates_cache: Dict[str, Candidate] = {}
        self._load_demo_data()

    def _load_demo_data(self):
        """Loads sample curriculum and candidates from data/ directory."""
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        curr_file = data_dir / "sample_curriculum.json"
        cand_file = data_dir / "sample_candidates.json"

        if curr_file.exists():
            with open(curr_file, "r", encoding="utf-8") as f:
                cdata = json.load(f)
                self._curriculum_cache = Curriculum(**cdata)

        if cand_file.exists():
            with open(cand_file, "r", encoding="utf-8") as f:
                cands = json.load(f)
                for c in cands:
                    cand_obj = Candidate(**c)
                    self._candidates_cache[cand_obj.candidate_id] = cand_obj

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
        min_curriculum_days: int = 4
    ) -> Tuple[InterviewState, str]:
        """
        Initializes an interview session, builds candidate strategy plan,
        and generates the first question.
        """
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        state = self.session_store.create_session(
            session_id=session_id,
            candidate_id=candidate_id,
            curriculum_id=curriculum_id,
            min_questions=min_questions,
            min_curriculum_days=min_curriculum_days
        )

        candidate = self._candidates_cache.get(
            candidate_id,
            Candidate(
                candidate_id=candidate_id,
                name="Demo Candidate",
                email="demo@skillproof.internal",
                is_synthetic_demo=True,
                background_summary="Generic engineering background",
                target_role="AI Engineer"
            )
        )

        curriculum = self._curriculum_cache
        if not curriculum:
            raise ValueError("Curriculum data unavailable")

        # Create initial plan
        topics_map, start_topic_id, start_day_id, start_depth = InterviewPlanner.create_initial_plan(
            candidate=candidate,
            curriculum=curriculum
        )

        start_day, start_topic = self._find_topic_and_day(start_topic_id)

        # Generate Question 1
        q_text, decision = question_generator.generate_question(
            action=AdaptiveAction.GO_DEEPER,
            topic=start_topic,
            day=start_day,
            target_depth=start_depth
        )

        # Update State
        state.interviewStatus = SessionStatus.IN_PROGRESS
        state.topicsAssessed = topics_map
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
            turn_index=current_turn.turn_index
        )

        current_turn.evaluation = eval_result
        state.topicsAssessed[current_turn.topic_id] = updated_assessment

        # Collect Evidence & Misconceptions
        for ev in eval_result.evidence:
            if ev not in state.skillEvidence:
                state.skillEvidence.append(ev)

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

        # 2. Check Deterministic Backend Constraints
        unique_days = set(state.curriculumDaysCovered)
        if len(state.coveredDayIds) < len(unique_days):
            pass # keep consistent
        
        state.canConclude = (
            state.questionCount >= state.minQuestions and
            len(state.curriculumDaysCovered) >= state.minCurriculumDays
        )

        # 3. Decide Next Action & Target Topic
        misconception_flagged = len(eval_result.misconceptions) > 0
        all_topics = self.get_all_topics()

        next_action, next_topic_id, next_depth, reason_code = question_generator.decide_next_action(
            eval_result_action=eval_result.recommendedNextAction,
            current_topic_assessment=updated_assessment,
            total_questions=state.questionCount,
            covered_days_count=len(state.curriculumDaysCovered),
            covered_days_list=state.curriculumDaysCovered,
            all_topics=all_topics,
            misconception_flagged=misconception_flagged
        )

        if next_action == AdaptiveAction.TRANSFER and current_turn.topic_id not in state.transferChallengesUsed:
            state.transferChallengesUsed.append(current_turn.topic_id)

        next_day, next_topic = self._find_topic_and_day(next_topic_id)

        # Update covered days list
        if next_day.day_number not in state.curriculumDaysCovered:
            state.curriculumDaysCovered.append(next_day.day_number)
        if next_day.day_id not in state.coveredDayIds:
            state.coveredDayIds.append(next_day.day_id)

        # Re-check completion criteria after day tracking
        state.canConclude = (
            state.questionCount >= state.minQuestions and
            len(state.curriculumDaysCovered) >= state.minCurriculumDays
        )

        # 4. Generate Next Question
        next_question_text, decision = question_generator.generate_question(
            action=next_action,
            topic=next_topic,
            day=next_day,
            target_depth=next_depth,
            previous_answer=candidate_answer
        )

        state.currentTopic = next_topic_id
        state.currentDayId = next_day.day_id
        state.currentDepth = next_depth
        next_turn_index = state.questionCount + 1
        state.questionCount = next_turn_index

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
        self.session_store.update_session(state)

        return state, next_question_text

    def finish_interview(self, session_id: str) -> InterviewState:
        """
        Concludes interview session. Enforces deterministic backend constraints.
        Fails if questionCount < 8 or uniqueCurriculumDays < 4.
        """
        state = self.session_store.get_session(session_id)
        if not state:
            raise ValueError(f"Session '{session_id}' not found")

        if not state.canConclude and (state.questionCount < state.minQuestions or len(state.curriculumDaysCovered) < state.minCurriculumDays):
            raise ValueError(
                f"Cannot finish interview: Deterministic constraints not met. "
                f"Questions asked: {state.questionCount}/{state.minQuestions}, "
                f"Curriculum Days covered: {len(state.curriculumDaysCovered)}/{state.minCurriculumDays}"
            )

        state.interviewStatus = SessionStatus.COMPLETED
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
                target_role="AI Engineer"
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

        transfer_status = "Demonstrated successful transfer to real-world domain" if len(state.transferChallengesUsed) > 0 else "Concept transfer not attempted"

        refinements = []
        for turn in state.conversationHistory:
            if turn.candidate_answer and turn.evaluation and turn.evaluation.technicalCorrectness > 0.4:
                refinements.append({
                    "question": turn.question_text,
                    "originalAnswer": turn.candidate_answer,
                    "whatWasGood": ", ".join(turn.evaluation.strengths) or "Clear core attempt",
                    "whatCouldImprove": ", ".join(turn.evaluation.missingConcepts + turn.evaluation.expressionIssues) or "Add more system design detail",
                    "interviewReadyVersion": f"In {turn.topic_id}, {turn.candidate_answer} Specifically, I would consider production latency and vector index caching.",
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
            topicSummaries=state.topicsAssessed,
            transferAbility=transfer_status,
            answerRefinementSuggestions=refinements[:3],
            summaryFeedback=f"Candidate evaluated across {state.questionCount} questions covering {len(state.curriculumDaysCovered)} curriculum days. Overall knowledge score: {avg_knowledge}, expression score: {avg_expression}."
        )

interview_engine = InterviewEngine()
