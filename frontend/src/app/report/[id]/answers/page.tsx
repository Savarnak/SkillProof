"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Award, ArrowLeft, CheckCircle2, Sparkles, BookOpen, Layers, RefreshCw, PlusCircle, MinusCircle } from "lucide-react";
import { getInterviewReport } from "../../../../lib/api";
import { InterviewReport } from "../../../../types/interview";

export default function AnswerRefinementPage() {
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
        setError(err.message || "Failed to load answer refinement data.");
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
          <span className="text-sm font-medium">Preparing Answer Refinements & Delivery Playbook...</span>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-[#0b0f19] text-slate-200 space-y-4">
        <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-900/50 text-rose-300 text-sm">
          {error || "Answer refinement data not found."}
        </div>
        <button
          onClick={() => router.push(`/report/${interviewId}`)}
          className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold"
        >
          Return to Report
        </button>
      </div>
    );
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-between p-6 md:p-12 bg-gradient-to-b from-[#0b0f19] via-[#0f172a] to-[#0b0f19] text-slate-100">
      <header className="w-full max-w-4xl flex items-center justify-between py-4 border-b border-slate-800/80">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push("/")}
            className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-slate-200 transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Home</span>
          </button>
          
          <button
            onClick={() => router.push(`/report/${interviewId}`)}
            className="inline-flex items-center gap-2 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-all"
          >
            <span>Back to Discovery Report</span>
          </button>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium glass-panel border border-slate-700/50">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span className="text-slate-300">Answer Refiner & Coaching</span>
        </div>
      </header>

      <section className="w-full max-w-4xl my-8 space-y-8 text-left">
        {/* Header */}
        <div className="space-y-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
            POST-INTERVIEW COACHING
          </span>
          <h2 className="text-3xl md:text-5xl font-extrabold text-white tracking-tight">
            Make your answers interview-ready.
          </h2>
          <p className="text-slate-400 text-sm">
            Your underlying technical knowledge was already there. Here is how to structure your answers for maximum clarity without pretending you originally said the AI-generated response.
          </p>
        </div>

        {/* Answer Refinement Cards */}
        <div className="space-y-6">
          {report.refinementDiffs.map((ref: any, idx: number) => (
            <div key={idx} className="p-6 md:p-8 rounded-3xl glass-panel border border-slate-800 space-y-6">
              <div className="space-y-1">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                  Question {ref.questionIndex || idx + 1}
                </span>
                <h3 className="text-base font-semibold text-white">{ref.questionText}</h3>
              </div>

              {/* Before vs After Comparison */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800/80 space-y-2">
                  <div className="font-semibold text-slate-400 uppercase tracking-wider text-[10px]">
                    YOUR ORIGINAL ANSWER
                  </div>
                  <p className="text-slate-300 italic leading-relaxed">&ldquo;{ref.originalAnswer}&rdquo;</p>
                </div>

                <div className="p-4 rounded-2xl bg-indigo-950/40 border border-indigo-500/30 space-y-2">
                  <div className="font-semibold text-indigo-300 uppercase tracking-wider text-[10px] flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-indigo-400" />
                    INTERVIEW-READY VERSION
                  </div>
                  <p className="text-indigo-100 font-medium leading-relaxed">&ldquo;{ref.interviewReadyVersion}&rdquo;</p>
                </div>
              </div>

              {/* What Changed Diff Breakdown */}
              <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-2 text-xs">
                <div className="font-semibold text-slate-300 text-[11px]">What Changed in Structure?</div>
                <div className="flex flex-wrap gap-2">
                  {ref.diffAdditions?.map((add: string, i: number) => (
                    <span key={i} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 text-[11px]">
                      <PlusCircle className="w-3 h-3 text-emerald-400" /> {add}
                    </span>
                  ))}
                  {ref.diffDeletions?.map((del: string, i: number) => (
                    <span key={i} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-rose-950/60 border border-rose-500/30 text-rose-300 text-[11px]">
                      <MinusCircle className="w-3 h-3 text-rose-400" /> {del}
                    </span>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="p-4 rounded-2xl bg-emerald-950/30 border border-emerald-500/20 space-y-1">
                  <div className="font-semibold text-emerald-400 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" /> What You Did Well
                  </div>
                  <p className="text-slate-300">{ref.whatWasGood}</p>
                </div>

                <div className="p-4 rounded-2xl bg-amber-950/30 border border-amber-500/20 space-y-1">
                  <div className="font-semibold text-amber-300 flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5" /> Delivery Coaching Formula
                  </div>
                  <p className="text-slate-300 font-mono font-medium">{ref.deliveryFormula}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Personal Technical Delivery Playbook */}
        <div className="p-6 md:p-8 rounded-3xl bg-gradient-to-br from-indigo-950/80 via-slate-900 to-slate-950 border border-indigo-500/30 space-y-6">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
              <BookOpen className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Your Technical Delivery Playbook</h3>
              <p className="text-xs text-slate-400">Personalized response structure formulas based on observed expression patterns</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            {report.personalPlaybookFormulas.map((item, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
                <div className="font-semibold text-indigo-300">{item.scenario}</div>
                <div className="text-slate-300 font-mono font-medium">{item.formula}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="w-full max-w-4xl py-6 border-t border-slate-800/80 text-center text-xs text-slate-500">
        SkillProof Answer Refiner — Know it. Show it. Prove it.
      </footer>
    </main>
  );
}
