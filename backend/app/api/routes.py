from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional

from app.interview.engine import interview_engine
from app.interview.schemas import InterviewState, InterviewReport

router = APIRouter(prefix="/api/interview", tags=["interview"])

class StartInterviewRequest(BaseModel):
    candidate_id: str = "cand_alex_rivers_001"
    curriculum_id: str = "curr_ai_eng_v1"

class AnswerRequest(BaseModel):
    answer_text: str = Field(..., min_length=1)

class StartInterviewResponse(BaseModel):
    state: InterviewState
    current_question: str

class AnswerResponse(BaseModel):
    state: InterviewState
    next_question: Optional[str] = None
    is_completed: bool = False

@router.post("/start", response_model=StartInterviewResponse)
def start_interview(req: StartInterviewRequest):
    try:
        state, first_question = interview_engine.start_interview(
            candidate_id=req.candidate_id,
            curriculum_id=req.curriculum_id
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

@router.get("/{interview_id}/report", response_model=InterviewReport)
def get_interview_report(interview_id: str):
    try:
        report = interview_engine.generate_report(interview_id)
        return report
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
