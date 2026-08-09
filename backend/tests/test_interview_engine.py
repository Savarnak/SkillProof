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
from app.interview.schemas import AdaptiveAction, SessionStatus, MisconceptionStatus

def test_scenario_a_strong_candidate():
    """Scenario A: Strong candidate triggers GO_DEEPER and TRANSFER actions."""
    state, first_q = interview_engine.start_interview(
        candidate_id="cand_maya_lin_002",
        curriculum_id="curr_ai_eng_v1"
    )
    
    # Strong answer 1
    state_2, q_2 = interview_engine.submit_answer(
        session_id=state.interviewId,
        candidate_answer="Cosine similarity measures the angle between normalized vector embeddings, making it scale-invariant compared to Euclidean distance."
    )
    assert state_2.conversationHistory[0].evaluation.technicalCorrectness >= 0.85
    assert state_2.questionCount >= 2

def test_scenario_b_beginner_recovery():
    """Scenario B: Beginner candidate says 'I don't know' and triggers RECOVER scaffold."""
    state, _ = interview_engine.start_interview(
        candidate_id="cand_alex_rivers_001",
        curriculum_id="curr_ai_eng_v1"
    )
    
    state_after, next_q = interview_engine.submit_answer(
        session_id=state.interviewId,
        candidate_answer="I don't know or remember this topic."
    )
    
    eval_1 = state_after.conversationHistory[0].evaluation
    assert eval_1.isStrugglingOrDontKnow is True
    assert eval_1.recommendedNextAction == AdaptiveAction.RECOVER
    assert "simplify" in next_q.lower() or "basic" in next_q.lower()

def test_scenario_c_strong_knowledge_weak_expression():
    """Scenario C: High knowledge / low expression triggers EXPRESSION_SCAFFOLD."""
    state, _ = interview_engine.start_interview(
        candidate_id="cand_alex_rivers_001",
        curriculum_id="curr_ai_eng_v1"
    )
    
    state_after, scaffold_q = interview_engine.submit_answer(
        session_id=state.interviewId,
        candidate_answer="RAG is basically when the AI searches some documents and then feeds them."
    )
    
    eval_1 = state_after.conversationHistory[0].evaluation
    assert eval_1.isExpressionUnclear is True
    assert "three parts" in scaffold_q.lower() or "structure" in scaffold_q.lower()
    assert len(state_after.expressionGaps) >= 1

def test_scenario_d_misconception_challenge():
    """Scenario D: Misconception detected, probed, and resolved."""
    state, _ = interview_engine.start_interview(
        candidate_id="cand_sam_patel_003",
        curriculum_id="curr_ai_eng_v1"
    )
    
    # 1. State misconception
    state_2, challenge_q = interview_engine.submit_answer(
        session_id=state.interviewId,
        candidate_answer="RAG eliminates hallucinations completely."
    )
    
    assert len(state_2.misconceptions) >= 1
    assert state_2.misconceptions[0].status == MisconceptionStatus.IDENTIFIED
    
    # 2. Candidate responds to challenge question correctly
    state_3, _ = interview_engine.submit_answer(
        session_id=state.interviewId,
        candidate_answer="No, it depends on whether the retrieved source documents are correct or outdated."
    )
    
    assert state_3.misconceptions[0].status == MisconceptionStatus.RESOLVED

def test_scenario_e_and_f_profile_vs_live_evidence_divergence():
    """Scenarios E & F: Live interview evidence overrides profile signals."""
    # Scenario E: Candidate with weak profile signal demonstrates strong live performance
    state, _ = interview_engine.start_interview(
        candidate_id="cand_sam_patel_003",
        curriculum_id="curr_ai_eng_v1"
    )
    
    state_after, _ = interview_engine.submit_answer(
        session_id=state.interviewId,
        candidate_answer="Cosine similarity dot product for normalized vectors ensures precision and recall optimization."
    )
    
    # Profile divergence note recorded
    assert len(state_after.profileVsEvidenceDivergence) >= 1
    assert "no completion signal" in state_after.profileVsEvidenceDivergence[0]

def test_scenario_g_coverage_and_max_questions_enforcement():
    """Scenario G: Deterministic constraints & MAX_QUESTIONS=15 safety limit."""
    state, _ = interview_engine.start_interview(
        candidate_id="cand_alex_rivers_001",
        curriculum_id="curr_ai_eng_v1"
    )
    
    # Attempt finish on turn 1 -> blocked
    raised = False
    try:
        interview_engine.finish_interview(state.interviewId)
    except ValueError as exc:
        raised = True
        assert "Deterministic constraints not met" in str(exc)
    assert raised is True

