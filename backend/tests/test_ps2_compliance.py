import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

# Add backend directory to sys.path
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

def test_ps2_compliance_full_flow():
    print("================================================================================")
    print("STARTING PS2 TECHNICAL SPECIFICATION COMPLIANCE AUDIT TEST")
    print("================================================================================")
    
    session_id = f"ps2_test_session_{Path(__file__).stat().st_mtime_ns}"

    # -------------------------------------------------------------------------
    # STEP 1: First Request (Initialization with sessionId & candidate)
    # -------------------------------------------------------------------------
    init_payload = {
        "sessionId": session_id,
        "candidate": {
            "candidate_id": "cand_ps2_eval_001",
            "name": "Alex Rivers Evaluator",
            "background_summary": "5 years of Python backend engineering with pgvector and RAG experience.",
            "target_role": "Senior AI Systems Engineer",
            "completed_missions": [
                {"mission_id": "m1", "day_id": "day_1_embeddings", "score": 0.9}
            ]
        }
    }
    
    res1 = post_json(f"{BASE_URL}/api/interview", init_payload)
    print(f"\n[Turn 1 Request] Session: {session_id}")
    print(f"Reply: '{res1['reply']}'")
    print(f"Done: {res1['done']}")

    assert "reply" in res1, "Response missing 'reply' field"
    assert res1["done"] is False, "New interview should not be done on turn 1"
    assert len(res1["reply"]) > 10, "First question should be a non-empty question string"
    print("[OK] Requirement 1 & 2: POST /api/interview session creation PASSED")

    # -------------------------------------------------------------------------
    # STEP 2: Subsequent Requests (Submitting Candidate Answers on SAME sessionId)
    # -------------------------------------------------------------------------
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

    turns = [res1["reply"]]
    current_response = res1

    for idx, ans in enumerate(sample_answers):
        turn_num = idx + 2
        answer_payload = {
            "sessionId": session_id,
            "message": ans
        }
        resp = post_json(f"{BASE_URL}/api/interview", answer_payload)
        current_response = resp
        print(f"\n[Turn {turn_num} Response] Done: {resp['done']}")
        if not resp["done"]:
            print(f"Next Question: '{resp['reply']}'")
            turns.append(resp["reply"])
        else:
            print(f"Final Reply: '{resp['reply']}'")
            break

    # -------------------------------------------------------------------------
    # STEP 3: Verify Final Completion Response Format
    # -------------------------------------------------------------------------
    assert current_response["done"] is True, "Interview should auto-complete at turn 8"
    assert current_response["reply"] == "Interview completed.", "Final reply text must match 'Interview completed.'"
    assert "feedback" in current_response, "Final response missing 'feedback' object"
    
    fb = current_response["feedback"]
    assert "summary" in fb, "Feedback missing 'summary'"
    assert "strengths" in fb and isinstance(fb["strengths"], list), "Feedback missing 'strengths' list"
    assert "gaps" in fb and isinstance(fb["gaps"], list), "Feedback missing 'gaps' list"
    assert "next" in fb and isinstance(fb["next"], list), "Feedback missing 'next' list"

    print("\n--------------------------------------------------------------------------------")
    print("FINAL PS2 FEEDBACK OUTPUT:")
    print(json.dumps(fb, indent=2))
    print("--------------------------------------------------------------------------------")

    print("\n[OK] Requirement 8, 9, 10, 12: Final PS2 Completion Schema PASSED")
    print("================================================================================")
    print("ALL PS2 COMPLIANCE AUDIT TESTS PASSED SUCCESSFULLY!")
    print("================================================================================")

if __name__ == "__main__":
    test_ps2_compliance_full_flow()
