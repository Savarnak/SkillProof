from typing import List, Dict, Any, Tuple
from app.schemas.curriculum import Curriculum, Topic, CurriculumDay
from app.schemas.candidate import Candidate
from app.interview.schemas import TopicAssessment, TopicStatus

class InterviewPlanner:
    """Creates the initial adaptive assessment strategy based on candidate background & curriculum."""
    
    @staticmethod
    def create_initial_plan(
        candidate: Candidate,
        curriculum: Curriculum
    ) -> Tuple[Dict[str, TopicAssessment], List[str], str, str, int]:
        """
        Builds initial TopicAssessment map, global pendingEvidence list, and starting topic & day.
        Returns: (topic_assessments_map, global_pending_evidence, initial_topic_id, initial_day_id, initial_depth)
        """
        topics_map: Dict[str, TopicAssessment] = {}
        global_pending_evidence: List[str] = []
        
        # 1. Flatten all topics across curriculum days
        all_topics: List[Tuple[CurriculumDay, Topic]] = []
        for module in curriculum.modules:
            for day in module.days:
                for topic in day.topics:
                    all_topics.append((day, topic))
        
        # 2. Check candidate's completed missions to set baseline hypothesis
        completed_day_ids = {m.day_id for m in candidate.completed_missions}
        
        for day, topic in all_topics:
            status = TopicStatus.NOT_STARTED
            initial_depth = 1
            
            # Extract learning objectives as pending evidence items
            pending_items = topic.learning_objectives.copy() if topic.learning_objectives else [f"{topic.name} core concepts"]
            for item in pending_items:
                if item not in global_pending_evidence:
                    global_pending_evidence.append(item)

            if day.day_id in completed_day_ids:
                initial_depth = 2
            
            topics_map[topic.topic_id] = TopicAssessment(
                topic_id=topic.topic_id,
                topic_name=topic.name,
                day_id=day.day_id,
                day_number=day.day_number,
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
        
        # 3. Select starting topic
        start_day, start_topic = all_topics[0]
        start_depth = topics_map[start_topic.topic_id].depth
        
        return topics_map, global_pending_evidence, start_topic.topic_id, start_day.day_id, start_depth
