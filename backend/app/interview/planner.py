from typing import List, Dict, Any, Tuple, Optional
import re
from app.schemas.curriculum import Curriculum, Topic, CurriculumDay
from app.schemas.candidate import Candidate
from app.interview.schemas import TopicAssessment, TopicStatus

class InterviewPlanner:
    """Creates the initial adaptive assessment strategy based on candidate background, selected topics, & JD."""

    @staticmethod
    def _slugify(name: str) -> str:
        clean = re.sub(r'[^a-zA-Z0-9]+', '_', name.strip().lower()).strip('_')
        return f"top_{clean}" if clean else "top_custom"

    @classmethod
    def create_initial_plan(
        cls,
        candidate: Candidate,
        curriculum: Curriculum,
        selected_topics: List[str] = [],
        target_role: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> Tuple[Dict[str, TopicAssessment], List[str], str, str, int]:
        """
        Builds initial TopicAssessment map, global pendingEvidence list, and starting topic & day.
        Respects custom selected topics, target role, and JD requirements.
        """
        topics_map: Dict[str, TopicAssessment] = {}
        global_pending_evidence: List[str] = []

        # 1. Determine active topics list
        active_topic_names: List[str] = []
        if selected_topics:
            active_topic_names = selected_topics.copy()
        
        # If no custom topics selected, fallback to standard curriculum topics
        if not active_topic_names and curriculum:
            for module in curriculum.modules:
                for day in module.days:
                    for topic in day.topics:
                        active_topic_names.append(topic.name)

        if not active_topic_names:
            active_topic_names = ["Operating Systems", "DBMS", "Computer Networks", "Software Architecture"]

        # 2. Build TopicAssessment objects mapped across days
        completed_day_ids = {m.day_id for m in candidate.completed_missions} if candidate else set()

        for idx, topic_name in enumerate(active_topic_names):
            day_num = (idx % 5) + 1
            day_id = f"day_{day_num}"
            topic_id = cls._slugify(topic_name)

            status = TopicStatus.NOT_STARTED
            initial_depth = 2 if day_id in completed_day_ids else 1

            pending_items = [
                f"{topic_name} fundamentals and core architecture",
                f"{topic_name} production scaling and trade-offs"
            ]

            for item in pending_items:
                if item not in global_pending_evidence:
                    global_pending_evidence.append(item)

            topics_map[topic_id] = TopicAssessment(
                topic_id=topic_id,
                topic_name=topic_name,
                day_id=day_id,
                day_number=day_num,
                knowledge=0.0,
                expression=0.0,
                application=0.0,
                depth=initial_depth,
                status=status,
                evidence=[],
                pending_evidence_list=pending_items,
                knowledge_confidence=0.0,
                expression_confidence=0.0,
                expression_recovery_used=False,
                misconceptions=[]
            )

        # 3. Select initial starting topic
        first_topic_id = list(topics_map.keys())[0]
        first_topic = topics_map[first_topic_id]
        
        return topics_map, global_pending_evidence, first_topic_id, first_topic.day_id, first_topic.depth
