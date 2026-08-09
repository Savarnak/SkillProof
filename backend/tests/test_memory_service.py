import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.memory.schemas import (
    CandidateMemoryItem, MemoryType, GrowthEvent, PersistentGap, MemoryContext
)
from app.memory.local_fallback import LocalMemoryProvider
from app.memory.breeth import BreethMemoryProvider
from app.memory.service import candidate_memory_service
from app.interview.engine import interview_engine

def test_memory_storage_and_retrieval():
    print("Running Test 1: Memory Storage & Retrieval...")
    candidate_id = "cand_test_memory_001"
    
    # Store skill evidence
    item1 = CandidateMemoryItem(
        memory_id="mem_test_001",
        candidate_id=candidate_id,
        type=MemoryType.SKILL_EVIDENCE,
        topic="Spring Boot",
        skill="Dependency Injection",
        level=3,
        evidence="Designed dependency injection for microservices",
        confidence=0.88,
        source_interview="interview_test_101",
        status="active"
    )
    
    stored = candidate_memory_service.store_memory(item1)
    assert stored is True
    
    ctx = candidate_memory_service.get_relevant_context(candidate_id, selected_topics=["Spring Boot"])
    assert ctx.candidate_id == candidate_id
    assert len(ctx.recent_memories) >= 1
    assert ctx.recent_memories[0].topic == "Spring Boot"
    print("[OK] Memory Storage & Retrieval PASSED")

def test_fallback_provider():
    print("\nRunning Test 2: Local Fallback Memory Provider...")
    local_provider = LocalMemoryProvider()
    assert local_provider.is_available() is True
    
    # Store item in local provider
    item = CandidateMemoryItem(
        memory_id="mem_local_test_002",
        candidate_id="cand_local_001",
        type=MemoryType.KNOWLEDGE_GAP,
        topic="DBMS",
        skill="Transaction Isolation",
        evidence="Struggled with phantom reads in isolation levels",
        confidence=0.82,
        source_interview="interview_local_102",
        status="active"
    )
    assert local_provider.store_memory_item(item) is True
    
    mems = local_provider.get_candidate_memories("cand_local_001")
    assert len(mems) >= 1
    assert mems[0].topic == "DBMS"
    print("[OK] Local Fallback Provider PASSED")

def test_growth_detection():
    print("\nRunning Test 3: Growth Detection...")
    candidate_id = "cand_growth_test_001"
    
    mem1 = CandidateMemoryItem(
        memory_id="mem_g_001",
        candidate_id=candidate_id,
        type=MemoryType.SKILL_EVIDENCE,
        topic="Spring Boot",
        level=2,
        evidence="Understood baseline concept of @Autowired",
        confidence=0.80,
        source_interview="interview_session_1",
        status="active",
        timestamp="2026-08-01T10:00:00Z"
    )
    
    mem2 = CandidateMemoryItem(
        memory_id="mem_g_002",
        candidate_id=candidate_id,
        type=MemoryType.SKILL_EVIDENCE,
        topic="Spring Boot",
        level=4,
        evidence="Designed production dependency injection architecture",
        confidence=0.90,
        source_interview="interview_session_2",
        status="active",
        timestamp="2026-08-05T10:00:00Z"
    )
    
    candidate_memory_service.store_memory(mem1)
    candidate_memory_service.store_memory(mem2)
    
    memories = candidate_memory_service.local_provider.get_candidate_memories(candidate_id)
    growth_events = candidate_memory_service.detect_growth(candidate_id, memories)
    
    assert len(growth_events) >= 1
    assert growth_events[0].topic == "Spring Boot"
    assert growth_events[0].previous_level == 2
    assert growth_events[0].current_level == 4
    assert growth_events[0].growth == 2
    print("[OK] Growth Detection PASSED")

def test_persistent_gap_detection():
    print("\nRunning Test 4: Persistent Gap Detection...")
    candidate_id = "cand_gap_test_001"
    
    mem1 = CandidateMemoryItem(
        memory_id="mem_p_001",
        candidate_id=candidate_id,
        type=MemoryType.KNOWLEDGE_GAP,
        topic="DBMS",
        skill="Transaction Isolation",
        evidence="Struggled with isolation levels in session 1",
        confidence=0.82,
        source_interview="interview_sess_1",
        status="active"
    )
    
    mem2 = CandidateMemoryItem(
        memory_id="mem_p_002",
        candidate_id=candidate_id,
        type=MemoryType.KNOWLEDGE_GAP,
        topic="DBMS",
        skill="Transaction Isolation",
        evidence="Struggled with isolation levels in session 2",
        confidence=0.85,
        source_interview="interview_sess_2",
        status="active"
    )
    
    candidate_memory_service.store_memory(mem1)
    candidate_memory_service.store_memory(mem2)
    
    memories = candidate_memory_service.local_provider.get_candidate_memories(candidate_id)
    persistent_gaps = candidate_memory_service.detect_persistent_gaps(candidate_id, memories)
    
    assert len(persistent_gaps) >= 1
    assert persistent_gaps[0].topic == "DBMS"
    assert persistent_gaps[0].occurrences_count >= 2
    print("[OK] Persistent Gap Detection PASSED")

def test_delete_candidate_memories():
    print("\nRunning Test 5: Data Minimization & Deletion...")
    candidate_id = "cand_del_test_001"
    
    item = CandidateMemoryItem(
        memory_id="mem_d_001",
        candidate_id=candidate_id,
        type=MemoryType.SKILL_EVIDENCE,
        topic="Git",
        evidence="Explained rebase vs merge",
        confidence=0.85,
        source_interview="interview_d_1",
        status="active"
    )
    candidate_memory_service.store_memory(item)
    
    assert len(candidate_memory_service.local_provider.get_candidate_memories(candidate_id)) >= 1
    
    deleted = candidate_memory_service.delete_candidate_memories(candidate_id)
    assert deleted is True
    assert len(candidate_memory_service.local_provider.get_candidate_memories(candidate_id)) == 0
    print("[OK] Data Minimization & Deletion PASSED")

if __name__ == "__main__":
    print("Running SkillProof Breeth Memory Unit Test Suite...\n")
    test_memory_storage_and_retrieval()
    test_fallback_provider()
    test_growth_detection()
    test_persistent_gap_detection()
    test_delete_candidate_memories()
    print("\n[OK] ALL BREETH MEMORY UNIT TESTS PASSED SUCCESSFULLY!")
