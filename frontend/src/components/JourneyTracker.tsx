"use client";

import { Compass, Sparkles } from "lucide-react";

interface JourneyTrackerProps {
  currentTurn: number;
  minQuestions: number;
  coveredTopicsCount: number;
  currentTopicName: string;
  targetRole?: string | null;
}

export default function JourneyTracker({
  currentTurn,
  minQuestions,
  coveredTopicsCount,
  currentTopicName,
  targetRole,
}: JourneyTrackerProps) {
  const displayTurn = String(currentTurn).padStart(2, "0");
  const displayTotal = String(minQuestions).padStart(2, "0");

  return (
    <div className="w-full glass-panel border-b border-slate-800/80 px-4 py-3">
      <div className="max-w-4xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 font-mono text-indigo-400 font-semibold bg-indigo-950/60 px-3 py-1 rounded-full border border-indigo-500/20">
            <Compass className="w-3.5 h-3.5" />
            <span>Question {displayTurn} / {displayTotal}</span>
          </div>
          <span className="text-slate-300 font-medium truncate max-w-xs md:max-w-md">
            Exploring: <strong className="text-white font-semibold">{currentTopicName}</strong>
          </span>
        </div>

        <div className="flex items-center gap-2">
          {targetRole && (
            <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-slate-900 border border-slate-800 text-slate-300">
              Role: {targetRole}
            </span>
          )}
          <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-indigo-950/60 border border-indigo-500/30 text-indigo-300 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-indigo-400" />
            {coveredTopicsCount} Topics Evaluated
          </span>
        </div>
      </div>
    </div>
  );
}
