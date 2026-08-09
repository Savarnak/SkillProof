import { InterviewState, InterviewReport } from "../types/interview";

// Compositional API Base URL resolution:
// In production on Vercel: defaults to "" (same-origin relative /api calls)
// In local dev browser: defaults to "http://localhost:8000" if NEXT_PUBLIC_API_URL is unset
const getApiBaseUrl = (): string => {
  if (process.env.NEXT_PUBLIC_API_URL !== undefined && process.env.NEXT_PUBLIC_API_URL !== "") {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") && process.env.NODE_ENV === "development") {
    return "http://localhost:8000";
  }
  return "";
};

const API_BASE_URL = getApiBaseUrl();

export interface StartInterviewResponse {
  state: InterviewState;
  current_question: string;
}

export interface AnswerResponse {
  state: InterviewState;
  next_question?: string;
  is_completed: boolean;
}

export interface StartInterviewOptions {
  candidateId?: string;
  curriculumId?: string;
  selectedTopics?: string[];
  selectedCategories?: string[];
  targetRole?: string;
  jobDescription?: string;
  mode?: "learning_journey" | "job_description";
}

export async function startInterview(
  options: StartInterviewOptions = {}
): Promise<StartInterviewResponse> {
  const payload = {
    candidate_id: options.candidateId || "cand_alex_rivers_001",
    curriculum_id: options.curriculumId || "curr_ai_eng_v1",
    selected_topics: options.selectedTopics || [],
    selected_categories: options.selectedCategories || [],
    target_role: options.targetRole || null,
    job_description: options.jobDescription || null,
    mode: options.mode || "learning_journey",
  };

  const res = await fetch(`${API_BASE_URL}/api/interview/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Failed to start interview (${res.status})`);
  }
  return res.json();
}

export async function submitAnswer(
  interviewId: string,
  answerText: string
): Promise<AnswerResponse> {
  const res = await fetch(`${API_BASE_URL}/api/interview/${interviewId}/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answer_text: answerText }),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Failed to submit answer (${res.status})`);
  }
  return res.json();
}

export async function getInterviewState(interviewId: string): Promise<InterviewState> {
  const res = await fetch(`${API_BASE_URL}/api/interview/${interviewId}/state`);
  if (!res.ok) {
    throw new Error(`Failed to fetch session state (${res.status})`);
  }
  return res.json();
}

export async function finishInterview(interviewId: string): Promise<InterviewState> {
  const res = await fetch(`${API_BASE_URL}/api/interview/${interviewId}/finish`, {
    method: "POST",
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Cannot conclude interview (${res.status})`);
  }
  return res.json();
}

export async function getInterviewReport(interviewId: string): Promise<InterviewReport> {
  const res = await fetch(`${API_BASE_URL}/api/interview/${interviewId}/report`);
  if (!res.ok) {
    throw new Error(`Failed to fetch report (${res.status})`);
  }
  return res.json();
}
