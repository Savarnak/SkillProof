"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ShieldCheck, Award, Brain, ArrowRight, AlertTriangle, CheckCircle2, RefreshCw, Lightbulb, UserCheck, HelpCircle, ArrowLeft, FileText, Target, Activity, Flame, Layers
} from "lucide-react";
import { getInterviewReport } from "../../../lib/api";
import { InterviewReport } from "../../../types/interview";
import EvidenceExpander from "../../../components/EvidenceExpander";
import TopicEvidenceMap from "../../../components/TopicEvidenceMap";
import GrowthProgressCard from "../../../components/GrowthProgressCard";
import AnswerCoach from "../../../components/AnswerCoach";
import MisconceptionReportCard from "../../../components/MisconceptionReportCard";
import ActionPlanCard from "../../../components/ActionPlanCard";

export default function ReportPage() {
  const params = useParams();
  const router = useRouter();
  const interviewId = params.id as string;

  const [report, setReport] = useState<InterviewReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        setIsLoading(true);
        const data = await getInterviewReport(interviewId);
        setReport(data);
      } catch (err: any) {
        setError(err.message || "Failed to load interview discovery report.");
      } finally {
        setIsLoading(false);
      }
    };

    if (interviewId) {
      fetchReport();
    }
  }, [interviewId]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0b0f19] text-slate-300">
        <div className="flex items-center gap-3 glass-panel p-6 rounded-2xl border border-slate-800 animate-pulse">
          <RefreshCw className="w-5 h-5 text-indigo-400 animate-spin" />
          <span className="text-sm font-medium">Generating Evidence Discovery Report...</span>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-[#0b0f19] text-slate-200 space-y-4">
        <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-900/50 text-rose-300 text-sm">
          {error || "Report not found."}
        </div>
        <button
          onClick={() => router.push("/")}
          className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Home</span>
        </button>
      </div>
    );
  }

  const scores = report.weightedScores;
  const kvInsight = report.knowledgeVsExpressionInsight;

  return (
    <main className="min-h-screen flex flex-col items-center justify-between p-4 sm:p-6 md:p-12 bg-gradient-to-b from-[#0b0f19] via-[#0f172a] to-[#0b0f19] text-slate-100">
      {/* Top Header Navigation */}
      <header className="w-full max-w-4xl flex items-center justify-between py-4 border-b border-slate-800/80">
        <button
          onClick={() => router.push("/")}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-slate-200 transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </button>

        <span className="px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-[11px] font-semibold">
          Discovery Report
        </span>
      </header>

      <section className="w-full max-w-4xl my-6 md:my-8 space-y-8">
        {/* Header Title */}
        <div className="space-y-2 text-left">
          <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
            YOUR TECHNICAL SNAPSHOT
          </span>
          <h2 className="text-2xl sm:text-3xl md:text-5xl font-extrabold text-white tracking-tight leading-tight">
            Here&apos;s what you demonstrated, {report.candidateName}.
          </h2>
          <p className="text-slate-400 text-xs sm:text-sm">
            Evaluated across {report.totalQuestionsAsked} questions covering {report.uniqueDaysCovered} topics.
          </p>
        </div>

        {/* Job Description Readiness Matrix if present */}
        {report.jdRequirementCoverage && report.jdRequirementCoverage.length > 0 && (
          <div className="p-5 sm:p-6 md:p-8 rounded-3xl glass-panel border border-indigo-500/30 text-left space-y-4">
            <h3 className="text-xs sm:text-sm font-semibold text-indigo-300 flex items-center gap-2">
              <FileText className="w-4 h-4 text-indigo-400" />
              Job Description Readiness Matrix
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {report.jdRequirementCoverage.map((item: any, idx: number) => (
                <div key={idx} className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between text-xs">
                  <span className="font-semibold text-white truncate max-w-[140px]">{item.requirement}</span>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                    item.evidence === "Strong"
                      ? "bg-emerald-950/60 border-emerald-500/40 text-emerald-400"
                      : item.evidence === "Demonstrated"
                      ? "bg-indigo-950/60 border-indigo-500/40 text-indigo-300"
                      : item.evidence === "Developing"
                      ? "bg-amber-950/60 border-amber-500/40 text-amber-300"
                      : "bg-slate-900 border-slate-800 text-slate-500"
                  }`}>
                    {item.evidence === "Strong" ? "✓ Strong" : item.evidence === "Demonstrated" ? "✓ Demonstrated" : item.evidence === "Developing" ? "△ Developing" : "○ Not assessed"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 1. YOUR INTERVIEW PROFILE (Psychologically Supportive Progress Indicators) */}
        <div className="p-5 sm:p-6 md:p-8 rounded-3xl glass-panel border border-slate-800 space-y-6 text-left">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
            <div className="space-y-1">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Activity className="w-4 h-4 text-indigo-400" />
                YOUR INTERVIEW PROFILE
              </span>
              <p className="text-xs text-slate-400">
                Your technical understanding is stronger than your first responses suggested.
              </p>
            </div>

            <div className="px-3.5 py-1.5 rounded-2xl bg-indigo-950/40 border border-indigo-500/30 text-indigo-300 text-xs font-bold shrink-0 self-start sm:self-auto">
              Overall Alignment: {scores.overallReadiness}%
            </div>
          </div>

          <div className="space-y-4">
            {/* Technical Knowledge */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-white">Technical Knowledge</span>
                <span className="font-mono text-indigo-300 font-bold">
                  {Math.round(scores.technicalKnowledge * 100)}% ({scores.technicalKnowledge >= 0.75 ? "Strong" : scores.technicalKnowledge >= 0.50 ? "Demonstrated" : "Developing"})
                </span>
              </div>
              <div className="w-full h-2.5 rounded-full bg-slate-900 overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-gradient-to-r from-indigo-600 to-emerald-400 rounded-full transition-all duration-500"
                  style={{ width: `${Math.max(10, Math.round(scores.technicalKnowledge * 100))}%` }}
                />
              </div>
            </div>

            {/* Application */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-white">Application</span>
                <span className="font-mono text-indigo-300 font-bold">
                  {Math.round(scores.application * 100)}% ({scores.application >= 0.75 ? "Strong" : scores.application >= 0.50 ? "Demonstrated" : "Developing"})
                </span>
              </div>
              <div className="w-full h-2.5 rounded-full bg-slate-900 overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-gradient-to-r from-indigo-600 to-emerald-400 rounded-full transition-all duration-500"
                  style={{ width: `${Math.max(10, Math.round(scores.application * 100))}%` }}
                />
              </div>
            </div>

            {/* Reasoning */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-white">Reasoning</span>
                <span className="font-mono text-indigo-300 font-bold">
                  {Math.round(scores.reasoning * 100)}% ({scores.reasoning >= 0.75 ? "Strong" : scores.reasoning >= 0.50 ? "Demonstrated" : "Developing"})
                </span>
              </div>
              <div className="w-full h-2.5 rounded-full bg-slate-900 overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-gradient-to-r from-indigo-600 to-emerald-400 rounded-full transition-all duration-500"
                  style={{ width: `${Math.max(10, Math.round(scores.reasoning * 100))}%` }}
                />
              </div>
            </div>

            {/* Technical Expression */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-white">Technical Expression</span>
                <span className="font-mono text-amber-300 font-bold">
                  {Math.round(scores.expression * 100)}% ({scores.expression >= 0.75 ? "Strong" : scores.expression >= 0.50 ? "Demonstrated" : "Developing"})
                </span>
              </div>
              <div className="w-full h-2.5 rounded-full bg-slate-900 overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-gradient-to-r from-indigo-600 to-amber-400 rounded-full transition-all duration-500"
                  style={{ width: `${Math.max(10, Math.round(scores.expression * 100))}%` }}
                />
              </div>
            </div>

            {/* Transfer Ability */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-white">Transfer Ability</span>
                <span className="font-mono text-indigo-300 font-bold">
                  {Math.round(scores.transfer * 100)}% ({scores.transfer >= 0.75 ? "Strong" : scores.transfer >= 0.50 ? "Demonstrated" : "Developing"})
                </span>
              </div>
              <div className="w-full h-2.5 rounded-full bg-slate-900 overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-gradient-to-r from-indigo-600 to-emerald-400 rounded-full transition-all duration-500"
                  style={{ width: `${Math.max(10, Math.round(scores.transfer * 100))}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* 2. SPECIAL INSIGHT: "You Knew It But Didn't Show It Clearly" */}
        {((report.showKnowledgeVsExpressionInsight && kvInsight?.show) || report.showKnowledgeVsExpressionInsight) && (
          <div className="p-6 md:p-8 rounded-3xl bg-gradient-to-br from-indigo-950/80 via-slate-900 to-slate-950 border border-indigo-500/30 space-y-3 text-left animate-fadeIn">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-semibold">
              <Brain className="w-3.5 h-3.5 text-indigo-400" />
              <span>Key Observation</span>
            </div>
            <h3 className="text-xl md:text-2xl font-bold text-white">
              {kvInsight?.headline || "You knew it. You just didn't show it clearly."}
            </h3>
            <p className="text-slate-300 text-sm leading-relaxed">
              {kvInsight?.technicalDemonstrated || report.insightMessage}
            </p>
            {kvInsight?.communicationImpact && (
              <p className="text-slate-400 text-xs leading-relaxed">
                <strong>Communication Impact:</strong> {kvInsight.communicationImpact}
              </p>
            )}
            {kvInsight?.howToImprove && (
              <div className="pt-2">
                <span className="px-3 py-1.5 rounded-xl bg-indigo-950/60 border border-indigo-500/30 text-indigo-200 text-xs font-medium inline-block">
                  💡 {kvInsight.howToImprove}
                </span>
              </div>
            )}
          </div>
        )}

        {/* 3. HERO FEATURE: ANSWER COACH */}
        {report.coachedAnswers && report.coachedAnswers.length > 0 && (
          <AnswerCoach coachedAnswers={report.coachedAnswers} />
        )}

        {/* 6. MISCONCEPTION REPORT */}
        {report.misconceptionInsights && report.misconceptionInsights.length > 0 && (
          <MisconceptionReportCard insights={report.misconceptionInsights} />
        )}

        {/* 7. YOUR GROWTH / MEMORY SECTION */}
        <div className="space-y-4">
          {report.isFirstTimeCandidate ? (
            <div className="p-6 rounded-3xl glass-panel border border-slate-800 text-left space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-indigo-400">
                <Flame className="w-4 h-4 text-indigo-400" />
                <span>YOUR GROWTH</span>
              </div>
              <div className="text-sm font-semibold text-white">Baseline established</div>
              <p className="text-xs text-slate-400">
                This is your initial candidate assessment. SkillProof will track your longitudinal growth and skill progressions in future interviews.
              </p>
            </div>
          ) : (
            <GrowthProgressCard
              growthSummary={report.growthSummary}
              whatChangedSinceLastInterview={report.whatChangedSinceLastInterview}
            />
          )}
        </div>

        {/* 8. PERSISTENT GAP SECTION */}
        {report.persistentGapInsights && report.persistentGapInsights.length > 0 && (
          <div className="p-6 rounded-3xl glass-panel border border-amber-500/30 text-left space-y-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-amber-300 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              WORTH FOCUSING ON
            </h3>
            {report.persistentGapInsights.map((gap, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2 text-xs">
                <div className="font-semibold text-white">{gap.topic}</div>
                <p className="text-slate-300">{gap.whyItMatters}</p>
                <div className="text-amber-300 font-medium">What to practice: {gap.whatToPractice}</div>
                <div className="text-indigo-300 font-mono text-[11px]">Suggested Challenge: {gap.suggestedNextChallenge}</div>
              </div>
            ))}
          </div>
        )}

        {/* 9. ACTION PLAN — YOUR NEXT 3 STEPS */}
        <ActionPlanCard actionPlan={report.actionPlan} />

        {/* Curriculum Topic Assessment Map */}
        <div className="space-y-4 text-left">
          <h3 className="text-xs sm:text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
            Curriculum Topic Assessment Map
          </h3>
          <TopicEvidenceMap expanders={report.topicEvidenceExpanders} />
        </div>

        {/* Detailed Evidence Expanders */}
        <div className="space-y-3 text-left">
          <h3 className="text-xs sm:text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <HelpCircle className="w-4 h-4 text-indigo-400" />
            Detailed Evidence Expanders (Click to inspect source questions)
          </h3>
          <div className="space-y-2">
            {report.topicEvidenceExpanders.map((expander) => (
              <EvidenceExpander
                key={expander.topic_id}
                topicName={expander.topic_name}
                score={expander.score}
                confidence={expander.confidence}
                evidenceCount={expander.evidenceCount}
                sourceQuestions={expander.sourceQuestions}
                evidenceQuotes={expander.evidenceQuotes}
                statusTag={expander.statusTag}
              />
            ))}
          </div>
        </div>
      </section>

      <footer className="w-full max-w-4xl py-6 border-t border-slate-800/80 text-center text-xs text-slate-500">
        SkillProof Discovery Report — Know it. Show it. Prove it.
      </footer>
    </main>
  );
}
