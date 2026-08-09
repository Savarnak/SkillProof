export interface Topic {
  topic_id: string;
  name: string;
  description: string;
  learning_objectives: string[];
  key_tools: string[];
}

export interface CurriculumDay {
  day_number: number;
  day_id: string;
  title: string;
  topics: Topic[];
}

export interface Module {
  module_id: string;
  title: string;
  days: CurriculumDay[];
}

export interface Curriculum {
  curriculum_id: string;
  title: string;
  description: string;
  version: string;
  modules: Module[];
}