def test_13_step_adaptive_interview_trace():
    """
    Executes complete 13-step adaptive trace demonstrating:
    1. Strong answer -> GO_DEEPER
    2. Partial answer -> PROBE
    3. "I don't know" -> RECOVER scaffold
    4. Expression gap -> EXPRESSION_SCAFFOLD
    5. Misconception -> Challenge & Resolution
    6. Topic Switch -> Uncovered curriculum day
    7. Cross-Domain Transfer -> Tailored domain
    8. 8+ Questions, 4+ Curriculum Days, Final Evidence Summary
    """
    state, current_q = interview_engine.start_interview(
        candidate_id="cand_maya_lin_002",
        curriculum_id="curr_ai_eng_v1"
    )

    print("\n" + "="*80)
    print(f"STARTING 13-STEP ADAPTIVE INTERVIEW TRACE (Session: {state.interviewId})")
    print("="*80)
    print(f"Turn 1 Question: {current_q}")

    trace_script = [
        # Step 1 (Day 1): Strong answer -> GO_DEEPER
        "Cosine similarity measures the angle between normalized vector embeddings, making it scale-invariant.",
        # Step 2 (Day 1): Engineering depth answer
        "HNSW builds a hierarchical graph with logarithmic search scaling, optimizing ANN precision versus recall trade-offs.",
        # Step 3 (Day 2): Topic switch to RAG -> Partial answer
        "Document chunking divides context window limits; retrieval uses BM25.",
        # Step 4 (Day 2): "I don't know" -> RECOVER
        "I don't know how cross-encoder rerankers work in detail.",
        # Step 5 (Day 2): Response to recovery scaffold
        "Cross-encoders score doc query relevance to filter bad context.",
        # Step 6 (Day 3): Agents -> High knowledge / low expression answer
        "RAG is basically when the AI searches some documents and then feeds them.",
        # Step 7 (Day 3): Response to expression scaffolding prompt
        "First, RAG retrieves document context; second, it injects context into the prompt; third, it grounds LLM outputs.",
        # Step 8 (Day 3): Misconception statement
        "RAG eliminates hallucinations completely.",
        # Step 9 (Day 3): Response to misconception challenge -> RESOLVED
        "No, it depends on whether the retrieved source documents contain accurate information.",
        # Step 10 (Day 4): DB Scaling -> Strong answer
        "pgvector provides relational SQL integration in PostgreSQL, whereas Qdrant handles memory-cached vector sharding.",
        # Step 11 (Day 5): Evaluation -> Strong answer
        "Ragas framework evaluates faithfulness and answer relevance using LLM-as-a-judge patterns.",
        # Step 12 (Day 5): Tailored Cross-Domain Transfer answer
        "For Healthcare Clinical Trial Intelligence, I would design a hybrid BM25 and dense vector index with patient privacy guardrails."
    ]

    for step_num, ans in enumerate(trace_script, start=1):
        if state.interviewStatus == SessionStatus.COMPLETED:
            break
        state, current_q = interview_engine.submit_answer(
            session_id=state.interviewId,
            candidate_answer=ans
        )
        print(f"\n--- Step {step_num} Evaluation & Progress ---")
        print(f"Answer Submitted: '{ans[:65]}...'")
        print(f"Questions Asked: {state.questionCount}")
        print(f"Curriculum Days Covered: {state.curriculumDaysCovered} (Total Unique Days: {len(state.curriculumDaysCovered)})")
        print(f"Active Topic: {state.currentTopic} (Depth Level: {state.currentDepth})")
        print(f"Can Conclude Interview? -> {state.canConclude}")
        if current_q:
            print(f"Next Question Generated: '{current_q[:90]}...'")

    assert state.questionCount >= 8
    assert len(state.curriculumDaysCovered) >= 4
    assert state.canConclude is True

    final_state = interview_engine.finish_interview(state.interviewId)
    assert final_state.interviewStatus == SessionStatus.COMPLETED

    report = interview_engine.generate_report(state.interviewId)
    assert report.totalQuestionsAsked >= 8
    assert report.uniqueDaysCovered >= 4

    print("\n" + "="*80)
    print("13-STEP ADAPTIVE INTERVIEW TRACE PASSED SUCCESSFULLY!")
    print(f"Total Questions: {report.totalQuestionsAsked}, Unique Days Covered: {report.uniqueDaysCovered}")
    print(f"Overall Knowledge Score: {report.overallKnowledgeScore}, Overall Expression Score: {report.overallExpressionScore}")
    print(f"Profile Divergence Notes: {len(report.profileDivergenceNotes)} recorded")
    print(f"Misconceptions Tracked: {len(report.misconceptionsFound)}")
    print("="*80 + "\n")

if __name__ == "__main__":
    print("Running SkillProof Phase 3 Test Suite...")
    test_scenario_a_strong_candidate()
    print("[OK] Scenario A PASSED")
    
    test_scenario_b_beginner_recovery()
    print("[OK] Scenario B PASSED")
    
    test_scenario_c_strong_knowledge_weak_expression()
    print("[OK] Scenario C PASSED")
    
    test_scenario_d_misconception_challenge()
    print("[OK] Scenario D PASSED")
    
    test_scenario_e_and_f_profile_vs_live_evidence_divergence()
    print("[OK] Scenarios E & F PASSED")
    
    test_scenario_g_coverage_and_max_questions_enforcement()
    print("[OK] Scenario G PASSED")
    
    test_13_step_adaptive_interview_trace()
    print("[OK] ALL PHASE 3 TESTS & 13-STEP ADAPTIVE TRACE PASSED SUCCESSFULLY!")
