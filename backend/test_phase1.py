"""
SkillProof Phase 1 Verification Script
Validates Pydantic schema deserialization against sample JSON data.
"""
import json
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from app.schemas.curriculum import Curriculum
from app.schemas.candidate import Candidate
from app.schemas.interview_state import InterviewSession, DeterministicState

def test_phase1_schemas():
    project_root = Path(__file__).parent.parent
    
    # 1. Test Curriculum Schema
    curriculum_path = project_root / "data" / "sample_curriculum.json"
    assert curriculum_path.exists(), f"Missing file: {curriculum_path}"
    with open(curriculum_path, "r", encoding="utf-8") as f:
        curr_data = json.load(f)
    curriculum = Curriculum(**curr_data)
    print(f"✓ Curriculum schema verified: {curriculum.title} ({len(curriculum.modules)} modules)")

    # 2. Test Candidate Schema
    candidates_path = project_root / "data" / "sample_candidates.json"
    assert candidates_path.exists(), f"Missing file: {candidates_path}"
    with open(candidates_path, "r", encoding="utf-8") as f:
        cand_data = json.load(f)
    candidates = [Candidate(**c) for c in cand_data]
    print(f"✓ Candidate schema verified: {len(candidates)} synthetic candidates loaded")

    # 3. Test Interview State Schema & Deterministic Rules
    dstate = DeterministicState(min_questions=8, min_curriculum_days=4)
    print(f"✓ Deterministic constraints initialized: min_questions={dstate.min_questions}, min_days={dstate.min_curriculum_days}")

if __name__ == "__main__":
    test_phase1_schemas()
