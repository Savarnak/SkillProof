"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ShieldCheck, Award, Brain, MessageSquare, Compass, ArrowRight, AlertTriangle, CheckCircle2, RefreshCw, Lightbulb, UserCheck, HelpCircle, ArrowLeft, FileText } from "lucide-react";
import { getInterviewReport } from "../../../lib/api";
import { InterviewReport } from "../../../types/interview";
import EvidenceExpander from "../../../components/EvidenceExpander";
import TopicEvidenceMap from "../../../components/TopicEvidenceMap";

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

  return (
    <main className="min-h-screen flex flex-col items-center justify-between p-6 md:p-12 bg-gradient-to-b from-[#0b0f19] via-[#0f172a] to-[#0b0f19] text-slate-100">
      <header className="w-full max-w-4xl flex items-center justify-between py-4 border-b border-slate-800/80">
        <button
          onClick={() => router.push("/")}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-slate-200 transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </button>

        <button
          onClick={() => router.push(`/report/${interviewId}/answers`)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition-all"
        >
          <span>Answer Refinement & Playbook</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </header>

      <section className="w-full max-w-4xl my-8 space-y-8">
        {/* Header Title */}
        <div className="space-y-2 text-left">
          <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
            YOUR TECHNICAL SNAPSHOT
          </span>
          <h2 className="text-3xl md:text-5xl font-extrabold text-white tracking-tight">
            Here&apos;s what you demonstrated, {report.candidateName}.
          </h2>
          <p className="text-slate-400 text-sm">
            Evaluated across {report.totalQuestionsAsked} questions covering {report.uniqueDaysCovered} topics.
          </p>
        </div>

        {/* Job Readiness Matrix if in JD Mode */}
        {report.jdRequirementCoverage && report.jdRequirementCoverage.length > 0 && (
          <div className="p-6 md:p-8 rounded-3xl glass-panel border border-indigo-500/30 text-left space-y-4">
            <h3 className="text-sm font-semibold text-indigo-300 flex items-center gap-2">
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

        {/* Overall Readiness & Weighted Score Matrix */}
        <div className="p-6 md:p-8 rounded-3xl glass-panel border border-slate-800 space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4 text-left">
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Overall Readiness Score</span>
              <div className="text-4xl md:text-6xl font-extrabold text-indigo-400 font-mono mt-1">
                {scores.overallReadiness} <span className="text-xl text-slate-500 font-normal">/ 100</span>
              </div>
            </div>
            <p className="text-xs text-slate-400 max-w-sm leading-relaxed">
              Transparent weighted calculation: Knowledge (30%), Reasoning (20%), Application (20%), Expression (15%), Transfer (15%).
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-left">
            <div className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-1">
              <div className="text-[11px] text-slate-400 font-medium">Knowledge (30%)</div>
              <div className="text-lg font-bold text-white font-mono">{Math.round(scores.technicalKnowledge * 100)}%</div>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-1">
              <div className="text-[11px] text-slate-400 font-medium">Application (20%)</div>
              <div className="text-lg font-bold text-white font-mono">{Math.round(scores.application * 100)}%</div>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-1">
              <div className="text-[11px] text-slate-400 font-medium">Expression (15%)</div>
              <div className="text-lg font-bold text-white font-mono">{Math.round(scores.expression * 100)}%</div>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-1">
              <div className="text-[11px] text-slate-400 font-medium">Transfer (15%)</div>
              <div className="text-lg font-bold text-white font-mono">{Math.round(scores.transfer * 100)}%</div>
            </div>
          </div>
        </div>

        {/* "You Know More Than You Showed" Insight Card */}
        {report.showKnowledgeVsExpressionInsight && (
          <div className="p-6 md:p-8 rounded-3xl bg-gradient-to-br from-indigo-950/80 via-slate-900 to-slate-950 border border-indigo-500/30 space-y-3 text-left animate-fadeIn">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-semibold">
              <Brain className="w-3.5 h-3.5 text-indigo-400" />
              <span>Assessment Insight</span>
            </div>
            <h3 className="text-xl md:text-2xl font-bold text-white">You knew more than your first answer showed.</h3>
            <p className="text-slate-300 text-sm leading-relaxed">
              {report.insightMessage}
            </p>
          </div>
        )}

        {/* Topic Evidence Map */}
        <div className="space-y-4 text-left">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
            Curriculum Topic Assessment Map
          </h3>
          <TopicEvidenceMap expanders={report.topicEvidenceExpanders} />
        </div>

        {/* Collapsible Evidence Expanders ("Why?") */}
        <div className="space-y-3 text-left">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
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

        {/* Candidate Profile Hypothesis vs Live Interview Evidence Verification */}
        {report.profileDivergenceNotes.length > 0 && (
          <div className="p-6 md:p-8 rounded-3xl glass-panel border border-indigo-500/30 text-left space-y-4">
            <h3 className="text-sm font-semibold text-indigo-300 flex items-center gap-2">
              <UserCheck className="w-4 h-4 text-indigo-400" />
              Profile Signal vs Live Evidence Divergence
            </h3>
            <div className="space-y-2 text-xs">
              {report.profileDivergenceNotes.map((note, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-300">
                  {note}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Demonstrated Strengths & Next Frontier */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
          <div className="p-6 rounded-3xl glass-panel border border-slate-800 space-y-4">
            <h3 className="text-sm font-semibold text-emerald-400 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              Demonstrated Strengths
            </h3>
            <ul className="space-y-2 text-xs text-slate-300">
              {report.demonstratedStrengths.map((str: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span>{str}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-6 rounded-3xl glass-panel border border-slate-800 space-y-4">
            <h3 className="text-sm font-semibold text-indigo-400 flex items-center gap-2">
              <Lightbulb className="w-4 h-4" />
              Your Next Frontier
            </h3>
            <ul className="space-y-2 text-xs text-slate-300">
              {report.knowledgeGaps.length > 0 ? (
                report.knowledgeGaps.map((gap: string, idx: number) => (
                  <li key={idx} className="flex items-start gap-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80">
                    <span className="text-indigo-400 font-bold">•</span>
                    <span>The interview did not provide sufficient evidence of {gap}</span>
                  </li>
                ))
              ) : (
                <li className="text-slate-400 italic">No critical conceptual gaps flagged. Continue practicing system design scaling.</li>
              )}
            </ul>
          </div>
        </div>

        {/* Misconception Tracker Card */}
        {report.misconceptionsFound.length > 0 && (
          <div className="p-6 md:p-8 rounded-3xl bg-amber-950/20 border border-amber-500/30 text-left space-y-4">
            <h3 className="text-sm font-semibold text-amber-300 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              Concept Worth Revisiting
            </h3>
            {report.misconceptionsFound.map((misc: any, idx: number) => (
              <div key={idx} className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2 text-xs">
                <div className="text-slate-400">Topic: <strong className="text-slate-200">{misc.topic}</strong></div>
                <div className="text-amber-200 font-medium">&ldquo;{misc.misconception}&rdquo;</div>
                <div className="text-emerald-400 font-semibold">
                  Status: {misc.status.toUpperCase()} (Challenged and probed during interview)
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Cross-Domain Transfer Result */}
        <div className="p-6 rounded-3xl glass-panel border border-slate-800 text-left space-y-3">
          <h3 className="text-sm font-semibold text-indigo-300 flex items-center gap-2">
            <Compass className="w-4 h-4 text-indigo-400" />
            Cross-Domain Concept Transfer
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed">{report.transferAbility}</p>
        </div>

        {/* Bottom CTA to Answer Refinement Page */}
        <div className="pt-4 text-center">
          <button
            onClick={() => router.push(`/report/${interviewId}/answers`)}
            className="w-full md:w-auto py-4 px-8 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-base inline-flex items-center justify-center gap-3 shadow-xl shadow-indigo-600/25 transition-all"
          >
            <span>Explore Answer Refinement & Coaching</span>
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </section>

      <footer className="w-full max-w-4xl py-6 border-t border-slate-800/80 text-center text-xs text-slate-500">
        SkillProof Discovery Report — Know it. Show it. Prove it.
      </footer>
    </main>
  );
}
