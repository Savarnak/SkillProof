import logging
import uuid
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from app.memory.schemas import (
    CandidateMemoryItem, MemoryType, GrowthEvent, PersistentGap, MemoryContext
)
from app.memory.breeth import BreethMemoryProvider
from app.memory.local_fallback import LocalMemoryProvider
from app.schemas.candidate import Candidate
from app.interview.schemas import InterviewState, SessionStatus

logger = logging.getLogger("SkillProof.MemoryService")

class CandidateMemoryService:
    """
    Unified Longitudinal Candidate Memory Service for SkillProof.
    Orchestrates Breeth AI memory layer with automatic local fallback.
    """

    def __init__(self):
        self.breeth_provider = BreethMemoryProvider()
        self.local_provider = LocalMemoryProvider()

    def get_provider(self):
        if self.breeth_provider.is_available():
            return self.breeth_provider
        logger.info("[MEMORY_FALLBACK_USED] Breeth API disabled or unavailable. Operating in Local Memory Fallback Mode.")
        return self.local_provider

    def store_memory(self, item: CandidateMemoryItem) -> bool:
        """Stores candidate memory with Breeth primary and Local fallback."""
        success = False
        if self.breeth_provider.is_available():
            try:
                success = self.breeth_provider.store_memory_item(item)
            except Exception as e:
                logger.error(f"[MEMORY_UNAVAILABLE] Breeth API call failed: {str(e)}")
                success = False

        # Always persist locally for offline resilience
        self.local_provider.store_memory_item(item)
        return True

    def store_interview_memories(
        self,
        state: InterviewState,
        candidate: Candidate
    ) -> List[CandidateMemoryItem]:
        """
        Extracts meaningful candidate-level insights from a completed interview turn history
        and persists them into longitudinal memory.
        """
        stored_items: List[CandidateMemoryItem] = []
        candidate_id = state.candidateId
        interview_id = state.interviewId

        # 1. Store Skill Evidence & Knowledge Gaps per Topic Assessment
        for topic_id, tass in state.topicsAssessed.items():
            topic_name = tass.topic_name
            if len(tass.evidence) > 0:
                ev_summary = "; ".join(tass.evidence[:2])
                item = CandidateMemoryItem(
                    memory_id=f"mem_sk_{interview_id[:8]}_{topic_id[:8]}",
                    candidate_id=candidate_id,
                    type=MemoryType.SKILL_EVIDENCE,
                    topic=topic_name,
                    skill=f"{topic_name} Depth Level {tass.depth}",
                    level=tass.depth,
                    evidence=ev_summary,
                    confidence=round(tass.knowledge_confidence or 0.85, 2),
                    source_interview=interview_id,
                    status="active"
                )
                self.store_memory(item)
                stored_items.append(item)

        # 2. Store Knowledge Gaps
        for gap in state.knowledgeGaps:
            item = CandidateMemoryItem(
                memory_id=f"mem_gap_{interview_id[:8]}_{uuid.uuid4().hex[:6]}",
                candidate_id=candidate_id,
                type=MemoryType.KNOWLEDGE_GAP,
                topic="Technical Knowledge",
                skill=gap,
                evidence=f"Demonstrated insufficient evidence on {gap} during interview session",
                confidence=0.82,
                source_interview=interview_id,
                status="active"
            )
            self.store_memory(item)
            stored_items.append(item)

        # 3. Store Expression Patterns
        if state.expressionGaps:
            pattern_summary = "; ".join(state.expressionGaps[:2])
            item = CandidateMemoryItem(
                memory_id=f"mem_exp_{interview_id[:8]}",
                candidate_id=candidate_id,
                type=MemoryType.EXPRESSION_PATTERN,
                topic="Technical Communication",
                pattern=pattern_summary,
                evidence=f"Observed technical expression pattern: {pattern_summary}",
                confidence=0.85,
                source_interview=interview_id,
                status="active"
            )
            self.store_memory(item)
            stored_items.append(item)

        # 4. Store Misconceptions
        for misc in state.misconceptions:
            item = CandidateMemoryItem(
                memory_id=f"mem_misc_{interview_id[:8]}_{uuid.uuid4().hex[:6]}",
                candidate_id=candidate_id,
                type=MemoryType.MISCONCEPTION,
                topic="Technical Fundamentals",
                skill=misc.misconception,
                evidence=f"Flagged misconception: '{misc.misconception}' (Status: {misc.status})",
                confidence=0.88,
                source_interview=interview_id,
                status="resolved" if misc.status == "RESOLVED" else "active"
            )
            self.store_memory(item)
            stored_items.append(item)

        logger.info(f"[MEMORY_WRITTEN] Successfully stored {len(stored_items)} longitudinal memories for candidate {candidate_id}")
        return stored_items

    def get_relevant_context(
        self,
        candidate_id: str,
        selected_topics: Optional[List[str]] = None,
        target_role: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> MemoryContext:
        """
        Retrieves relevant longitudinal memories and constructs a MemoryContext
        for the Interview Planner and Candidate Report.
        """
        logger.info(f"[MEMORY_RETRIEVAL_STARTED] Retrieving memory context for candidate {candidate_id}")
        
        # Primary search via Breeth or Local Fallback
        all_memories = self.local_provider.get_candidate_memories(candidate_id)
        if self.breeth_provider.is_available():
            breeth_mems = self.breeth_provider.search_memories(candidate_id=candidate_id, topics=selected_topics, limit=50)
            if breeth_mems:
                all_memories = breeth_mems

        if not all_memories:
            logger.info(f"[MEMORY_RETRIEVAL_COMPLETED] Baseline candidate {candidate_id}: No historical memory found.")
            return MemoryContext(
                candidate_id=candidate_id,
                total_previous_interviews=0,
                summary_hypothesis="Baseline candidate interview (No prior memory found)."
            )

        # Separate memories by type
        strengths = [m for m in all_memories if m.type == MemoryType.SKILL_EVIDENCE and (m.level or 0) >= 3]
        gaps = [m for m in all_memories if m.type == MemoryType.KNOWLEDGE_GAP or (m.type == MemoryType.SKILL_EVIDENCE and (m.level or 0) < 3)]
        misconceptions = [m for m in all_memories if m.type == MemoryType.MISCONCEPTION and m.status == "active"]
        exp_patterns = [m.evidence for m in all_memories if m.type == MemoryType.EXPRESSION_PATTERN]

        # Extract unique previous interviews
        unique_sessions = {m.source_interview for m in all_memories if m.source_interview}

        # Detect persistent gaps across multiple sessions
        persistent_gaps = self.detect_persistent_gaps(candidate_id, all_memories)

        # Detect growth
        growth_history = self.detect_growth(candidate_id, all_memories)

        summary = f"Candidate has {len(unique_sessions)} previous interview(s). Demonstrated strengths in {', '.join([s.topic for s in strengths[:2]]) or 'core CS'}. Identified {len(persistent_gaps)} persistent gap(s)."

        ctx = MemoryContext(
            candidate_id=candidate_id,
            total_previous_interviews=len(unique_sessions),
            recent_memories=all_memories[:10],
            demonstrated_strengths=strengths,
            recurring_gaps=persistent_gaps,
            growth_history=growth_history,
            unresolved_misconceptions=misconceptions,
            expression_patterns=exp_patterns[:3],
            summary_hypothesis=summary
        )

        logger.info(f"[MEMORY_RETRIEVAL_COMPLETED] Retrieved memory context for candidate {candidate_id} ({len(unique_sessions)} previous sessions)")
        return ctx

    def detect_growth(
        self,
        candidate_id: str,
        memories: List[CandidateMemoryItem]
    ) -> List[GrowthEvent]:
        """Compares historical skill levels across interviews to identify candidate growth."""
        growth_events: List[GrowthEvent] = []
        topic_history: Dict[str, List[Tuple[int, str, str]]] = {}

        for m in memories:
            if m.type == MemoryType.SKILL_EVIDENCE and m.level is not None:
                if m.topic not in topic_history:
                    topic_history[m.topic] = []
                topic_history[m.topic].append((m.level, m.source_interview, m.timestamp))

        for topic, history in topic_history.items():
            if len(history) >= 2:
                # Sort by timestamp/interview
                sorted_hist = sorted(history, key=lambda x: x[2])
                first_level, first_interview, _ = sorted_hist[0]
                latest_level, latest_interview, _ = sorted_hist[-1]

                if latest_level > first_level:
                    diff = latest_level - first_level
                    growth_events.append(GrowthEvent(
                        candidate_id=candidate_id,
                        topic=topic,
                        previous_level=first_level,
                        current_level=latest_level,
                        growth=diff,
                        confidence=0.89,
                        evidence=f"Candidate improved depth in {topic} from Level {first_level} to Level {latest_level}.",
                        source_interviews=[first_interview, latest_interview]
                    ))
                    logger.info(f"[GROWTH_DETECTED] Growth detected for {candidate_id} in {topic}: Level {first_level} -> {latest_level}")

        return growth_events

    def detect_persistent_gaps(
        self,
        candidate_id: str,
        memories: List[CandidateMemoryItem]
    ) -> List[PersistentGap]:
        """Identifies technical gaps that recurred across multiple interview sessions."""
        gap_map: Dict[str, List[Tuple[str, str]]] = {}

        for m in memories:
            if m.type == MemoryType.KNOWLEDGE_GAP or (m.type == MemoryType.SKILL_EVIDENCE and (m.level or 0) <= 2):
                key = f"{m.topic}:{m.skill or 'Core Concept'}"
                if key not in gap_map:
                    gap_map[key] = []
                gap_map[key].append((m.evidence, m.source_interview))

        persistent_gaps: List[PersistentGap] = []
        for key, occurrences in gap_map.items():
            unique_interviews = list({occ[1] for occ in occurrences})
            if len(unique_interviews) >= 2:
                topic, skill = key.split(":", 1)
                p_gap = PersistentGap(
                    candidate_id=candidate_id,
                    topic=topic,
                    skill=skill,
                    occurrences_count=len(unique_interviews),
                    evidence_samples=[occ[0] for occ in occurrences[:3]],
                    source_interviews=unique_interviews,
                    status="active"
                )
                persistent_gaps.append(p_gap)
                logger.info(f"[PERSISTENT_GAP_DETECTED] Persistent gap detected for {candidate_id} in {topic} ({skill}) across {len(unique_interviews)} sessions")

        return persistent_gaps

    def delete_candidate_memories(self, candidate_id: str) -> bool:
        """Deletes all candidate memory across Breeth and Local storage (Data Minimization)."""
        b_res = self.breeth_provider.delete_candidate_memories(candidate_id) if self.breeth_provider.is_available() else True
        l_res = self.local_provider.delete_candidate_memories(candidate_id)
        logger.info(f"[MEMORY_DELETED] Deleted candidate memories for {candidate_id}")
        return b_res and l_res

candidate_memory_service = CandidateMemoryService()
