"use client";

import { Target, CheckCircle2, ArrowRight } from "lucide-react";
import { ActionPlan } from "../types/interview";

interface ActionPlanCardProps {
  actionPlan?: ActionPlan;
}

export default function ActionPlanCard({ actionPlan }: ActionPlanCardProps) {
  const steps = actionPlan?.nextSteps || [
    "Practice explaining your core technical concept in under 60 seconds using the Definition -> Mechanism -> Trade-off formula.",
    "Build a small hybrid retrieval pipeline combining BM25 keyword search with vector embeddings.",
    "Revisit failure modes, boundary edge cases, and quantitative performance trade-offs under high load."
  ];

  return (
    <div className="w-full p-6 md:p-8 rounded-3xl bg-gradient-to-br from-indigo-950/80 via-slate-900 to-slate-950 border border-indigo-500/30 text-left space-y-4 shadow-xl">
      <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm uppercase tracking-wider">
        <Target className="w-5 h-5 text-indigo-400" />
        <span>YOUR NEXT 3 STEPS</span>
      </div>

      <p className="text-slate-300 text-xs leading-relaxed">
        Evidence-backed recommendations to maximize your interview readiness for your next challenge:
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs pt-2">
        {steps.slice(0, 3).map((step, idx) => (
          <div
            key={idx}
            className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-3 flex flex-col justify-between hover:border-indigo-500/40 transition-colors"
          >
            <div className="space-y-2">
              <div className="w-7 h-7 rounded-xl bg-indigo-600/30 border border-indigo-500/40 text-indigo-300 flex items-center justify-center font-mono font-bold text-xs">
                {idx + 1}
              </div>
              <p className="text-slate-200 font-medium leading-relaxed">{step}</p>
            </div>

            <div className="flex items-center gap-1 text-[11px] font-semibold text-indigo-400 pt-2 border-t border-slate-800/60">
              <span>Suggested Focus</span>
              <ArrowRight className="w-3 h-3 text-indigo-400" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
