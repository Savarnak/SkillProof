export type SkillDepthLevel =
  | 'Recognition'
  | 'Understanding'
  | 'Application'
  | 'Engineering'
  | 'System Design'
  | 'Transfer';

export type AdaptiveAction =
  | 'Go deeper'
  | 'Probe missing concept'
  | 'Rephrase'
  | 'Recover/scaffold'
  | 'Change topic'
  | 'Cross-domain transfer';

export type SessionStatus = 'initialized' | 'in_progress' | 'completed';

export interface SkillAssessment {
  topic: string;
  knowledge: number;
  expression: number;
  application: number;
  depth_level: SkillDepthLevel;
  evidence: string[];
  misconceptions: string[];
}

export interface QuestionAnswerTurn {
  turn_index: number;
  day_id: string;
  topic_id: string;
  depth_level: SkillDepthLevel;
  question_text: string;
  candidate_answer?: string;
  next_action?: AdaptiveAction;
  scaffold_used?: string;
  misconception_flagged?: string;
  turn_analysis?: string;
}

export interface DeterministicState {
  min_questions: number;
  min_curriculum_days: number;
  total_questions_asked: number;
  covered_days: string[];
  covered_topics: string[];
  meets_completion_criteria: boolean;
}

export interface InterviewSession {
  session_id: string;
  candidate_id: string;
  curriculum_id: string;
  status: SessionStatus;
  current_turn_index: number;
  turns: QuestionAnswerTurn[];
  assessments: Record<string, SkillAssessment>;
  deterministic_state: DeterministicState;
  created_at: string;
  updated_at: string;
}
