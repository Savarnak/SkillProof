export interface CompletedMission {
  mission_id: string;
  day_id: string;
  score: number;
  completed_at: string;
}

export interface LearningSignals {
  demonstrated_strengths: string[];
  known_gaps: string[];
  expression_notes?: string;
  suspected_misconceptions: string[];
}

export interface Candidate {
  candidate_id: string;
  name: string;
  email: string;
  is_synthetic_demo: boolean;
  background_summary: string;
  target_role: string;
  completed_missions: CompletedMission[];
  learning_signals: LearningSignals;
}
