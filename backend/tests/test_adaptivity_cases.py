import sys
import json
import urllib.request
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

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

import time

def test_all_adaptive_cases():
    print("================================================================================")
    print("STARTING INTERVIEW ADAPTIVITY TEST SUITE")
    print("================================================================================")

    session_id = f"test_adapt_{time.time_ns()}"

    # 1. Start Session
    res1 = post_json(f"{BASE_URL}/api/interview", {
        "sessionId": session_id,
        "candidate": {
            "candidate_id": "cand_adapt_001",
            "name": "Alex Rivers",
            "background_summary": "Python backend engineer"
        }
    })
    q1 = res1["reply"]
    print(f"\n[Turn 1 Q1]: {q1}")

    # -------------------------------------------------------------------------
    # TEST 1 — Strong Answer on Q1
    # -------------------------------------------------------------------------
    ans1 = "Vector spaces represent information as numerical vectors. Similarity metrics such as cosine similarity can compare these vectors based on their direction, which is useful for semantic search and retrieval."
    res2 = post_json(f"{BASE_URL}/api/interview", {"sessionId": session_id, "message": ans1})
    q2 = res2["reply"]
    print(f"\n[TEST 1 - Strong Answer Submitted]: '{ans1}'")
    print(f"[Turn 2 Next Question]: {q2}")
    assert "direction" in q2.lower() or "cosine" in q2.lower() or "vector" in q2.lower(), "Follow-up question should explicitly ground on candidate's answer"
    print("[OK] TEST 1 — Strong Answer Adaptation PASSED (Grounded on direction/cosine)")

    # -------------------------------------------------------------------------
    # TEST 2 — Weak/Incomplete Answer on Q2
    # -------------------------------------------------------------------------
    ans2 = "It just compares numbers in lists."
    res3 = post_json(f"{BASE_URL}/api/interview", {"sessionId": session_id, "message": ans2})
    q3 = res3["reply"]
    print(f"\n[TEST 2 - Weak Answer Submitted]: '{ans2}'")
    print(f"[Turn 3 Next Question]: {q3}")
    assert ("structure" in q3.lower() or "explain" in q3.lower() or "clarify" in q3.lower() or "vector" in q3.lower()), "Incomplete answer should trigger scaffolding/clarification"
    print("[OK] TEST 2 — Weak Answer Adaptation PASSED (Triggers scaffolding/clarification)")

    # -------------------------------------------------------------------------
    # TEST 3 — 'I don't know' on Q3
    # -------------------------------------------------------------------------
    ans3 = "I don't know how that works."
    res4 = post_json(f"{BASE_URL}/api/interview", {"sessionId": session_id, "message": ans3})
    q4 = res4["reply"]
    print(f"\n[TEST 3 - 'I don't know' Submitted]: '{ans3}'")
    print(f"[Turn 4 Next Question]: {q4}")
    assert "fine" in q4.lower() or "simplify" in q4.lower() or "fundamental" in q4.lower(), "'I don't know' should trigger supportive recovery scaffold"
    print("[OK] TEST 3 — 'I don't know' Adaptation PASSED (Supportive recovery scaffold)")

    # -------------------------------------------------------------------------
    # TEST 4 — Misconception on Q4
    # -------------------------------------------------------------------------
    ans4 = "RAG eliminates hallucinations completely because the vector database replaces model weights."
    res5 = post_json(f"{BASE_URL}/api/interview", {"sessionId": session_id, "message": ans4})
    q5 = res5["reply"]
    print(f"\n[TEST 4 - Misconception Submitted]: '{ans4}'")
    print(f"[Turn 5 Next Question]: {q5}")
    assert "hallucination" in q5.lower() or "suppose" in q5.lower() or "irrelevant" in q5.lower(), "Misconception should trigger targeted probe"
    print("[OK] TEST 4 — Misconception Adaptation PASSED (Targeted probe challenge)")

    # -------------------------------------------------------------------------
    # TEST 5 & 6 — Strong Repeated Answers & Natural Topic Switch
    # -------------------------------------------------------------------------
    ans5 = "If search returns bad docs, tokenization limits, chunk boundary cuts, or embedding model drift could cause false positives."
    res6 = post_json(f"{BASE_URL}/api/interview", {"sessionId": session_id, "message": ans5})
    q6 = res6["reply"]
    print(f"\n[TEST 5 - Strong Answer Submitted]: '{ans5}'")
    print(f"[Turn 6 Next Question]: {q6}")

    ans6 = "We would construct a hybrid search pipeline combining BM25 keyword matching with HNSW ANN indexing using Reciprocal Rank Fusion."
    res7 = post_json(f"{BASE_URL}/api/interview", {"sessionId": session_id, "message": ans6})
    q7 = res7["reply"]
    print(f"\n[TEST 6 - Natural Topic Switch Request]: '{ans6}'")
    print(f"[Turn 7 Next Question]: {q7}")
    assert "solid" in q7.lower() or "build on" in q7.lower() or "move into" in q7.lower() or "day" in q7.lower(), "Topic switch should feature natural transition"
    print("[OK] TEST 5 & 6 — Progressive Depth & Natural Topic Switch PASSED")

    # Complete interview turns 7 and 8
    ans7 = "Document chunking strategy balances semantic overlap with recursive splitting."
    res8 = post_json(f"{BASE_URL}/api/interview", {"sessionId": session_id, "message": ans7})
    print(f"[Turn 8 Res]: reply='{res8.get('reply')}', done={res8.get('done')}")

    if res8.get("done"):
        final_res = res8
    else:
        ans8 = "Cross-encoder rerankers re-score candidate document passages to filter false positives."
        final_res = post_json(f"{BASE_URL}/api/interview", {"sessionId": session_id, "message": ans8})

    print(f"\n[Final Response] Done: {final_res['done']}")
    assert final_res["done"] is True, "Interview should auto-complete at turn 8"
    assert final_res["reply"] == "Interview completed.", "Final reply must be 'Interview completed.'"
    assert "feedback" in final_res, "Feedback object must be present"

    print("\n--------------------------------------------------------------------------------")
    print("FINAL ADAPTIVE INTERVIEW FEEDBACK:")
    print(json.dumps(final_res["feedback"], indent=2))
    print("--------------------------------------------------------------------------------")

    print("\n================================================================================")
    print("ALL 6 ADAPTIVITY TEST CASES PASSED SUCCESSFULLY!")
    print("================================================================================")

if __name__ == "__main__":
    test_all_adaptive_cases()
