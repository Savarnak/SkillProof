"use client";

import { AlertTriangle, CheckCircle2, HelpCircle } from "lucide-react";
import { MisconceptionInsight } from "../types/interview";

interface MisconceptionReportCardProps {
  insights: MisconceptionInsight[];
}

export default function MisconceptionReportCard({ insights }: MisconceptionReportCardProps) {
  if (!insights || insights.length === 0) return null;

  return (
    <div className="w-full p-6 md:p-8 rounded-3xl bg-amber-950/20 border border-amber-500/30 text-left space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-amber-300 font-bold text-sm uppercase tracking-wider">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          <span>MISCONCEPTION REPORT</span>
        </div>
        <span className="text-xs text-amber-300/80 font-medium">Non-judgmental coaching review</span>
      </div>

      <div className="space-y-4">
        {insights.map((item, idx) => (
          <div key={idx} className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-3 text-xs">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="font-semibold text-slate-300">Topic: {item.topic}</span>
              <span
                className={`px-2.5 py-0.5 rounded-full text-[10px] font-semibold border ${
                  item.status === "Resolved"
                    ? "bg-emerald-950/60 border-emerald-500/40 text-emerald-400"
                    : item.status === "Partially resolved"
                    ? "bg-amber-950/60 border-amber-500/40 text-amber-300"
                    : "bg-rose-950/60 border-rose-500/40 text-rose-300"
                }`}
              >
                STATUS: {item.status.toUpperCase()}
              </span>
            </div>

            <div className="space-y-1">
              <div className="text-[10px] font-semibold text-amber-400 uppercase tracking-wider">
                MISCONCEPTION IDENTIFIED
              </div>
              <p className="text-amber-200 font-medium italic">&ldquo;{item.misconception}&rdquo;</p>
            </div>

            <div className="space-y-1">
              <div className="text-[10px] font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                <span>WHAT&apos;S ACTUALLY TRUE</span>
              </div>
              <p className="text-slate-200 leading-relaxed">{item.whatsActuallyTrue}</p>
            </div>

            {item.howToRememberIt && (
              <div className="p-3 rounded-xl bg-indigo-950/40 border border-indigo-500/30 space-y-1">
                <div className="text-[10px] font-semibold text-indigo-300 uppercase tracking-wider flex items-center gap-1">
                  <HelpCircle className="w-3 h-3 text-indigo-400" />
                  <span>HOW TO REMEMBER IT (Mental Model)</span>
                </div>
                <p className="text-indigo-200 font-medium">{item.howToRememberIt}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
