from typing import Tuple, Optional, List, Dict
from app.interview.schemas import (
    AdaptiveAction, InterviewDecision, TopicAssessment, TopicStatus
)
from app.interview.llm import llm_service
from app.schemas.curriculum import Curriculum, Topic, CurriculumDay
from app.schemas.candidate import Candidate

class QuestionGenerator:
    """Decides next adaptive action and generates candidate-tailored interviewer questions."""

    DOMAIN_MAP: Dict[str, List[str]] = {
        "Senior AI Systems Engineer": [
            "Logistics & Supply Chain Exception Intelligence",
            "Real-time Financial Fraud Audit Search",
            "High-Throughput E-Commerce Recommendation Engine"
        ],
        "AI Research & Systems Engineer": [
            "Healthcare Clinical Trial Diagnostic Matching",
            "Cybersecurity Threat Intelligence Graph",
            "Automated Patent Prior-Art Discovery"
        ],
        "Applied AI Developer": [
            "Customer Support Multi-channel Routing",
            "Retail Inventory Optimization Assistant",
            "Smart Manufacturing Maintenance Alert Search"
        ]
    }

    @classmethod
    def select_transfer_domain(cls, candidate: Candidate, day_number: int) -> str:
        domains = cls.DOMAIN_MAP.get(candidate.target_role, [
            "Logistics Exception Tracking",
            "Healthcare Diagnostic Intelligence",
            "Financial Audit Search"
        ])
        return domains[day_number % len(domains)]

    @staticmethod
    def decide_next_action(
        eval_result_action: AdaptiveAction,
        is_expression_unclear: bool,
        current_topic_assessment: TopicAssessment,
        total_questions: int,
        covered_days_count: int,
        covered_days_list: List[int],
        all_topics: List[Tuple[CurriculumDay, Topic]],
        misconception_flagged: bool = False
    ) -> Tuple[AdaptiveAction, str, int, str, Optional[str]]:
        """
        Determines next adaptive action, next target topic, target depth, reason code, and pending evidence item.
        """
        pending_item = current_topic_assessment.pending_evidence_list[0] if current_topic_assessment.pending_evidence_list else None

        # 1. If candidate struggled or expressed "I don't know", recover with scaffolding
        if eval_result_action == AdaptiveAction.RECOVER:
            return (
                AdaptiveAction.RECOVER,
                current_topic_assessment.topic_id,
                current_topic_assessment.depth,
                "struggled_needs_scaffold",
                pending_item
            )

        # 2. If candidate has high knowledge but unclear expression, trigger Expression Scaffolding
        if is_expression_unclear or eval_result_action == AdaptiveAction.EXPRESSION_SCAFFOLD:
            return (
                AdaptiveAction.EXPRESSION_SCAFFOLD,
                current_topic_assessment.topic_id,
                current_topic_assessment.depth,
                "high_knowledge_unclear_expression",
                pending_item
            )

        # 3. If misconception was flagged, probe it
        if misconception_flagged or eval_result_action == AdaptiveAction.PROBE:
            return (
                AdaptiveAction.PROBE,
                current_topic_assessment.topic_id,
                current_topic_assessment.depth,
                "misconception_flagged",
                pending_item
            )

        # 4. Check for Cross-Domain Transfer Readiness (Level 4+ depth achieved)
        if current_topic_assessment.depth >= 4 and len(current_topic_assessment.evidence) >= 2:
            return (
                AdaptiveAction.TRANSFER,
                current_topic_assessment.topic_id,
                6,
                "ready_for_cross_domain_transfer",
                pending_item
            )

        # 5. If topic has sufficient evidence or depth >= 2, move to next curriculum day
        if len(current_topic_assessment.evidence) >= 1 or current_topic_assessment.depth >= 2:
            # First priority: find a topic on a curriculum day not yet covered
            for day, topic in all_topics:
                if day.day_number not in covered_days_list:
                    return (
                        AdaptiveAction.CHANGE_TOPIC,
                        topic.topic_id,
                        1,
                        f"switch_to_uncovered_day_{day.day_number}",
                        pending_item
                    )
            
            # Second priority: pick any unassessed topic
            for day, topic in all_topics:
                if topic.topic_id != current_topic_assessment.topic_id:
                    return (
                        AdaptiveAction.CHANGE_TOPIC,
                        topic.topic_id,
                        1,
                        "sufficient_evidence_switch_topic",
                        pending_item
                    )

        # 6. Default: GO_DEEPER on current topic
        next_depth = min(5, current_topic_assessment.depth + 1)
        return (
            AdaptiveAction.GO_DEEPER,
            current_topic_assessment.topic_id,
            next_depth,
            "strong_fundamentals",
            pending_item
        )

    @classmethod
    def generate_question(
        cls,
        action: AdaptiveAction,
        topic: Topic,
        day: CurriculumDay,
        target_depth: int,
        candidate: Optional[Candidate] = None,
        pending_evidence_item: Optional[str] = None,
        previous_answer: Optional[str] = None
    ) -> Tuple[str, InterviewDecision]:
        """Generates question text and constructs the structured InterviewDecision object."""
        scaffold_prompt = None
        transfer_domain = None
        
        if action == AdaptiveAction.TRANSFER:
            cand = candidate or Candidate(
                candidate_id="cand_demo",
                name="Demo",
                email="demo@skillproof.internal",
                is_synthetic_demo=True,
                background_summary="",
                target_role="Senior AI Systems Engineer"
            )
            transfer_domain = cls.select_transfer_domain(cand, day.day_number)

        if action == AdaptiveAction.RECOVER:
            scaffold_prompt = f"Simplify {topic.name} into basic functional elements"

        if action == AdaptiveAction.EXPRESSION_SCAFFOLD:
            scaffold_prompt = f"Structure explanation of {topic.name} into three parts"

        question_text = llm_service.generate_question_text(
            action=action,
            topic_name=topic.name,
            day_number=day.day_number,
            target_depth=target_depth,
            pending_evidence_item=pending_evidence_item,
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
