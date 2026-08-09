from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.memory.schemas import CandidateMemoryItem, MemoryContext, GrowthEvent, PersistentGap

class BaseMemoryProvider(ABC):
    """Abstract Base Class for Candidate Memory Providers."""

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if provider is configured and reachable."""
        pass

    @abstractmethod
    def store_memory_item(self, item: CandidateMemoryItem) -> bool:
        """Stores a single structured candidate memory item."""
        pass

    @abstractmethod
    def store_memory_batch(self, items: List[CandidateMemoryItem]) -> int:
        """Stores a batch of candidate memory items. Returns number stored."""
        pass

    @abstractmethod
    def search_memories(
        self,
        candidate_id: str,
        query: Optional[str] = None,
        topics: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[CandidateMemoryItem]:
        """Searches candidate memories by candidate_id, query string, or topics filter."""
        pass

    @abstractmethod
    def get_candidate_memories(self, candidate_id: str) -> List[CandidateMemoryItem]:
        """Retrieves all memory items for a specific candidate."""
        pass

    @abstractmethod
    def delete_candidate_memories(self, candidate_id: str) -> bool:
        """Deletes all memory items for a candidate (Privacy / Data Minimization)."""
        pass
