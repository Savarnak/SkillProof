from typing import Tuple, Optional, List
from app.interview.schemas import (
    AdaptiveAction, InterviewDecision, TopicAssessment, TopicStatus
)
from app.interview.llm import llm_service
from app.schemas.curriculum import Curriculum, Topic, CurriculumDay

class QuestionGenerator:
    """Decides next adaptive action and generates tailored interviewer questions."""

    TRANSFER_DOMAINS = [
        "Logistics & Supply Chain Exception Tracking",
        "Healthcare Diagnostic Report Intelligence",
        "E-Commerce Real-time Recommendation Engine",
        "Financial Fraud Audit Search",
    ]

    @staticmethod
    def decide_next_action(
        eval_result_action: AdaptiveAction,
        current_topic_assessment: TopicAssessment,
        total_questions: int,
        covered_days_count: int,
        covered_days_list: List[int],
        all_topics: List[Tuple[CurriculumDay, Topic]],
        misconception_flagged: bool = False
    ) -> Tuple[AdaptiveAction, str, int, str]:
        """
        Determines next adaptive action, next target topic, target depth, and reason code.
        Prioritizes uncovered curriculum days to satisfy non-negotiable PS2 coverage rules.
        """
        # 1. If candidate struggled or expressed "I don't know", recover with scaffolding
        if eval_result_action == AdaptiveAction.RECOVER:
            return (
                AdaptiveAction.RECOVER,
                current_topic_assessment.topic_id,
                current_topic_assessment.depth,
                "struggled_needs_scaffold"
            )

        # 2. If misconception was flagged, probe it
        if misconception_flagged or eval_result_action == AdaptiveAction.PROBE:
            return (
                AdaptiveAction.PROBE,
                current_topic_assessment.topic_id,
                current_topic_assessment.depth,
                "misconception_flagged"
            )

        # 3. Check for Cross-Domain Transfer Readiness (Level 4+ depth achieved)
        if current_topic_assessment.depth >= 4 and len(current_topic_assessment.evidence) >= 2:
            return (
                AdaptiveAction.TRANSFER,
                current_topic_assessment.topic_id,
                6,  # Transfer depth level 6
                "ready_for_cross_domain_transfer"
            )

        # 4. If current topic has sufficient evidence or depth >= 2, move to next curriculum day
        if len(current_topic_assessment.evidence) >= 1 or current_topic_assessment.depth >= 2:
            # First priority: find a topic on a curriculum day not yet covered
            for day, topic in all_topics:
                if day.day_number not in covered_days_list:
                    return (
                        AdaptiveAction.CHANGE_TOPIC,
                        topic.topic_id,
                        1,
                        f"switch_to_uncovered_day_{day.day_number}"
                    )
            
            # Second priority: pick any unassessed topic
            for day, topic in all_topics:
                if topic.topic_id != current_topic_assessment.topic_id:
                    return (
                        AdaptiveAction.CHANGE_TOPIC,
                        topic.topic_id,
                        1,
                        "sufficient_evidence_switch_topic"
                    )

        # 5. Default: GO_DEEPER on current topic
        next_depth = min(5, current_topic_assessment.depth + 1)
        return (
            AdaptiveAction.GO_DEEPER,
            current_topic_assessment.topic_id,
            next_depth,
            "strong_fundamentals"
        )

    @classmethod
    def generate_question(
        cls,
        action: AdaptiveAction,
        topic: Topic,
        day: CurriculumDay,
        target_depth: int,
        previous_answer: Optional[str] = None
    ) -> Tuple[str, InterviewDecision]:
        """Generates question text and constructs the structured InterviewDecision object."""
        scaffold_prompt = None
        transfer_domain = None
        
        if action == AdaptiveAction.TRANSFER:
            domain_idx = (target_depth + day.day_number) % len(cls.TRANSFER_DOMAINS)
            transfer_domain = cls.TRANSFER_DOMAINS[domain_idx]

        if action == AdaptiveAction.RECOVER:
            scaffold_prompt = f"Simplify {topic.name} into basic functional elements"

        question_text = llm_service.generate_question_text(
            action=action,
            topic_name=topic.name,
            day_number=day.day_number,
            target_depth=target_depth,
            scaffold_prompt=scaffold_prompt,
            transfer_domain=transfer_domain,
            previous_answer=previous_answer
        )

        decision = InterviewDecision(
            action=action,
            topic_id=topic.topic_id,
            target_depth=target_depth,
            reasonCode=f"{action.value.lower()}_for_{topic.topic_id}",
            scaffold_prompt=scaffold_prompt,
            transfer_domain=transfer_domain
        )

        return question_text, decision

question_generator = QuestionGenerator()
