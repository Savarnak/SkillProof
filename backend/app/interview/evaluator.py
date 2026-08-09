from typing import Tuple, List
from app.interview.schemas import (
    AnswerEvaluation, TopicAssessment, AdaptiveAction, MisconceptionItem,
    MisconceptionStatus, SessionStatus
)
from app.interview.llm import llm_service

class AnswerEvaluator:
    """Evaluates candidate answers, updates topic assessments, pending evidence, and misconception statuses."""

    @staticmethod
    def process_answer(
        question_text: str,
        answer_text: str,
        topic_assessment: TopicAssessment,
        current_depth: int,
        turn_index: int,
        existing_misconceptions: List[MisconceptionItem]
    ) -> Tuple[AnswerEvaluation, TopicAssessment, List[MisconceptionItem]]:
        """
        Processes answer via LLM/Evaluator service.
        Updates topic_assessment scores, depth, evidence, pending evidence, and misconception resolutions.
        """
        eval_result = llm_service.evaluate_answer(
            question_text=question_text,
            answer_text=answer_text,
            topic_name=topic_assessment.topic_name,
            current_depth=current_depth
        )

        new_misconceptions: List[MisconceptionItem] = []

        # 1. Separate Knowledge & Expression Score Calculation
        raw_knowledge = (
            eval_result.technicalCorrectness * 0.35 +
            eval_result.conceptualDepth * 0.35 +
            eval_result.application * 0.30
        )
        
        raw_expression = (
            eval_result.expressionClarity * 0.60 +
            eval_result.answerStructure * 0.40
        )

        # Handle Expression Scaffolding Recovery
        if topic_assessment.expression_recovery_used:
            # Boost expression score if candidate responded well after scaffolding
            if eval_result.expressionClarity > 0.60:
                raw_expression = max(raw_expression, 0.80)

        if topic_assessment.knowledge == 0.0:
            topic_assessment.knowledge = round(raw_knowledge, 2)
            topic_assessment.expression = round(raw_expression, 2)
            topic_assessment.application = round(eval_result.application, 2)
        else:
            topic_assessment.knowledge = round(topic_assessment.knowledge * 0.4 + raw_knowledge * 0.6, 2)
            topic_assessment.expression = round(topic_assessment.expression * 0.4 + raw_expression * 0.6, 2)
            topic_assessment.application = round(topic_assessment.application * 0.4 + eval_result.application * 0.6, 2)

        # Calculate evidence confidence
        ev_count = len(topic_assessment.evidence) + (1 if eval_result.technicalCorrectness > 0.70 else 0)
        topic_assessment.knowledge_confidence = min(0.98, round(0.50 + ev_count * 0.15, 2))
        topic_assessment.expression_confidence = min(0.98, round(0.50 + ev_count * 0.15, 2))

        # 2. Update Depth & Evidence
        if eval_result.technicalCorrectness >= 0.75 and not eval_result.isStrugglingOrDontKnow:
            if topic_assessment.depth < 6:
                topic_assessment.depth = min(6, max(topic_assessment.depth, current_depth + 1))
        
        for ev in eval_result.evidence:
            if ev not in topic_assessment.evidence:
                topic_assessment.evidence.append(ev)

        # 3. Update Pending Evidence List (Remove demonstrated items)
        if eval_result.technicalCorrectness >= 0.60 and topic_assessment.pending_evidence_list:
            # Remove top demonstrated item from pending list
            topic_assessment.pending_evidence_list.pop(0)

        # 4. Misconception Resolution & Discovery
        # Check if an existing misconception was probed in this turn
        for misc in existing_misconceptions:
            if misc.topic == topic_assessment.topic_name and misc.status == MisconceptionStatus.IDENTIFIED:
                misc.status = MisconceptionStatus.PROBED
                # Check if candidate resolved it in their answer
                if "depend" in answer_text.lower() or "source" in answer_text.lower() or "no" in answer_text.lower() or "incorrect" in answer_text.lower():
                    misc.status = MisconceptionStatus.RESOLVED
                    misc.resolution_turn = turn_index
                else:
                    misc.status = MisconceptionStatus.PERSISTS

        for misc_text in eval_result.misconceptions:
            if misc_text not in topic_assessment.misconceptions:
                topic_assessment.misconceptions.append(misc_text)
                new_misconceptions.append(
                    MisconceptionItem(
                        topic=topic_assessment.topic_name,
                        misconception=misc_text,
                        status=MisconceptionStatus.IDENTIFIED,
                        detected_at_turn=turn_index
                    )
                )

        return eval_result, topic_assessment, new_misconceptions

answer_evaluator = AnswerEvaluator()
