export type SkillDepthLevel = 1 | 2 | 3 | 4 | 5 | 6;

export type AdaptiveAction =
  | 'GO_DEEPER'
  | 'PROBE'
  | 'REPHRASE'
  | 'RECOVER'
  | 'EXPRESSION_SCAFFOLD'
  | 'CHANGE_TOPIC'
  | 'TRANSFER'
  | 'END';

export type SessionStatus = 'initialized' | 'in_progress' | 'completed';
export type MisconceptionStatus = 'identified' | 'probed' | 'resolved' | 'persists';

export interface MisconceptionItem {
  topic: string;
  misconception: string;
  status: MisconceptionStatus;
  detected_at_turn: number;
  resolution_turn?: number;
}

export interface TopicAssessment {
  topic_id: string;
  topic_name: string;
  day_id: string;
  day_number: number;
  knowledge: number;
  expression: number;
  application: number;
  depth: number;
  status: string;
  evidence: string[];
  pending_evidence_list: string[];
  knowledge_confidence: number;
  expression_confidence: number;
  expression_recovery_used: boolean;
  misconceptions: string[];
}

export interface AnswerEvaluation {
  technicalCorrectness: number;
  conceptualDepth: number;
  relevance: number;
  reasoning: number;
  application: number;
  expressionClarity: number;
  answerStructure: number;
  confidenceOfAssessment: number;
  strengths: string[];
  missingConcepts: string[];
  misconceptions: string[];
  expressionIssues: string[];
  evidence: string[];
  isStrugglingOrDontKnow: boolean;
  isExpressionUnclear: boolean;
  recommendedNextAction: AdaptiveAction;
  recommendedReasonCode: string;
}

export interface InterviewDecision {
  action: AdaptiveAction;
  topic_id: string;
  target_depth: number;
  reasonCode: string;
  scaffold_prompt?: string;
  transfer_domain?: string;
}

export interface QuestionTurn {
  turn_index: number;
  question_id: string;
  topic_id: string;
  day_id: string;
  day_number: number;
  depth_level: number;
  question_text: string;
  candidate_answer?: string;
  evaluation?: AnswerEvaluation;
  decision?: InterviewDecision;
  timestamp: string;
}

export interface InterviewState {
  interviewId: string;
  candidateId: string;
  curriculumId: string;
  questionCount: number;
  curriculumDaysCovered: number[];
  coveredDayIds: string[];
  topicsAssessed: Record<string, TopicAssessment>;
  currentTopic: string;
  currentDayId: string;
  currentDepth: number;
  conversationHistory: QuestionTurn[];
  skillEvidence: string[];
  pendingEvidence: string[];
  strengths: string[];
  knowledgeGaps: string[];
  expressionGaps: string[];
  misconceptions: MisconceptionItem[];
  transferChallengesUsed: string[];
  profileVsEvidenceDivergence: string[];
  selectedTopics?: string[];
  selectedCategories?: string[];
  targetRole?: string | null;
  jobDescription?: string | null;
  interviewMode?: string;
  jdRequirementCoverage?: any[];
  interviewStatus: SessionStatus;
  completionReason?: string;
  minQuestions: number;
  minCurriculumDays: number;
  maxQuestions: number;
  canConclude: boolean;
  created_at: string;
  updated_at: string;
}

export interface WeightedScoreBreakdown {
  technicalKnowledge: number;
  reasoning: number;
  application: number;
  expression: number;
  transfer: number;
  overallReadiness: number;
}

export interface TopicEvidenceExpander {
  topic_id: string;
  topic_name: string;
  score: number;
  confidence: number;
  evidenceCount: number;
  sourceQuestions: number[];
  evidenceQuotes: string[];
  statusTag: string;
}

export interface RefinementDiff {
  questionIndex: number;
  questionText: string;
  originalAnswer: string;
  interviewReadyVersion: string;
  diffAdditions: string[];
  diffDeletions: string[];
  deliveryFormula: string;
  whatWasGood: string;
  whatCouldImprove: string;
}

export interface GrowthItem {
  topic: string;
  previousLevel: number;
  currentLevel: number;
  growthAmount: number;
  evidence: string;
}

export interface ProgressChangeItem {
  topic: string;
  previousStatus: string;
  currentStatus: string;
  changeTag: string;
}

export interface CoachedAnswer {
  questionIndex: number;
  questionText: string;
  originalAnswer: string;
  strengths: string[];
  whatHeldItBack: string;
  interviewReadyVersion: string;
  deliveryFormulaName: string;
  deliveryFormulaSteps: string[];
}

export interface MisconceptionInsight {
  topic: string;
  misconception: string;
  whatsActuallyTrue: string;
  howToRememberIt: string;
  status: string;
}

export interface PersistentGapInsight {
  topic: string;
  whyItMatters: string;
  whatToPractice: string;
  suggestedNextChallenge: string;
  isResolved?: boolean;
}

export interface KnowledgeVsExpressionInsight {
  show: boolean;
  headline: string;
  technicalDemonstrated: string;
  communicationImpact: string;
  howToImprove: string;
}

export interface ActionPlan {
  nextSteps: string[];
}

export interface InterviewReport {
  interviewId: string;
  candidateName: string;
  curriculumTitle: string;
  totalQuestionsAsked: number;
  uniqueDaysCovered: number;
  weightedScores: WeightedScoreBreakdown;
  topicEvidenceExpanders: TopicEvidenceExpander[];
  demonstratedStrengths: string[];
  knowledgeGaps: string[];
  expressionGaps: string[];
  showKnowledgeVsExpressionInsight: boolean;
  insightMessage?: string;
  knowledgeVsExpressionInsight?: KnowledgeVsExpressionInsight;
  misconceptionsFound: MisconceptionItem[];
  misconceptionInsights?: MisconceptionInsight[];
  profileDivergenceNotes: string[];
  transferAbility: string;
  interviewMode?: string;
  jdRequirementCoverage?: any[];
  refinementDiffs: RefinementDiff[];
  coachedAnswers?: CoachedAnswer[];
  personalPlaybookFormulas: Record<string, string>[];
  isFirstTimeCandidate?: boolean;
  growthSummary?: GrowthItem[];
  whatChangedSinceLastInterview?: ProgressChangeItem[];
  persistentGapInsights?: PersistentGapInsight[];
  actionPlan?: ActionPlan;
  summaryFeedback: string;
}
