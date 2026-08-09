import logging
import json
import datetime
from typing import Dict, Any

logger = logging.getLogger("skillproof.engine")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class InterviewLogger:
    """Structured Event Logger for SkillProof Observability."""

    @staticmethod
    def log_event(event_type: str, session_id: str, payload: Dict[str, Any]):
        event = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "event_type": event_type,
            "session_id": session_id,
            "data": payload
        }
        logger.info(f"[{event_type}] Session: {session_id} | Data: {json.dumps(payload)}")
        return event

interview_logger = InterviewLogger()
