"""
SkillProof Modular Prompt Architecture
Defines clean, isolated prompt templates for LLM evaluation, adaptive question generation,
misconception probing, expression scaffolding, and cross-domain transfer.
"""
from typing import Dict, Any, List, Optional

def build_candidate_context_prompt(
    candidate_name: str,
    target_role: str,
    background_summary: str,
    profile_strengths: List[str],
    profile_gaps: List[str]
) -> str:
    return f"""
CANDIDATE CONTEXT:
- Name: {candidate_name}
- Target Role: {target_role}
- Background: {background_summary}
- Profile Signals (Hypotheses):
  * Strengths: {', '.join(profile_strengths) if profile_strengths else 'None recorded'}
  * Known Gaps: {', '.join(profile_gaps) if profile_gaps else 'None recorded'}
    """.strip()

def build_answer_evaluation_prompt(
    question_text: str,
    answer_text: str,
    topic_name: str,
    target_depth: int
) -> str:
    return f"""
EVALUATE CANDIDATE ANSWER:
Topic: {topic_name} (Target Depth Level: {target_depth})
Question: "{question_text}"
Candidate Response: "{answer_text}"

Evaluate separately:
1. Technical Correctness (0.0 to 1.0)
2. Conceptual Depth (0.0 to 1.0)
3. Application Ability (0.0 to 1.0)
4. Expression Clarity & Structure (0.0 to 1.0)
5. Identify any technical misconceptions or struggles ("I don't know").
    """.strip()

def build_question_generation_prompt(
    topic_name: str,
    day_number: int,
    action: str,
    target_depth: int,
    pending_evidence_item: Optional[str] = None,
    previous_answer: Optional[str] = None
) -> str:
    pending_clause = f"Target missing evidence: {pending_evidence_item}" if pending_evidence_item else ""
    prev_clause = f"Candidate's previous response: '{previous_answer}'" if previous_answer else ""
    
    return f"""
GENERATE ADAPTIVE INTERVIEW QUESTION:
- Topic: {topic_name} (Curriculum Day {day_number})
- Target Depth Level: {target_depth} (Action: {action})
- {pending_clause}
- {prev_clause}

Formulate a natural, professional technical question encouraging the candidate to demonstrate understanding.
    """.strip()

def build_misconception_challenge_prompt(
    topic_name: str,
    misconception_text: str
) -> str:
    return f"""
MISCONCEPTION CHALLENGE PROBE:
Topic: {topic_name}
Detected Misconception: "{misconception_text}"

Formulate a gentle, probing challenge question that tests whether the candidate can reason through this edge case without revealing the correct answer.
    """.strip()

def build_expression_recovery_prompt(
    topic_name: str,
    raw_answer: str
) -> str:
    return f"""
EXPRESSION SCAFFOLDING PROMPT:
Topic: {topic_name}
Candidate Response: "{raw_answer}"

The candidate appears to understand the core concept but gave an unstructured response.
Provide an encouraging scaffolding prompt inviting them to explain the concept in a 3-part structured format.
    """.strip()

def build_transfer_prompt(
    topic_name: str,
    domain_name: str,
    candidate_role: str
) -> str:
    return f"""
CROSS-DOMAIN CONCEPT TRANSFER CHALLENGE:
Technical Topic: {topic_name}
New Domain Scenario: {domain_name} (Target Role: {candidate_role})

Formulate a real-world architectural scenario asking the candidate to transfer their knowledge of {topic_name} into {domain_name}.
    """.strip()

def build_final_feedback_prompt(
    candidate_name: str,
    knowledge_score: float,
    expression_score: float,
    strengths: List[str],
    gaps: List[str],
    misconceptions: List[str]
) -> str:
    return f"""
GENERATE POST-INTERVIEW FEEDBACK:
Candidate: {candidate_name}
Overall Knowledge Score: {knowledge_score}
Overall Expression Score: {expression_score}
Demonstrated Strengths: {', '.join(strengths)}
Identified Gaps: {', '.join(gaps)}
Misconceptions: {', '.join(misconceptions)}
    """.strip()
