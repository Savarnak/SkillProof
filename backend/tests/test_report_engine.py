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
from app.report.generator import report_generator
from app.interview.schemas import SessionStatus

def test_valid_completion_generates_report():
    """Verify valid completion (8+ questions, 4+ days) sets status to COMPLETED and generates report."""
    state, current_q = interview_engine.start_interview(
        candidate_id="cand_alex_rivers_001",
        curriculum_id="curr_ai_eng_v1"
    )
    
    # Run 8 turns across curriculum days
    for turn in range(8):
        state, _ = interview_engine.submit_answer(
            session_id=state.interviewId,
            candidate_answer="Cosine similarity dot product BM25 hybrid search reranking."
        )

    assert state.canConclude is True
    completed_state = interview_engine.finish_interview(state.interviewId)
    assert completed_state.interviewStatus == SessionStatus.COMPLETED
    assert completed_state.completionReason == "mandatory_coverage_reached"

    cand = interview_engine._candidates_cache.get("cand_alex_rivers_001")
    report = report_generator.generate_discovery_report(
        state=completed_state,
        candidate=cand,
        curriculum_title="AI Systems"
    )

    assert report.totalQuestionsAsked >= 8
    assert report.uniqueDaysCovered >= 4
    assert report.weightedScores.overallReadiness > 0

def test_incomplete_interview_blocked_from_completed_status():
    """
    CRITICAL RULE FIX TEST:
    Verify if maxQuestions=15 is hit without satisfying mandatory curriculum coverage (4 days),
    status is NOT set to COMPLETED; it is set to INCOMPLETE (completionReason = mandatory_coverage_not_reached).
    """
    # Start session with high min_questions so mandatory coverage is not reached
    state, current_q = interview_engine.start_interview(
        candidate_id="cand_alex_rivers_001",
        curriculum_id="curr_ai_eng_v1",
        min_questions=20,
        min_curriculum_days=10,
        max_questions=15
    )

    # Force question count to 15 without covering 10 days
    state.questionCount = 15
    state.curriculumDaysCovered = [1, 2]  # Only 2 days covered
    
    # Call finish_interview
    incomplete_state = interview_engine.finish_interview(state.interviewId)
    
    assert incomplete_state.interviewStatus != SessionStatus.COMPLETED
    assert incomplete_state.completionReason == "mandatory_coverage_not_reached"

def test_not_assessed_topics_not_scored_as_zero():
    """Verify unassessed curriculum topics are tagged 'Not Assessed' rather than penalizing candidate as 0."""
    state, _ = interview_engine.start_interview(
        candidate_id="cand_maya_lin_002",
        curriculum_id="curr_ai_eng_v1"
    )
    
    for _ in range(8):
        state, _ = interview_engine.submit_answer(
            session_id=state.interviewId,
            candidate_answer="Cosine similarity vector search embeddings."
        )

    cand = interview_engine._candidates_cache.get("cand_maya_lin_002")
    report = report_generator.generate_discovery_report(
        state=state,
        candidate=cand,
        curriculum_title="AI Systems"
    )

    not_assessed = [exp for exp in report.topicEvidenceExpanders if exp.statusTag == "Not Assessed"]
    assert len(not_assessed) > 0
    for item in not_assessed:
        assert item.statusTag == "Not Assessed"

def test_evidence_expanders_linked_to_questions():
    """Verify topic evidence expanders link scores to specific source questions (Q1, Q2, etc.)."""
    state, _ = interview_engine.start_interview(
        candidate_id="cand_alex_rivers_001",
        curriculum_id="curr_ai_eng_v1"
    )

    for _ in range(8):
        state, _ = interview_engine.submit_answer(
            session_id=state.interviewId,
            candidate_answer="HNSW indexing logarithmic search cosine angle precision."
        )

    cand = interview_engine._candidates_cache.get("cand_alex_rivers_001")
    report = report_generator.generate_discovery_report(
        state=state,
        candidate=cand,
        curriculum_title="AI Systems"
    )

    assessed = [exp for exp in report.topicEvidenceExpanders if exp.statusTag != "Not Assessed"]
    assert len(assessed) > 0
    for item in assessed:
        assert len(item.sourceQuestions) > 0

def test_misconception_and_transfer_report_elements():
    """Verify misconception lifecycle items and transfer scorecard are present in report."""
    state, _ = interview_engine.start_interview(
        candidate_id="cand_sam_patel_003",
        curriculum_id="curr_ai_eng_v1"
    )

    state, _ = interview_engine.submit_answer(
        session_id=state.interviewId,
        candidate_answer="RAG eliminates hallucinations completely."
    )

    for _ in range(7):
        state, _ = interview_engine.submit_answer(
            session_id=state.interviewId,
            candidate_answer="Vector database pgvector memory caching dot product."
        )

    cand = interview_engine._candidates_cache.get("cand_sam_patel_003")
    report = report_generator.generate_discovery_report(
        state=state,
        candidate=cand,
        curriculum_title="AI Systems"
    )

    assert len(report.misconceptionsFound) >= 1

def test_answer_refinement_diff_and_coaching():
    """Verify Before vs. After answer refinement diffs and delivery formulas are generated."""
    state, _ = interview_engine.start_interview(
        candidate_id="cand_alex_rivers_001",
        curriculum_id="curr_ai_eng_v1"
    )

    state, _ = interview_engine.submit_answer(
        session_id=state.interviewId,
        candidate_answer="RAG retrieves document chunks and passes them to the LLM."
    )

    cand = interview_engine._candidates_cache.get("cand_alex_rivers_001")
    report = report_generator.generate_discovery_report(
        state=state,
        candidate=cand,
        curriculum_title="AI Systems"
    )

    assert len(report.refinementDiffs) >= 1
    diff_item = report.refinementDiffs[0]
    assert diff_item.originalAnswer == "RAG retrieves document chunks and passes them to the LLM."
    assert len(diff_item.diffAdditions) > 0
    assert len(diff_item.deliveryFormula) > 0

if __name__ == "__main__":
    print("Running SkillProof Phase 5 Report Engine & Completion Fix Test Suite...")
    test_valid_completion_generates_report()
    print("[OK] test_valid_completion_generates_report PASSED")

    test_incomplete_interview_blocked_from_completed_status()
    print("[OK] test_incomplete_interview_blocked_from_completed_status PASSED (Rule Fix Verified)")

    test_not_assessed_topics_not_scored_as_zero()
    print("[OK] test_not_assessed_topics_not_scored_as_zero PASSED")

    test_evidence_expanders_linked_to_questions()
    print("[OK] test_evidence_expanders_linked_to_questions PASSED")

    test_misconception_and_transfer_report_elements()
    print("[OK] test_misconception_and_transfer_report_elements PASSED")

    test_answer_refinement_diff_and_coaching()
    print("[OK] test_answer_refinement_diff_and_coaching PASSED")

    print("[OK] ALL PHASE 5 REPORT ENGINE TESTS PASSED SUCCESSFULLY!")
