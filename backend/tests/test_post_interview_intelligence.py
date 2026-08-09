import sys
import json
import urllib.request
import time
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.interview.engine import interview_engine
from app.report.generator import report_generator
from app.schemas.candidate import Candidate
from app.interview.schemas import AdaptiveAction, TopicStatus, MisconceptionStatus, MisconceptionItem, QuestionTurn, AnswerEvaluation

BASE_URL = "http://127.0.0.1:8000"

def post_json(url: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def test_post_interview_intelligence():
    print("================================================================================")
    print("STARTING POST-INTERVIEW INTELLIGENCE & ANSWER COACH TEST SUITE")
    print("================================================================================")

    # -------------------------------------------------------------------------
    # TEST A: Strong Technical + Poor Expression
    # -------------------------------------------------------------------------
    print("\n--- TEST A: Strong Technical + Poor Expression ---")
    state_a, _ = interview_engine.start_interview(candidate_id="cand_test_a", curriculum_id="curr_ai_eng_v1")
    sid_a = state_a.interviewId

    # Candidate provides deep concept but with informal phrasing ("basically...")
    ans_a1 = "Basically, cosine similarity looks at vector angles and direction metrics rather than distance to compare embeddings."
    interview_engine.submit_answer(sid_a, ans_a1)

    cand_a = Candidate(candidate_id="cand_test_a", name="Alex (Test A)", email="a@test.internal", is_synthetic_demo=True, background_summary="", target_role="AI Engineer", completed_missions=[])
    rep_a = report_generator.generate_discovery_report(state_a, cand_a, "AI Engineering Curriculum")

    print(f"Insight Show: {rep_a.knowledgeVsExpressionInsight.show}")
    print(f"Headline: '{rep_a.knowledgeVsExpressionInsight.headline}'")
    assert rep_a.knowledgeVsExpressionInsight.show is True or rep_a.showKnowledgeVsExpressionInsight is True, "Knowledge vs Expression insight should trigger"
    assert "knew it" in rep_a.knowledgeVsExpressionInsight.headline.lower() or "strong" in rep_a.insightMessage.lower(), "Headline should reflect 'You knew it. You just didn't show it clearly.'"
    print("[OK] TEST A PASSED")

    # -------------------------------------------------------------------------
    # TEST B: Weak Technical + Clear Expression
    # -------------------------------------------------------------------------
    print("\n--- TEST B: Weak Technical + Clear Expression ---")
    state_b, _ = interview_engine.start_interview(candidate_id="cand_test_b", curriculum_id="curr_ai_eng_v1")
    sid_b = state_b.interviewId

    ans_b1 = "I can explain this clearly in three structured parts: First, vector search finds data. Second, it uses databases. Third, it is used in production."
    state_b.conversationHistory[0].evaluation = AnswerEvaluation(
        technicalCorrectness=0.40,
        conceptualDepth=0.35,
        relevance=0.70,
        reasoning=0.40,
        application=0.40,
        expressionClarity=0.90,
        answerStructure=0.85,
        confidenceOfAssessment=0.85,
        strengths=["Clear structured verbal delivery"],
        missingConcepts=["Low-level vector math and metrics"],
        misconceptions=[],
        expressionIssues=[],
        evidence=["Polished verbal delivery"],
        isStrugglingOrDontKnow=False,
        isExpressionUnclear=False,
        recommendedNextAction=AdaptiveAction.GO_DEEPER,
        recommendedReasonCode="clear_expression_weak_knowledge"
    )

    cand_b = Candidate(candidate_id="cand_test_b", name="Taylor (Test B)", email="b@test.internal", is_synthetic_demo=True, background_summary="", target_role="AI Engineer", completed_missions=[])
    rep_b = report_generator.generate_discovery_report(state_b, cand_b, "AI Engineering Curriculum")

    print(f"Headline: '{rep_b.knowledgeVsExpressionInsight.headline}'")
    assert "communication" in rep_b.knowledgeVsExpressionInsight.headline.lower() or "clear" in rep_b.knowledgeVsExpressionInsight.headline.lower(), "Should detect clear communication with technical gap"
    print("[OK] TEST B PASSED")

    # -------------------------------------------------------------------------
    # TEST C: Misconception Report Section
    # -------------------------------------------------------------------------
    print("\n--- TEST C: Misconception Report Section ---")
    state_c, _ = interview_engine.start_interview(candidate_id="cand_test_c", curriculum_id="curr_ai_eng_v1")
    sid_c = state_c.interviewId

    ans_c1 = "RAG eliminates hallucinations completely because the vector database replaces model weights."
    interview_engine.submit_answer(sid_c, ans_c1)

    cand_c = Candidate(candidate_id="cand_test_c", name="Morgan (Test C)", email="c@test.internal", is_synthetic_demo=True, background_summary="", target_role="AI Engineer", completed_missions=[])
    rep_c = report_generator.generate_discovery_report(state_c, cand_c, "AI Engineering Curriculum")

    print(f"Misconception Insights Count: {len(rep_c.misconceptionInsights)}")
    assert len(rep_c.misconceptionInsights) > 0, "Misconception insights should be generated"
    m_insight = rep_c.misconceptionInsights[0]
    print(f"Misconception: {m_insight.misconception}")
    print(f"Mental Model: {m_insight.howToRememberIt}")
    print(f"Status: {m_insight.status}")
    assert "Mental Model" in m_insight.howToRememberIt, "Mental model should be included"
    print("[OK] TEST C PASSED")

    # -------------------------------------------------------------------------
    # TEST D: "I don't know" Handling
    # -------------------------------------------------------------------------
    print("\n--- TEST D: 'I don't know' Handling ---")
    state_d, _ = interview_engine.start_interview(candidate_id="cand_test_d", curriculum_id="curr_ai_eng_v1")
    sid_d = state_d.interviewId

    ans_d1 = "I don't know how that works."
    interview_engine.submit_answer(sid_d, ans_d1)

    cand_d = Candidate(candidate_id="cand_test_d", name="Jordan (Test D)", email="d@test.internal", is_synthetic_demo=True, background_summary="", target_role="AI Engineer", completed_missions=[])
    rep_d = report_generator.generate_discovery_report(state_d, cand_d, "AI Engineering Curriculum")

    if rep_d.coachedAnswers:
        c_ans = rep_d.coachedAnswers[0]
        print(f"What Held It Back: '{c_ans.whatHeldItBack}'")
        assert "uncertainty" in c_ans.whatHeldItBack.lower() or "knowledge" in c_ans.whatHeldItBack.lower(), "Root cause should identify uncertainty"
    print("[OK] TEST D PASSED")

    # -------------------------------------------------------------------------
    # TEST E: First-Time Candidate ("Baseline established")
    # -------------------------------------------------------------------------
    print("\n--- TEST E: First-Time Candidate ---")
    cand_e_id = f"cand_first_time_{time.time_ns()}"
    state_e, _ = interview_engine.start_interview(candidate_id=cand_e_id, curriculum_id="curr_ai_eng_v1")
    cand_e = Candidate(candidate_id=cand_e_id, name="First-Timer", email="ft@test.internal", is_synthetic_demo=True, background_summary="", target_role="AI Engineer", completed_missions=[])
    rep_e = report_generator.generate_discovery_report(state_e, cand_e, "AI Engineering Curriculum")

    print(f"Is First Time Candidate: {rep_e.isFirstTimeCandidate}")
    assert rep_e.isFirstTimeCandidate is True, "First time candidate flag should be True"
    print("[OK] TEST E PASSED")

    # -------------------------------------------------------------------------
    # TEST F: Returning Candidate with Breeth Memory
    # -------------------------------------------------------------------------
    print("\n--- TEST F: Returning Candidate with Breeth Memory ---")
    from app.memory.service import candidate_memory_service
    from app.memory.schemas import CandidateMemoryItem, MemoryType

    cand_f_id = "cand_alex_rivers_001"
    # Populate historical memory item directly
    candidate_memory_service.store_memory(
        CandidateMemoryItem(
            memory_id="mem_test_f1",
            candidate_id=cand_f_id,
            type=MemoryType.SKILL_EVIDENCE,
            topic="Spring Boot",
            skill="Dependency Injection",
            level=2,
            evidence="Demonstrated basic DI understanding",
            confidence=0.8,
            source_interview="prev_sess_100",
            status="active",
            timestamp="2026-08-01T10:00:00Z"
        )
    )

    state_f, _ = interview_engine.start_interview(candidate_id=cand_f_id, curriculum_id="curr_ai_eng_v1")
    cand_f = Candidate(candidate_id=cand_f_id, name="Alex Rivers", email="alex@test.internal", is_synthetic_demo=True, background_summary="", target_role="AI Engineer", completed_missions=[])
    rep_f = report_generator.generate_discovery_report(state_f, cand_f, "AI Engineering Curriculum")

    print(f"Is First Time Candidate: {rep_f.isFirstTimeCandidate}")
    assert rep_f.isFirstTimeCandidate is False, "Returning candidate with memory should have isFirstTimeCandidate = False"
    print("[OK] TEST F PASSED")

    # -------------------------------------------------------------------------
    # TEST G: Final API Contract POST /api/interview Preserved
    # -------------------------------------------------------------------------
    print("\n--- TEST G: Final API Contract POST /api/interview Preserved ---")
    session_id_g = f"ps2_contract_{time.time_ns()}"

    res_init = post_json(f"{BASE_URL}/api/interview", {
        "sessionId": session_id_g,
        "candidate": {"candidate_id": "cand_g", "name": "Contract Test Candidate"}
    })
    print(f"Init reply: '{res_init['reply']}', done={res_init['done']}")

    sample_answers = [
        "Cosine similarity measures the angle between normalized vector embeddings, making it scale-invariant compared to Euclidean distance.",
        "HNSW builds a multi-layer graph with logarithmic search complexity to find approximate nearest neighbors quickly.",
        "Document chunking splits large texts into smaller windows; hybrid search combines BM25 keyword matching with dense vector embeddings.",
        "Cross-encoder rerankers re-score retrieved document passages against the user query to eliminate irrelevant chunks before LLM generation.",
        "Structured outputs use JSON schema definitions and function calling protocols to guarantee deterministic parameter parsing.",
        "Let's design a high-throughput event loop for 100k concurrent connections using epoll and non-blocking sockets.",
        "CPU context switching overhead is minimized using thread pools and non-blocking I/O queues.",
        "Virtual memory uses page tables to translate virtual addresses to physical RAM frames, isolating process memory across processes."
    ]

    last_res = res_init
    idx = 0
    while not last_res.get("done") and idx < 12:
        ans_to_send = sample_answers[idx % len(sample_answers)]
        last_res = post_json(f"{BASE_URL}/api/interview", {"sessionId": session_id_g, "message": ans_to_send})
        idx += 1

    print(f"\nFinal Response Done: {last_res['done']}")
    print(f"Final Reply: '{last_res['reply']}'")
    assert last_res["done"] is True, "Interview should conclude"
    assert last_res["reply"] == "Interview completed.", "Final reply MUST be 'Interview completed.'"
    assert "feedback" in last_res, "Feedback schema MUST be present"
    assert "summary" in last_res["feedback"], "Feedback MUST contain summary"
    assert "strengths" in last_res["feedback"], "Feedback MUST contain strengths"
    assert "gaps" in last_res["feedback"], "Feedback MUST contain gaps"
    assert "next" in last_res["feedback"], "Feedback MUST contain next"
    print("[OK] TEST G PASSED — POST /api/interview API contract preserved!")

    print("\n================================================================================")
    print("ALL POST-INTERVIEW INTELLIGENCE & ANSWER COACH TESTS PASSED SUCCESSFULLY!")
    print("================================================================================")

if __name__ == "__main__":
    test_post_interview_intelligence()
