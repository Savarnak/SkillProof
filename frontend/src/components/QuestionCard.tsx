"use client";

import { Cpu, Layers, Sparkles } from "lucide-react";

interface QuestionCardProps {
  questionText: string;
  topicName: string;
  depthLevel: number;
  isScaffolded?: boolean;
}

export default function QuestionCard({
  questionText,
  topicName,
  depthLevel,
  isScaffolded = false,
}: QuestionCardProps) {
  const depthLabels: Record<number, string> = {
    1: "Recognition",
    2: "Understanding",
    3: "Application",
    4: "Engineering Depth",
    5: "System Design",
    6: "Cross-Domain Transfer",
  };

  return (
    <div className="w-full space-y-4 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
            <Cpu className="w-4 h-4" />
          </div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Interviewer
          </span>
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-900/80 border border-slate-800 text-indigo-300">
          <Layers className="w-3.5 h-3.5 text-indigo-400" />
          <span>{depthLabels[depthLevel] || "Understanding"}</span>
        </div>
      </div>

      <div className="p-6 md:p-8 rounded-3xl glass-panel border border-slate-800/80 shadow-xl space-y-4 text-slate-100 leading-relaxed text-base md:text-lg">
        {isScaffolded && (
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-950/40 border border-amber-500/30 text-amber-300 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Reframed Angle</span>
          </div>
        )}

        <p className="font-normal text-slate-100">{questionText}</p>
      </div>
    </div>
  );
}
