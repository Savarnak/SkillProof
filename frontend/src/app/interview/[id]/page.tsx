"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Cpu, ArrowRight, CheckCircle2, AlertCircle, RefreshCw, ArrowLeft } from "lucide-react";
import JourneyTracker from "../../../components/JourneyTracker";
import QuestionCard from "../../../components/QuestionCard";
import AnswerInput from "../../../components/AnswerInput";
import CrossDomainCard from "../../../components/CrossDomainCard";
import LeaveInterviewModal from "../../../components/LeaveInterviewModal";
import { getInterviewState, submitAnswer, finishInterview } from "../../../lib/api";
import { InterviewState, QuestionTurn } from "../../../types/interview";

export default function InterviewScreen() {
  const params = useParams();
  const router = useRouter();
  const interviewId = params.id as string;

  const [state, setState] = useState<InterviewState | null>(null);
  const [currentTurn, setCurrentTurn] = useState<QuestionTurn | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showLeaveModal, setShowLeaveModal] = useState(false);

  useEffect(() => {
    const loadSession = async () => {
      try {
        setIsLoading(true);
        const fetchedState = await getInterviewState(interviewId);
        setState(fetchedState);
        if (fetchedState.conversationHistory.length > 0) {
          setCurrentTurn(fetchedState.conversationHistory[fetchedState.conversationHistory.length - 1]);
        }
      } catch (err: any) {
        setError(err.message || "Failed to load interview session state.");
      } finally {
        setIsLoading(false);
      }
    };

    if (interviewId) {
      loadSession();
    }
  }, [interviewId]);

  const handleSubmitAnswerText = async (text: string) => {
    if (!interviewId || isSubmitting) return;
    setIsSubmitting(true);
    setError(null);
    try {
      const res = await submitAnswer(interviewId, text);
      setState(res.state);
      if (res.state.conversationHistory.length > 0) {
        setCurrentTurn(res.state.conversationHistory[res.state.conversationHistory.length - 1]);
      }
    } catch (err: any) {
      setError(err.message || "Failed to submit answer.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDontKnowClick = () => {
    handleSubmitAnswerText("I don't know or remember this topic.");
  };

  const handleFinishAndNavigateReport = async () => {
    if (!interviewId) return;
    setIsSubmitting(true);
    try {
      await finishInterview(interviewId);
      router.push(`/report/${interviewId}`);
    } catch (err: any) {
      setError(err.message || "Failed to conclude interview.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0b0f19] text-slate-300">
        <div className="flex items-center gap-3 glass-panel p-6 rounded-2xl border border-slate-800 animate-pulse">
          <RefreshCw className="w-5 h-5 text-indigo-400 animate-spin" />
          <span className="text-sm font-medium">Connecting to Interview Engine...</span>
        </div>
      </div>
    );
  }

  if (error && !state) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-[#0b0f19] text-slate-200 space-y-4">
        <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-900/50 text-rose-300 text-sm max-w-md flex items-center gap-2">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
        <button
          onClick={() => router.push("/")}
          className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold"
        >
          Return to Home
        </button>
      </div>
    );
  }

  const isTransferActive = currentTurn?.decision?.action === "TRANSFER";
  const canConclude = state?.canConclude;

  return (
    <main className="min-h-screen flex flex-col justify-between bg-[#0b0f19] text-slate-100">
      {/* Top Header with Navigation Safety */}
      <div className="w-full bg-slate-950/80 border-b border-slate-900 px-4 py-2 flex items-center justify-between text-xs">
        <button
          onClick={() => setShowLeaveModal(true)}
          className="inline-flex items-center gap-2 font-semibold text-slate-400 hover:text-slate-200 transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </button>

        <span className="text-slate-500 font-mono text-[11px]">
          Session: {interviewId.slice(0, 12)}...
        </span>
      </div>

      {/* Top Journey Tracker Header */}
      <JourneyTracker
        currentTurn={state?.questionCount || 1}
        minQuestions={state?.minQuestions || 8}
        coveredTopicsCount={state?.curriculumDaysCovered?.length || 1}
        currentTopicName={
          (currentTurn && state?.topicsAssessed[currentTurn.topic_id]?.topic_name) ||
          currentTurn?.topic_id ||
          "Technical Assessment"
        }
        targetRole={state?.targetRole}
      />

      {/* Main Conversation Container */}
      <section className="w-full max-w-3xl mx-auto flex-1 p-4 md:p-6 space-y-6 my-auto">
        {error && (
          <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-900/50 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Transfer Challenge Unlocked Banner */}
        {isTransferActive && (
          <CrossDomainCard
            domainName={currentTurn?.decision?.transfer_domain || "Logistics Exception Tracking"}
            topicName={
              (currentTurn && state?.topicsAssessed[currentTurn.topic_id]?.topic_name) ||
              currentTurn?.topic_id ||
              "Core Technical Architecture"
            }
          />
        )}

        {/* Current Active Question Card */}
        {currentTurn && (
          <QuestionCard
            questionText={currentTurn.question_text}
            topicName={
              state?.topicsAssessed[currentTurn.topic_id]?.topic_name ||
              currentTurn.topic_id
            }
            depthLevel={currentTurn.depth_level}
            isScaffolded={currentTurn.decision?.action === "RECOVER" || currentTurn.decision?.action === "EXPRESSION_SCAFFOLD"}
          />
        )}

        {/* Render Answer Input if active, or Completion Card if limit reached */}
        {!canConclude && state?.interviewStatus !== "completed" ? (
          <AnswerInput
            onSubmitAnswer={handleSubmitAnswerText}
            onDontKnow={handleDontKnowClick}
            isLoading={isSubmitting}
          />
        ) : (
          <div className="p-6 rounded-3xl bg-gradient-to-r from-emerald-950/80 via-slate-900 to-slate-950 border border-emerald-500/40 text-left space-y-4 animate-fadeIn shadow-2xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> Interview Complete
              </span>
              <span className="text-xs text-slate-400 font-mono">
                {state?.questionCount || 8} Questions Completed | {state?.curriculumDaysCovered.length || 4} Topics Assessed
              </span>
            </div>
            <p className="text-sm text-slate-200 leading-relaxed">
              We&apos;ve collected sufficient technical evidence across your chosen topics. Your personalized Discovery Report and Technical Delivery Playbook are ready.
            </p>
            <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
              <button
                onClick={handleFinishAndNavigateReport}
                disabled={isSubmitting}
                className="w-full py-4 px-6 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-base flex items-center justify-center gap-2 shadow-xl shadow-emerald-600/30 transition-all cursor-pointer"
              >
                <span>View My Discovery Report</span>
                <ArrowRight className="w-5 h-5" />
              </button>

              <button
                onClick={() => router.push("/")}
                className="w-full sm:w-auto py-4 px-5 rounded-2xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-sm font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Home</span>
              </button>
            </div>
          </div>
        )}
      </section>

      {/* Leave Active Interview Modal */}
      <LeaveInterviewModal
        isOpen={showLeaveModal}
        onCancel={() => setShowLeaveModal(false)}
        onConfirm={() => router.push("/")}
      />

      {/* Footer */}
      <footer className="w-full py-4 text-center text-xs text-slate-600 border-t border-slate-900">
        SkillProof — Adaptive Technical Conversation
      </footer>
    </main>
  );
}
