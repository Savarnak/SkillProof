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

        # 5. Check if mandatory 4-day coverage requires exploring an uncovered curriculum day
        # We need at least 4 curriculum days by Question 8. If we are at Question 4+ and need more days:
        needs_mandatory_coverage_switch = (
            total_questions >= 4 and
            covered_days_count < 4
        )

        topic_completed = (
            current_topic_assessment.depth >= 4 or
            len(current_topic_assessment.evidence) >= 2
        )

        if needs_mandatory_coverage_switch or topic_completed:
            # Priority 1: Find topic from an uncovered curriculum day
            uncovered_day_topics = [
                (d, t) for d, t in all_topics
                if d.day_number not in covered_days_list and t.topic_id != current_topic_assessment.topic_id
            ]
            if uncovered_day_topics:
                next_day, next_topic = uncovered_day_topics[0]
                reason = f"switching_to_uncovered_day_{next_day.day_number}_for_mandatory_coverage" if needs_mandatory_coverage_switch else "completed_current_topic_advancing_curriculum"
                return (
                    AdaptiveAction.CHANGE_TOPIC,
                    next_topic.topic_id,
                    1,
                    reason,
                    pending_item
                )

            # Priority 2: Pick any other topic not currently active
            other_topics = [(d, t) for d, t in all_topics if t.topic_id != current_topic_assessment.topic_id]
            if other_topics:
                next_day, next_topic = other_topics[0]
                return (
                    AdaptiveAction.CHANGE_TOPIC,
                    next_topic.topic_id,
                    1,
                    "switching_topic_balanced_coverage",
                    pending_item
                )

        # 6. Default: Advance Depth Ladder on Current Topic (Depth 1 -> 2 -> 3 -> 4 -> 5)
        next_depth = min(5, current_topic_assessment.depth + 1)
        reason_code = f"candidate_demonstrated_depth_{current_topic_assessment.depth}_advancing_to_depth_{next_depth}"
        return (
            AdaptiveAction.GO_DEEPER,
            current_topic_assessment.topic_id,
            next_depth,
            reason_code,
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
        previous_answer: Optional[str] = None,
        asked_questions: Optional[List[str]] = None,
        previous_topic_name: Optional[str] = None
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
                target_role="Software Engineer",
                completed_missions=[]
            )
            transfer_domain = cls.select_transfer_domain(cand, day.day_number)
        elif action == AdaptiveAction.EXPRESSION_SCAFFOLD:
            scaffold_prompt = "high_knowledge_unclear_expression"

        # Generate base question text
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

        # Prevent duplicate question texts in the same session for GO_DEEPER actions
        if asked_questions and action == AdaptiveAction.GO_DEEPER:
            current_try_depth = target_depth
            attempts = 0
            while question_text in asked_questions and attempts < 5:
                current_try_depth = (current_try_depth % 5) + 1
                question_text = llm_service.generate_question_text(
                    action=action,
                    topic_name=topic.name,
                    day_number=day.day_number,
                    target_depth=current_try_depth,
                    pending_evidence_item=pending_evidence_item,
                    scaffold_prompt=scaffold_prompt,
                    transfer_domain=transfer_domain,
                    previous_answer=previous_answer
                )
                attempts += 1

        # Format natural transition for CHANGE_TOPIC actions
        if action == AdaptiveAction.CHANGE_TOPIC and previous_topic_name:
            question_text = f"Your technical explanation of {previous_topic_name} is solid. Let's build on that and move into {topic.name}: {question_text}"

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
