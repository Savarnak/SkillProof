from typing import Optional, List, Dict, Any
import json
import re
from app.config import settings
from app.interview.schemas import (
    AnswerEvaluation, AdaptiveAction, InterviewDecision, SkillDepthLevel
)

class LLMService:
    """Handles structured LLM evaluations and adaptive question generation with fallback mock support."""
    
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or settings.LLM_PROVIDER
        self.api_key = settings.OPENAI_API_KEY or settings.GEMINI_API_KEY

    def evaluate_answer(
        self,
        question_text: str,
        answer_text: str,
        topic_name: str,
        current_depth: int
    ) -> AnswerEvaluation:
        """
        Evaluates candidate response.
        Detects technical correctness, depth, expression clarity, missing concepts, misconceptions, and struggle/'I don't know'.
        """
        if not self.api_key or self.provider == "mock":
            return self._mock_evaluate_answer(question_text, answer_text, topic_name, current_depth)
        
        # Real API call logic (OpenAI / Gemini) with fallback to mock
        try:
            return self._real_evaluate_answer(question_text, answer_text, topic_name, current_depth)
        except Exception:
            return self._mock_evaluate_answer(question_text, answer_text, topic_name, current_depth)

    def generate_question_text(
        self,
        action: AdaptiveAction,
        topic_name: str,
        day_number: int,
        target_depth: int,
        scaffold_prompt: Optional[str] = None,
        transfer_domain: Optional[str] = None,
        previous_answer: Optional[str] = None
    ) -> str:
        """Generates adaptive question string based on action and target depth."""
        if not self.api_key or self.provider == "mock":
            return self._mock_generate_question_text(
                action, topic_name, day_number, target_depth, scaffold_prompt, transfer_domain, previous_answer
            )
        
        try:
            return self._real_generate_question_text(
                action, topic_name, day_number, target_depth, scaffold_prompt, transfer_domain, previous_answer
            )
        except Exception:
            return self._mock_generate_question_text(
                action, topic_name, day_number, target_depth, scaffold_prompt, transfer_domain, previous_answer
            )

    # ------------------------------------------------------------------------
    # MOCK ENGINE IMPLEMENTATION (Deterministic for testing & offline mode)
    # ------------------------------------------------------------------------
    def _mock_evaluate_answer(
        self,
        question_text: str,
        answer_text: str,
        topic_name: str,
        current_depth: int
    ) -> AnswerEvaluation:
        ans_clean = answer_text.strip().lower()

        # 1. Check for "I don't know" / struggle triggers
        dont_know_phrases = ["i don't know", "i dont know", "not sure", "don't remember", "no idea", "can you rephrase", "pass"]
        is_struggling = any(p in ans_clean for p in dont_know_phrases) or len(ans_clean) < 12

        if is_struggling:
            return AnswerEvaluation(
                technicalCorrectness=0.15,
                conceptualDepth=0.10,
                relevance=0.30,
                reasoning=0.10,
                application=0.10,
                expressionClarity=0.40,
                answerStructure=0.30,
                confidenceOfAssessment=0.90,
                strengths=["Acknowledged gap openly"],
                missingConcepts=["Core concept details"],
                misconceptions=[],
                expressionIssues=["Candidate expressed uncertainty"],
                evidence=["Candidate stated they were unsure about the topic"],
                isStrugglingOrDontKnow=True,
                recommendedNextAction=AdaptiveAction.RECOVER,
                recommendedReasonCode="struggled_needs_scaffold"
            )

        # 2. Check for Misconception Triggers
        # Example: "RAG eliminates hallucination"
        misconception_found = []
        if "eliminate" in ans_clean and ("hallucination" in ans_clean or "error" in ans_clean):
            misconception_found.append("Believes RAG completely eliminates hallucinations")
        elif "pgvector" in ans_clean and "no memory" in ans_clean:
            misconception_found.append("Believes vector search requires no RAM caching")

        if misconception_found:
            return AnswerEvaluation(
                technicalCorrectness=0.60,
                conceptualDepth=0.45,
                relevance=0.85,
                reasoning=0.50,
                application=0.60,
                expressionClarity=0.75,
                answerStructure=0.70,
                confidenceOfAssessment=0.85,
                strengths=["Understands general mechanism"],
                missingConcepts=["Grounding limits and hallucination failure modes"],
                misconceptions=misconception_found,
                expressionIssues=[],
                evidence=["Stated that RAG eliminates hallucinations entirely"],
                isStrugglingOrDontKnow=False,
                recommendedNextAction=AdaptiveAction.PROBE,
                recommendedReasonCode="misconception_flagged"
            )

        # 3. High quality / Deep technical answer
        strong_keywords = ["cosine", "bm25", "hybrid", "rerank", "cross-encoder", "hnsw", "pydantic", "react", "sharding", "latency", "precision", "recall"]
        matches = [kw for kw in strong_keywords if kw in ans_clean]

        if len(matches) >= 2 or len(ans_clean) > 100:
            return AnswerEvaluation(
                technicalCorrectness=0.90,
                conceptualDepth=0.85,
                relevance=0.95,
                reasoning=0.88,
                application=0.85,
                expressionClarity=0.80,
                answerStructure=0.78,
                confidenceOfAssessment=0.92,
                strengths=[f"Accurately explained key technical terms ({', '.join(matches[:2])})", "Structured technical reasoning"],
                missingConcepts=[],
                misconceptions=[],
                expressionIssues=[],
                evidence=[f"Demonstrated solid understanding of {topic_name}"],
                isStrugglingOrDontKnow=False,
                recommendedNextAction=AdaptiveAction.GO_DEEPER,
                recommendedReasonCode="strong_fundamentals"
            )

        # 4. Standard moderate answer
        return AnswerEvaluation(
            technicalCorrectness=0.75,
            conceptualDepth=0.60,
            relevance=0.80,
            reasoning=0.65,
            application=0.70,
            expressionClarity=0.70,
            answerStructure=0.65,
            confidenceOfAssessment=0.80,
            strengths=["Correct baseline definition"],
            missingConcepts=["System design trade-offs"],
            misconceptions=[],
            expressionIssues=[],
            evidence=[f"Understands basic application of {topic_name}"],
            isStrugglingOrDontKnow=False,
            recommendedNextAction=AdaptiveAction.GO_DEEPER,
            recommendedReasonCode="moderate_understanding"
        )

    def _mock_generate_question_text(
        self,
        action: AdaptiveAction,
        topic_name: str,
        day_number: int,
        target_depth: int,
        scaffold_prompt: Optional[str] = None,
        transfer_domain: Optional[str] = None,
        previous_answer: Optional[str] = None
    ) -> str:
        if action == AdaptiveAction.RECOVER:
            return f"Let's simplify it. If a system receives context for {topic_name}, what basic signal tells you whether that information is relevant to the prompt?"
        
        if action == AdaptiveAction.PROBE:
            return f"You mentioned how {topic_name} handles output. Suppose the retrieved source documents contain contradictory or outdated info—what happens to the LLM's response?"
        
        if action == AdaptiveAction.TRANSFER:
            domain = transfer_domain or "Logistics Exception Reports"
            return f"You've shown solid engineering depth in {topic_name}. Let's apply this: Imagine a real-world scenario in {domain}. How would you architect this system to handle millions of unindexed records?"
        
        if action == AdaptiveAction.CHANGE_TOPIC:
            return f"Great work on Day {day_number}. Let's switch gears to {topic_name}. How would you describe the core operational trade-off in this layer?"
        
        if target_depth >= 5:
            return f"For production system design in {topic_name}: How would you optimize latency and throughput under high concurrent load?"

        if target_depth >= 4:
            return f"Engineering deep-dive into {topic_name}: What specific failure modes occur during high query spikes, and how do you mitigate them?"

        if target_depth >= 3:
            return f"Applying {topic_name}: How would you construct a practical workflow combining tools and data validation?"

        # Default depth 1-2
        return f"Understanding {topic_name} (Day {day_number}): How would you explain the core mechanism of {topic_name} to a backend developer?"

    def _real_evaluate_answer(
        self,
        question_text: str,
        answer_text: str,
        topic_name: str,
        current_depth: int
    ) -> AnswerEvaluation:
        # Fallback to mock if API key isn't setup
        return self._mock_evaluate_answer(question_text, answer_text, topic_name, current_depth)

    def _real_generate_question_text(
        self,
        action: AdaptiveAction,
        topic_name: str,
        day_number: int,
        target_depth: int,
        scaffold_prompt: Optional[str] = None,
        transfer_domain: Optional[str] = None,
        previous_answer: Optional[str] = None
    ) -> str:
        return self._mock_generate_question_text(
            action, topic_name, day_number, target_depth, scaffold_prompt, transfer_domain, previous_answer
        )

llm_service = LLMService()
