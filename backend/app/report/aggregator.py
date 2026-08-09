from typing import List, Dict, Any, Tuple
from app.interview.schemas import InterviewState, QuestionTurn, TopicAssessment
from app.report.schemas import WeightedScoreBreakdown, TopicEvidenceExpander

class ReportAggregator:
    """Aggregates evidence across turns and calculates transparent weighted readiness scores."""

    WEIGHTS = {
        "technicalKnowledge": 0.30,
        "reasoning": 0.20,
        "application": 0.20,
        "expression": 0.15,
        "transfer": 0.15
    }

    @classmethod
    def calculate_weighted_scores(cls, state: InterviewState) -> WeightedScoreBreakdown:
        assessed = [t for t in state.topicsAssessed.values() if t.knowledge > 0.0 or len(t.evidence) > 0]
        
        if assessed:
            avg_know = sum(t.knowledge for t in assessed) / len(assessed)
            avg_app = sum(t.application for t in assessed) / len(assessed)
            avg_exp = sum(t.expression for t in assessed) / len(assessed)
            avg_reas = (avg_know + avg_app) / 2.0
        else:
            avg_know = avg_app = avg_exp = avg_reas = 0.50

        avg_trans = 0.85 if len(state.transferChallengesUsed) > 0 else 0.50

        weighted_val = (
            avg_know * cls.WEIGHTS["technicalKnowledge"] +
            avg_reas * cls.WEIGHTS["reasoning"] +
            avg_app * cls.WEIGHTS["application"] +
            avg_exp * cls.WEIGHTS["expression"] +
            avg_trans * cls.WEIGHTS["transfer"]
        )

        overall_readiness = max(0, min(100, int(round(weighted_val * 100))))

        return WeightedScoreBreakdown(
            technicalKnowledge=round(avg_know, 2),
            reasoning=round(avg_reas, 2),
            application=round(avg_app, 2),
            expression=round(avg_exp, 2),
            transfer=round(avg_trans, 2),
            overallReadiness=overall_readiness
        )

    @classmethod
    def build_topic_evidence_expanders(cls, state: InterviewState) -> List[TopicEvidenceExpander]:
        expanders: List[TopicEvidenceExpander] = []
        
        # Build index of questions per topic
        questions_per_topic: Dict[str, List[int]] = {}
        for turn in state.conversationHistory:
            if turn.topic_id not in questions_per_topic:
                questions_per_topic[turn.topic_id] = []
            questions_per_topic[turn.topic_id].append(turn.turn_index)

        for topic_id, topic_assessment in state.topicsAssessed.items():
            sources = questions_per_topic.get(topic_id, [])
            ev_count = len(topic_assessment.evidence)
            
            # Determine status tag
            if len(sources) == 0:
                status_tag = "Not Assessed"
                score_val = 0.0
                confidence_val = 0.0
            elif topic_assessment.knowledge >= 0.80 and ev_count >= 2:
                status_tag = "Strong"
                score_val = topic_assessment.knowledge
                confidence_val = min(0.95, 0.60 + ev_count * 0.15)
            elif topic_assessment.knowledge >= 0.60:
                status_tag = "Demonstrated"
                score_val = topic_assessment.knowledge
                confidence_val = min(0.90, 0.50 + ev_count * 0.15)
            elif topic_assessment.knowledge > 0.0:
                status_tag = "Developing"
                score_val = topic_assessment.knowledge
                confidence_val = 0.50
            else:
                status_tag = "Insufficient Evidence"
                score_val = 0.20
                confidence_val = 0.40

            expanders.append(
                TopicEvidenceExpander(
                    topic_id=topic_id,
                    topic_name=topic_assessment.topic_name,
                    score=score_val,
                    confidence=confidence_val,
                    evidenceCount=ev_count,
                    sourceQuestions=sources,
                    evidenceQuotes=topic_assessment.evidence,
                    statusTag=status_tag
                )
            )

        return expanders

report_aggregator = ReportAggregator()
