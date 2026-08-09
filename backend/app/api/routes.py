from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.interview.engine import interview_engine
from app.interview.schemas import InterviewState, InterviewReport

router = APIRouter(prefix="/api/interview", tags=["interview"])

from app.schemas.candidate import Candidate

class StartInterviewRequest(BaseModel):
    candidate_id: str = "cand_alex_rivers_001"
    curriculum_id: str = "curr_ai_eng_v1"
    selected_topics: List[str] = Field(default_factory=list)
    selected_categories: List[str] = Field(default_factory=list)
    target_role: Optional[str] = None
    job_description: Optional[str] = None
    mode: str = "learning_journey"  # learning_journey or job_description

class AnswerRequest(BaseModel):
    answer_text: str = Field(..., min_length=1)

class StartInterviewResponse(BaseModel):
    state: InterviewState
    current_question: str

class AnswerResponse(BaseModel):
    state: InterviewState
    next_question: Optional[str] = None
    is_completed: bool = False

# -----------------------------------------------------------------------------
# OFFICIAL PS2 EVALUATOR ADAPTER (POST /api/interview)
# -----------------------------------------------------------------------------
class PS2Feedback(BaseModel):
    summary: str
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    next: List[str] = Field(default_factory=list)

class PS2InterviewRequest(BaseModel):
    sessionId: str = Field(..., description="Unique interview session identifier")
    candidate: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class PS2InterviewResponse(BaseModel):
    reply: str
    done: bool = False
    feedback: Optional[PS2Feedback] = None

import datetime

@router.post("", response_model=PS2InterviewResponse)
@router.post("/", response_model=PS2InterviewResponse)
def ps2_interview_adapter(req: PS2InterviewRequest):
    session_id = req.sessionId.strip()
    existing_state = interview_engine.session_store.get_session(session_id)

    if not existing_state:
        # Case 1: Initialize New Session
        cand_dict = req.candidate or {}
        cand_id = cand_dict.get("candidate_id") or cand_dict.get("id") or f"cand_{session_id}"
        cand_name = cand_dict.get("name") or "Alex Rivers"

        if cand_dict:
            try:
                raw_missions = cand_dict.get("completed_missions", [])
                formatted_missions = []
                for m in raw_missions:
                    if isinstance(m, dict):
                        m_copy = m.copy()
                        if "completed_at" not in m_copy:
                            m_copy["completed_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                        formatted_missions.append(m_copy)

                cand_obj = Candidate(
                    candidate_id=cand_id,
                    name=cand_name,
                    email=cand_dict.get("email", f"{cand_id}@demo.skillproof.internal"),
                    is_synthetic_demo=False,
                    background_summary=cand_dict.get("background_summary", ""),
                    target_role=cand_dict.get("target_role", "Senior AI Systems Engineer"),
                    completed_missions=formatted_missions
                )
                interview_engine._candidates_cache[cand_id] = cand_obj
            except Exception:
                pass

        state, first_question = interview_engine.start_interview(
            candidate_id=cand_id,
            curriculum_id="curr_ai_eng_v1"
        )

        if state.interviewId != session_id:
            old_id = state.interviewId
            state.interviewId = session_id
            interview_engine.session_store._sessions.pop(old_id, None)
            interview_engine.session_store._sessions[session_id] = state

        return PS2InterviewResponse(
            reply=first_question,
            done=False
        )

    # Case 2: Submit Candidate Answer message to existing session
    if req.message:
        state, next_question = interview_engine.submit_answer(
            session_id=session_id,
            candidate_answer=req.message
        )
    else:
        state = existing_state
        next_question = state.conversationHistory[-1].question_text if state.conversationHistory else None

    # Check if interview complete
    if state.interviewStatus == "completed" or next_question is None:
        summary_txt = f"Completed adaptive technical evaluation across {state.questionCount} questions covering {len(state.curriculumDaysCovered)} curriculum days."
        strengths_lst = state.strengths[:5] or ["Demonstrated solid core technical understanding"]
        gaps_lst = state.knowledgeGaps[:5] or state.expressionGaps[:5] or ["Practice system design trade-offs"]
        next_lst = [
            "Review B+ Tree indexing & transaction isolation",
            "Practice virtual memory page fault resolution",
            "Explore production system design scenarios"
        ]

        return PS2InterviewResponse(
            reply="Interview completed.",
            done=True,
            feedback=PS2Feedback(
                summary=summary_txt,
                strengths=strengths_lst,
                gaps=gaps_lst,
                next=next_lst
            )
        )

    return PS2InterviewResponse(
        reply=next_question,
        done=False
    )

@router.post("/start", response_model=StartInterviewResponse)
def start_interview(req: StartInterviewRequest):
    try:
        state, first_question = interview_engine.start_interview(
            candidate_id=req.candidate_id,
            curriculum_id=req.curriculum_id,
            selected_topics=req.selected_topics,
            selected_categories=req.selected_categories,
            target_role=req.target_role,
            job_description=req.job_description,
            mode=req.mode
        )
        return StartInterviewResponse(state=state, current_question=first_question)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{interview_id}/answer", response_model=AnswerResponse)
def submit_answer(interview_id: str, req: AnswerRequest):
    try:
        state, next_q = interview_engine.submit_answer(
            session_id=interview_id,
            candidate_answer=req.answer_text
        )
        return AnswerResponse(
            state=state,
            next_question=next_q,
            is_completed=(state.interviewStatus == "completed")
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{interview_id}/state", response_model=InterviewState)
def get_interview_state(interview_id: str):
    state = interview_engine.session_store.get_session(interview_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Interview '{interview_id}' not found")
    return state

@router.post("/{interview_id}/finish", response_model=InterviewState)
def finish_interview(interview_id: str):
    try:
        state = interview_engine.finish_interview(interview_id)
        return state
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from app.report.generator import report_generator

@router.get("/{interview_id}/report")
def get_interview_report(interview_id: str):
    try:
        state = interview_engine.session_store.get_session(interview_id)
        if not state:
            raise HTTPException(status_code=404, detail=f"Session '{interview_id}' not found")
        
        candidate = interview_engine._candidates_cache.get(
            state.candidateId,
            interview_engine._candidates_cache.get("cand_alex_rivers_001")
        )
        curr_title = interview_engine._curriculum_cache.title if interview_engine._curriculum_cache else "AI Systems"
        
        report_data = report_generator.generate_discovery_report(
            state=state,
            candidate=candidate,
            curriculum_title=curr_title
        )
        return report_data
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from app.memory.service import candidate_memory_service

@router.delete("/candidate/{candidate_id}/memory")
def delete_candidate_memory(candidate_id: str):
    try:
        success = candidate_memory_service.delete_candidate_memories(candidate_id)
        return {"status": "deleted", "candidate_id": candidate_id, "success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
