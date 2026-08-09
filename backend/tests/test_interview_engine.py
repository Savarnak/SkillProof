try:
    import pytest
except ImportError:
    pytest = None

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.interview.engine import interview_engine
from app.interview.schemas import AdaptiveAction, SessionStatus

def test_interview_initialization():
    """Verify session starts cleanly and initial state is initialized."""
    state, first_q = interview_engine.start_interview(
        candidate_id="cand_alex_rivers_001",
        curriculum_id="curr_ai_eng_v1"
    )
    
    assert state.interviewId is not None
    assert state.questionCount == 1
    assert len(state.conversationHistory) == 1
    assert len(first_q) > 10
    assert state.interviewStatus == SessionStatus.IN_PROGRESS
    assert state.canConclude is False

def test_cannot_finish_early():
    """Verify engine blocks finish_interview if questionCount < 8 or uniqueDays < 4."""
    state, _ = interview_engine.start_interview(
        candidate_id="cand_alex_rivers_001",
        curriculum_id="curr_ai_eng_v1"
    )
    
    # Attempt finish on question 1
    raised = False
    try:
        interview_engine.finish_interview(state.interviewId)
    except ValueError as exc:
        raised = True
        assert "Deterministic constraints not met" in str(exc)
    
    assert raised is True


def test_dont_know_triggers_recovery():
    """Verify 'I don't know' triggers RECOVER action and scaffolding prompt."""
    state, first_q = interview_engine.start_interview(
        candidate_id="cand_alex_rivers_001",
        curriculum_id="curr_ai_eng_v1"
    )
    
    state_after, next_q = interview_engine.submit_answer(
        session_id=state.interviewId,
        candidate_answer="I don't know or remember this topic."
    )
    
    # Turn 1 evaluation should detect struggle
    turn1_eval = state_after.conversationHistory[0].evaluation
    assert turn1_eval is not None
    assert turn1_eval.isStrugglingOrDontKnow is True
    assert turn1_eval.recommendedNextAction == AdaptiveAction.RECOVER
    assert "simplify" in next_q.lower() or "basic" in next_q.lower()

def test_misconception_detection():
    """Verify stating a misconception is recorded in state.misconceptions."""
    state, _ = interview_engine.start_interview(
        candidate_id="cand_sam_patel_003",
        curriculum_id="curr_ai_eng_v1"
    )
    
    state_after, _ = interview_engine.submit_answer(
        session_id=state.interviewId,
        candidate_answer="RAG eliminates hallucinations completely."
    )
    
    assert len(state_after.misconceptions) >= 1
    assert "hallucination" in state_after.misconceptions[0].misconception.lower()


def test_full_simulated_8_turn_interview_trace():
    """
    Simulates a full 8+ question interview covering at least 4 curriculum days,
    verifying deterministic constraints enforcement, adaptive depth, and final report generation.
    """
    state, current_q = interview_engine.start_interview(
        candidate_id="cand_maya_lin_002",
        curriculum_id="curr_ai_eng_v1"
    )
    
    print("\n" + "="*80)
    print(f"STARTING SIMULATED INTERVIEW TRACE (Session: {state.interviewId})")
    print("="*80)
    print(f"Turn 1 Question: {current_q}")

    answers_script = [
        # Turn 1 (Day 1): Strong answer
        "Cosine similarity measures the angle between normalized vector embeddings, making it scale-invariant compared to Euclidean distance.",
        # Turn 2 (Day 1): Engineering depth answer
        "HNSW builds a hierarchical graph with logarithmic search scaling, optimizing ANN precision versus recall trade-offs.",
        # Turn 3 (Day 2): Topic switch to RAG
        "Chunk size dictates retrieval context boundaries; hybrid search combines BM25 lexical indexing with dense vector retrieval using reciprocal rank fusion.",
        # Turn 4 (Day 2): Cross-encoder / reranking
        "Cross-encoders score document-query pairs joint-attentively, reducing RAG retrieval failure modes and hallucination rates.",
        # Turn 5 (Day 3): Agents / Function calling
        "Pydantic schemas enforce JSON output structures for OpenAI function calling, preventing schema parsing exceptions.",
        # Turn 6 (Day 3): ReAct loop
        "Stateful execution loops manage agent tool execution cycles with guardrails to prevent infinite retries.",
        # Turn 7 (Day 4): DB Scaling
        "pgvector allows unified SQL querying within PostgreSQL, whereas specialized vector databases offer sharded memory optimization for billion-scale vectors.",
        # Turn 8 (Day 5): Evaluation
        "Ragas and LLM-as-a-judge patterns evaluate answer relevance, faithfulness, and semantic ground truth across benchmark datasets."
    ]

    for turn_num, ans in enumerate(answers_script, start=1):
        state, current_q = interview_engine.submit_answer(
            session_id=state.interviewId,
            candidate_answer=ans
        )
        print(f"\n--- Turn {turn_num} Evaluation & Progress ---")
        print(f"Answer Submitted: '{ans[:60]}...'")
        print(f"Questions Asked: {state.questionCount}")
        print(f"Curriculum Days Covered: {state.curriculumDaysCovered} (Total Unique Days: {len(state.curriculumDaysCovered)})")
        print(f"Active Topic: {state.currentTopic} (Depth Level: {state.currentDepth})")
        print(f"Can Conclude Interview? -> {state.canConclude}")
        if current_q:
            print(f"Next Question Generated: '{current_q}'")

    # Verify constraints satisfied
    assert state.questionCount >= 8
    assert len(state.curriculumDaysCovered) >= 4
    assert state.canConclude is True

    # Complete interview
    final_state = interview_engine.finish_interview(state.interviewId)
    assert final_state.interviewStatus == SessionStatus.COMPLETED

    # Generate report
    report = interview_engine.generate_report(state.interviewId)
    assert report.totalQuestionsAsked >= 8
    assert report.uniqueDaysCovered >= 4
    assert report.overallKnowledgeScore >= 0.70
    assert len(report.answerRefinementSuggestions) >= 1

    print("\n" + "="*80)
    print("SIMULATED INTERVIEW TRACE PASSED SUCCESSFULLY!")
    print(f"Total Questions: {report.totalQuestionsAsked}, Unique Days Covered: {report.uniqueDaysCovered}")
    print(f"Knowledge Score: {report.overallKnowledgeScore}, Expression Score: {report.overallExpressionScore}")
    print("="*80 + "\n")

if __name__ == "__main__":
    print("Running SkillProof Phase 2 Test Suite...")
    test_interview_initialization()
    print("[OK] test_interview_initialization PASSED")
    
    test_cannot_finish_early()
    print("[OK] test_cannot_finish_early PASSED")
    
    test_dont_know_triggers_recovery()
    print("[OK] test_dont_know_triggers_recovery PASSED")
    
    test_misconception_detection()
    print("[OK] test_misconception_detection PASSED")
    
    test_full_simulated_8_turn_interview_trace()
    print("[OK] ALL PHASE 2 TESTS PASSED SUCCESSFULLY!")


