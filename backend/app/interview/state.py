from typing import Dict, Optional
import datetime
from app.interview.schemas import InterviewState, SessionStatus

class SessionStoreManager:
    """Thread-safe in-memory session manager for interview sessions."""
    def __init__(self):
        self._sessions: Dict[str, InterviewState] = {}

    def create_session(
        self,
        session_id: str,
        candidate_id: str,
        curriculum_id: str,
        min_questions: int = 8,
        min_curriculum_days: int = 4
    ) -> InterviewState:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        state = InterviewState(
            interviewId=session_id,
            candidateId=candidate_id,
            curriculumId=curriculum_id,
            minQuestions=min_questions,
            minCurriculumDays=min_curriculum_days,
            created_at=now,
            updated_at=now,
        )
        self._sessions[session_id] = state
        return state

    def get_session(self, session_id: str) -> Optional[InterviewState]:
        return self._sessions.get(session_id)

    def update_session(self, state: InterviewState) -> InterviewState:
        state.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._sessions[state.interviewId] = state
        return state

    def clear(self):
        self._sessions.clear()

session_store = SessionStoreManager()
