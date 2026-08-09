"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, HelpCircle, CheckCircle2 } from "lucide-react";

interface EvidenceExpanderProps {
  topicName: string;
  score: number;
  confidence: number;
  evidenceCount: number;
  sourceQuestions: number[];
  evidenceQuotes: string[];
  statusTag: string;
}

export default function EvidenceExpander({
  topicName,
  score,
  confidence,
  evidenceCount,
  sourceQuestions,
  evidenceQuotes,
  statusTag,
}: EvidenceExpanderProps) {
  const [isOpen, setIsOpen] = useState(false);

  const isNotAssessed = statusTag === "Not Assessed";
  const scorePct = Math.round(score * 100);
  const confidencePct = Math.round(confidence * 100);

  return (
    <div className="w-full rounded-2xl glass-panel border border-slate-800 overflow-hidden transition-all">
      <div
        onClick={() => !isNotAssessed && setIsOpen(!isOpen)}
        className={`p-4 flex items-center justify-between cursor-pointer ${
          isNotAssessed ? "opacity-60 cursor-default" : "hover:bg-slate-900/60"
        }`}
      >
        <div className="flex items-center gap-3">
          <div
            className={`px-2.5 py-1 rounded-full text-[11px] font-semibold uppercase tracking-wider ${
              statusTag === "Strong"
                ? "bg-emerald-950/60 border border-emerald-500/30 text-emerald-400"
                : statusTag === "Demonstrated"
                ? "bg-indigo-950/60 border border-indigo-500/30 text-indigo-300"
                : statusTag === "Developing"
                ? "bg-amber-950/60 border border-amber-500/30 text-amber-300"
                : "bg-slate-900 border border-slate-800 text-slate-400"
            }`}
          >
            {statusTag}
          </div>
          <span className="text-sm font-semibold text-white">{topicName}</span>
        </div>

        <div className="flex items-center gap-4">
          {!isNotAssessed ? (
            <div className="text-right">
              <span className="text-sm font-bold text-indigo-400 font-mono">{scorePct}%</span>
              <span className="text-[10px] text-slate-500 block">Confidence: {confidencePct}%</span>
            </div>
          ) : (
            <span className="text-xs text-slate-500 italic">Not assessed</span>
          )}

          {!isNotAssessed && (
            <button className="p-1 rounded-lg text-slate-400 hover:text-white">
              {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          )}
        </div>
      </div>

      {isOpen && !isNotAssessed && (
        <div className="p-4 bg-slate-950/60 border-t border-slate-800/80 text-xs space-y-3 animate-fadeIn">
          <div className="flex items-center gap-2 font-medium text-slate-300">
            <HelpCircle className="w-3.5 h-3.5 text-indigo-400" />
            <span>Why this score? (Source Questions: {sourceQuestions.map((q) => `Q${q}`).join(", ")})</span>
          </div>

          <ul className="space-y-1.5 text-slate-300 pl-4 list-disc marker:text-indigo-400">
            {evidenceQuotes.length > 0 ? (
              evidenceQuotes.map((quote, idx) => (
                <li key={idx} className="leading-relaxed">{quote}</li>
              ))
            ) : (
              <li className="text-slate-500 italic">Baseline answer evaluated.</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
