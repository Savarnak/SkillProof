from typing import Tuple, List
from app.interview.schemas import (
    AnswerEvaluation, TopicAssessment, AdaptiveAction, MisconceptionItem, SessionStatus
)
from app.interview.llm import llm_service

class AnswerEvaluator:
    """Evaluates candidate answers and updates candidate topic assessments."""

    @staticmethod
    def process_answer(
        question_text: str,
        answer_text: str,
        topic_assessment: TopicAssessment,
        current_depth: int,
        turn_index: int
    ) -> Tuple[AnswerEvaluation, TopicAssessment, List[MisconceptionItem]]:
        """
        Processes answer via LLM/Evaluator service.
        Updates topic_assessment scores, depth, evidence, and returns discovered misconceptions.
        """
        eval_result = llm_service.evaluate_answer(
            question_text=question_text,
            answer_text=answer_text,
            topic_name=topic_assessment.topic_name,
            current_depth=current_depth
        )

        new_misconceptions: List[MisconceptionItem] = []

        # 1. Knowledge vs Expression Score Update
        # Knowledge score is derived strictly from technical correctness, conceptual depth, reasoning, and application
        raw_knowledge = (
            eval_result.technicalCorrectness * 0.35 +
            eval_result.conceptualDepth * 0.35 +
            eval_result.application * 0.30
        )
        
        # Expression score is derived strictly from clarity & structure
        raw_expression = (
            eval_result.expressionClarity * 0.60 +
            eval_result.answerStructure * 0.40
        )

        # Exponential moving average update for topic assessment
        if topic_assessment.knowledge == 0.0:
            topic_assessment.knowledge = round(raw_knowledge, 2)
            topic_assessment.expression = round(raw_expression, 2)
            topic_assessment.application = round(eval_result.application, 2)
        else:
            topic_assessment.knowledge = round(topic_assessment.knowledge * 0.4 + raw_knowledge * 0.6, 2)
            topic_assessment.expression = round(topic_assessment.expression * 0.4 + raw_expression * 0.6, 2)
            topic_assessment.application = round(topic_assessment.application * 0.4 + eval_result.application * 0.6, 2)

        # 2. Update Depth & Evidence
        if eval_result.technicalCorrectness >= 0.75 and not eval_result.isStrugglingOrDontKnow:
            if topic_assessment.depth < 6:
                topic_assessment.depth = min(6, max(topic_assessment.depth, current_depth + 1))
        
        for ev in eval_result.evidence:
            if ev not in topic_assessment.evidence:
                topic_assessment.evidence.append(ev)

        # 3. Misconception Discovery
        for misc in eval_result.misconceptions:
            if misc not in topic_assessment.misconceptions:
                topic_assessment.misconceptions.append(misc)
                new_misconceptions.append(
                    MisconceptionItem(
                        topic=topic_assessment.topic_name,
                        misconception=misc,
                        status="identified",
                        detected_at_turn=turn_index
                    )
                )

        return eval_result, topic_assessment, new_misconceptions

answer_evaluator = AnswerEvaluator()
