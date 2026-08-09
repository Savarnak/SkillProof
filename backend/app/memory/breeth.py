import logging
import json
import urllib.request
import urllib.error
from typing import List, Optional, Dict, Any
from app.config import settings
from app.memory.base import BaseMemoryProvider
from app.memory.schemas import CandidateMemoryItem, MemoryType

logger = logging.getLogger("SkillProof.BreethMemory")

class BreethMemoryProvider(BaseMemoryProvider):
    """
    Breeth AI Memory Provider connecting to https://api.thebreeth.com/v1.
    Performs memory ingestion (POST /v1/episodes) and hybrid search (POST /v1/search)
    isolated by candidate_id (group_id).
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.BREETH_API_KEY
        self.base_url = (base_url or settings.BREETH_BASE_URL).rstrip("/")
        self.enabled = settings.BREETH_ENABLED and bool(self.api_key)

    def is_available(self) -> bool:
        return self.enabled and bool(self.api_key)

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def store_memory_item(self, item: CandidateMemoryItem) -> bool:
        if not self.is_available():
            logger.warning("[MEMORY_UNAVAILABLE] Breeth API disabled or API key missing.")
            return False

        url = f"{self.base_url}/episodes"
        payload = {
            "content": f"[{item.type.value.upper()}] Topic: {item.topic} | Skill: {item.skill or 'General'} | Evidence: {item.evidence}",
            "group_id": item.candidate_id,
            "extract_intent": True,
            "metadata": {
                "memory_id": item.memory_id,
                "candidate_id": item.candidate_id,
                "type": item.type.value,
                "topic": item.topic,
                "skill": item.skill,
                "level": item.level,
                "confidence": item.confidence,
                "source_interview": item.source_interview,
                "status": item.status,
                "timestamp": item.timestamp
            }
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=self._headers(), method="POST")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status in (200, 201):
                    logger.info(f"[MEMORY_WRITTEN] Breeth memory stored: {item.memory_id} (Candidate: {item.candidate_id})")
                    return True
        except Exception as e:
            logger.error(f"[MEMORY_WRITTEN_FAILED] Breeth API error storing item {item.memory_id}: {str(e)}")
            return False

        return False

    def store_memory_batch(self, items: List[CandidateMemoryItem]) -> int:
        count = 0
        for item in items:
            if self.store_memory_item(item):
                count += 1
        return count

    def search_memories(
        self,
        candidate_id: str,
        query: Optional[str] = None,
        topics: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[CandidateMemoryItem]:
        if not self.is_available():
            logger.warning("[MEMORY_UNAVAILABLE] Breeth API not available for search.")
            return []

        url = f"{self.base_url}/search"
        search_query = query or (f"Technical evidence for {', '.join(topics)}" if topics else "Candidate technical evidence and gaps")
        payload = {
            "query": search_query,
            "group_id": candidate_id,
            "limit": limit
        }

        results: List[CandidateMemoryItem] = []
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=self._headers(), method="POST")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    episodes = data.get("episodes", data.get("results", []))
                    for ep in episodes:
                        meta = ep.get("metadata", {})
                        if meta.get("candidate_id") == candidate_id:
                            try:
                                results.append(CandidateMemoryItem(
                                    memory_id=meta.get("memory_id", "mem_breeth_auto"),
                                    candidate_id=candidate_id,
                                    type=MemoryType(meta.get("type", "skill_evidence")),
                                    topic=meta.get("topic", "General"),
                                    skill=meta.get("skill"),
                                    level=meta.get("level"),
                                    evidence=meta.get("evidence", ep.get("content", "")),
                                    confidence=meta.get("confidence", 0.85),
                                    source_interview=meta.get("source_interview", "interview_previous"),
                                    status=meta.get("status", "active"),
                                    timestamp=meta.get("timestamp", "")
                                ))
                            except Exception:
                                pass
                    logger.info(f"[MEMORY_RETRIEVAL_COMPLETED] Breeth returned {len(results)} memories for {candidate_id}")
                    return results
        except Exception as e:
            logger.error(f"[MEMORY_RETRIEVAL_FAILED] Breeth API search error for candidate {candidate_id}: {str(e)}")

        return []

    def get_candidate_memories(self, candidate_id: str) -> List[CandidateMemoryItem]:
        return self.search_memories(candidate_id=candidate_id, limit=50)

    def delete_candidate_memories(self, candidate_id: str) -> bool:
        if not self.is_available():
            return False

        url = f"{self.base_url}/group/{candidate_id}"
        try:
            req = urllib.request.Request(url, headers=self._headers(), method="DELETE")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status in (200, 204):
                    logger.info(f"[MEMORY_DELETED] Deleted candidate memories for {candidate_id} from Breeth")
                    return True
        except Exception as e:
            logger.error(f"[MEMORY_DELETED_FAILED] Failed to delete candidate memories for {candidate_id}: {str(e)}")

        return False
