"use client";

import { TrendingUp, ArrowUpRight, Sparkles, CheckCircle2, History, Award } from "lucide-react";
import { GrowthItem, ProgressChangeItem } from "../types/interview";

interface GrowthProgressCardProps {
  growthSummary?: GrowthItem[];
  whatChangedSinceLastInterview?: ProgressChangeItem[];
}

export default function GrowthProgressCard({
  growthSummary = [],
  whatChangedSinceLastInterview = [],
}: GrowthProgressCardProps) {
  const hasGrowth = growthSummary.length > 0 || whatChangedSinceLastInterview.length > 0;

  if (!hasGrowth) {
    return (
      <div className="p-6 rounded-3xl glass-panel border border-slate-800 text-left space-y-3">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          <History className="w-4 h-4 text-indigo-400" />
          <span>Longitudinal Progress</span>
        </div>
        <p className="text-slate-300 text-sm">
          This is your baseline interview. Future sessions will track demonstrated growth, resolved misconceptions, and progress across interviews.
        </p>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 rounded-3xl bg-gradient-to-br from-indigo-950/40 via-slate-900 to-slate-950 border border-indigo-500/30 text-left space-y-6 shadow-2xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">Longitudinal Candidate Growth</span>
            <h2 className="text-xl font-bold text-white tracking-tight">Your Progress & Improvement</h2>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 w-fit">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Growth Detected Across Sessions</span>
        </div>
      </div>

      {/* What Changed Since Last Interview */}
      {whatChangedSinceLastInterview.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <History className="w-4 h-4 text-indigo-400" />
            What changed since your last interview
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {whatChangedSinceLastInterview.map((item, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between gap-3">
                <div>
                  <div className="font-semibold text-white text-sm">{item.topic}</div>
                  <div className="text-xs text-slate-400 flex items-center gap-2 mt-1">
                    <span>{item.previousStatus}</span>
                    <ArrowUpRight className="w-3.5 h-3.5 text-indigo-400" />
                    <span className="text-indigo-300 font-medium">{item.currentStatus}</span>
                  </div>
                </div>

                <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                  item.changeTag === 'Improved'
                    ? 'bg-emerald-950/80 border border-emerald-500/40 text-emerald-300'
                    : 'bg-amber-950/80 border border-amber-500/40 text-amber-300'
                }`}>
                  {item.changeTag}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Growth Breakdown */}
      {growthSummary.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Award className="w-4 h-4 text-emerald-400" />
            Demonstrated Depth Transitions
          </h3>

          <div className="space-y-2">
            {growthSummary.map((growth, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-emerald-950/20 border border-emerald-500/30 text-xs space-y-1.5">
                <div className="flex items-center justify-between font-semibold text-white">
                  <span>{growth.topic}</span>
                  <span className="text-emerald-400 font-mono">
                    Level {growth.previousLevel} &rarr; Level {growth.currentLevel} (+{growth.growthAmount} Depth)
                  </span>
                </div>
                <p className="text-slate-300 leading-relaxed italic">
                  &ldquo;{growth.evidence}&rdquo;
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800 text-xs text-slate-400 flex items-center gap-2">
        <CheckCircle2 className="w-4 h-4 text-indigo-400 shrink-0" />
        <span>SkillProof remembers candidate growth across interviews rather than relying on isolated single-session snapshots.</span>
      </div>
    </div>
  );
}
