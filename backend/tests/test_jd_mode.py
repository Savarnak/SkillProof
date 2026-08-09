import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.interview.jd_analyzer import jd_analyzer
from app.interview.engine import interview_engine
from app.report.generator import report_generator

def test_jd_analyzer_extraction():
    """Verify JD Analyzer extracts key languages, frameworks, cloud tools, databases, and roles."""
    sample_jd = """
    We are looking for a Senior Java Developer with strong expertise in Spring Boot, REST Microservices, PostgreSQL, SQL, Docker, AWS, and Git.
    Responsibilities include designing backend systems and optimizing database performance.
    """
    res = jd_analyzer.analyze_jd(sample_jd)
    
    assert "Java" in res.programming_languages
    assert "Spring Boot" in res.frameworks
    assert "Postgresql" in res.databases or "Sql" in res.databases
    assert "Docker" in res.cloud_tools or "Aws" in res.cloud_tools
    assert len(res.requirements_map) >= 4

def test_start_interview_with_jd_mode():
    """Verify start_interview initializes session in JD mode with JD requirement coverage items."""
    sample_jd = "Looking for a Python Developer with Django, PostgreSQL, Docker, and AWS."
    state, first_q = interview_engine.start_interview(
        candidate_id="cand_alex_rivers_001",
        job_description=sample_jd,
        mode="job_description"
    )

    assert state.interviewMode == "job_description"
    assert len(state.jdRequirementCoverage) >= 4
    assert state.targetRole is not None

    cand = interview_engine._candidates_cache.get("cand_alex_rivers_001")
    report = report_generator.generate_discovery_report(
        state=state,
        candidate=cand,
        curriculum_title="AI Systems"
    )

    assert report.interviewMode == "job_description"
    assert len(report.jdRequirementCoverage) >= 4

def test_start_interview_with_custom_topics_and_role():
    """Verify start_interview stores selected custom topics and target role."""
    state, first_q = interview_engine.start_interview(
        candidate_id="cand_alex_rivers_001",
        selected_topics=["Operating Systems", "DBMS", "Spring Boot"],
        selected_categories=["core_cs", "frameworks"],
        target_role="Backend Developer"
    )

    assert state.targetRole == "Backend Developer"
    assert "Operating Systems" in state.selectedTopics
    assert "core_cs" in state.selectedCategories

if __name__ == "__main__":
    print("Running SkillProof Refinement Test Suite (JD Mode & Setup)...")
    test_jd_analyzer_extraction()
    print("[OK] test_jd_analyzer_extraction PASSED")

    test_start_interview_with_jd_mode()
    print("[OK] test_start_interview_with_jd_mode PASSED")

    test_start_interview_with_custom_topics_and_role()
    print("[OK] test_start_interview_with_custom_topics_and_role PASSED")

    print("[OK] ALL REFINEMENT TESTS PASSED SUCCESSFULLY!")
