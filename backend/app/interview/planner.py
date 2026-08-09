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
    ) -> Tuple[Dict[str, TopicAssessment], str, str, int]:
        """
        Builds initial TopicAssessment map and determines starting topic & day.
        Returns: (topic_assessments_map, initial_topic_id, initial_day_id, initial_depth)
        """
        topics_map: Dict[str, TopicAssessment] = {}
        
        # 1. Flatten all topics across curriculum days
        all_topics: List[Tuple[CurriculumDay, Topic]] = []
        for module in curriculum.modules:
            for day in module.days:
                for topic in day.topics:
                    all_topics.append((day, topic))
        
        # 2. Check candidate's completed missions to set baseline
        completed_day_ids = {m.day_id for m in candidate.completed_missions}
        
        for day, topic in all_topics:
            status = TopicStatus.NOT_STARTED
            initial_depth = 1
            
            # If candidate completed mission on this day, boost initial status expectation
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
                misconceptions=[]
            )
        
        # 3. Select starting topic (prefer Day 1 or topic candidate has basic familiarity with)
        start_day, start_topic = all_topics[0]
        start_depth = topics_map[start_topic.topic_id].depth
        
        return topics_map, start_topic.topic_id, start_day.day_id, start_depth
