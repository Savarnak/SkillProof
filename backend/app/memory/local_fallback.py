import os
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from app.memory.base import BaseMemoryProvider
from app.memory.schemas import CandidateMemoryItem, MemoryType

logger = logging.getLogger("SkillProof.LocalMemory")

class LocalMemoryProvider(BaseMemoryProvider):
    """
    Local JSON Memory Provider for offline & fallback mode.
    Persists structured candidate memories to backend/app/data/memory_db.json.
    """

    def __init__(self, db_path: Optional[str] = None):
        if not db_path:
            base_dir = Path(__file__).resolve().parent.parent
            db_path = str(base_dir / "data" / "memory_db.json")
        self.db_path = Path(db_path)
        self._ensure_storage()

    def _ensure_storage(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump({"memories": []}, f, indent=2)

    def _read_data(self) -> List[Dict[str, Any]]:
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("memories", [])
        except Exception as e:
            logger.error(f"Failed to read memory_db.json: {e}")
            return []

    def _write_data(self, memories: List[Dict[str, Any]]) -> bool:
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump({"memories": memories}, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to write memory_db.json: {e}")
            return False

    def is_available(self) -> bool:
        return True

    def store_memory_item(self, item: CandidateMemoryItem) -> bool:
        memories = self._read_data()
        item_dict = item.model_dump()
        
        # Check if item already exists by memory_id
        updated = False
        for idx, m in enumerate(memories):
            if m.get("memory_id") == item.memory_id:
                memories[idx] = item_dict
                updated = True
                break

        if not updated:
            memories.append(item_dict)

        success = self._write_data(memories)
        if success:
            logger.info(f"[MEMORY_WRITTEN_LOCAL] Local memory stored: {item.memory_id} (Candidate: {item.candidate_id})")
        return success

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
        memories = self._read_data()
        results: List[CandidateMemoryItem] = []

        q_lower = query.lower() if query else ""
        topic_lowers = [t.lower() for t in topics] if topics else []

        for m in memories:
            if m.get("candidate_id") != candidate_id:
                continue

            item_topic = str(m.get("topic", "")).lower()
            item_skill = str(m.get("skill", "")).lower()
            item_ev = str(m.get("evidence", "")).lower()

            match_topic = not topic_lowers or any(t in item_topic or t in item_skill for t in topic_lowers)
            match_query = not q_lower or (q_lower in item_topic or q_lower in item_skill or q_lower in item_ev)

            if match_topic and match_query:
                try:
                    results.append(CandidateMemoryItem(**m))
                except Exception as e:
                    logger.error(f"Error parsing memory item: {e}")

            if len(results) >= limit:
                break

        logger.info(f"[MEMORY_RETRIEVAL_LOCAL] Found {len(results)} local memories for candidate {candidate_id}")
        return results

    def get_candidate_memories(self, candidate_id: str) -> List[CandidateMemoryItem]:
        return self.search_memories(candidate_id=candidate_id, limit=100)

    def delete_candidate_memories(self, candidate_id: str) -> bool:
        memories = self._read_data()
        filtered = [m for m in memories if m.get("candidate_id") != candidate_id]
        success = self._write_data(filtered)
        if success:
            logger.info(f"[MEMORY_DELETED_LOCAL] Deleted all local memories for candidate {candidate_id}")
        return success
