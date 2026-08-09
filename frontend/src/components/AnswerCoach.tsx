"use client";

import { useState } from "react";
import { Sparkles, CheckCircle2, ChevronDown, ChevronUp, Layers, HelpCircle, AlertCircle } from "lucide-react";
import { CoachedAnswer } from "../types/interview";

interface AnswerCoachProps {
  coachedAnswers: CoachedAnswer[];
}

export default function AnswerCoach({ coachedAnswers }: AnswerCoachProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);

  if (!coachedAnswers || coachedAnswers.length === 0) return null;

  return (
    <div className="w-full space-y-4 text-left">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            HERO FEATURE — ANSWER COACH
          </span>
          <h3 className="text-xl md:text-2xl font-extrabold text-white">
            Make your answers interview-ready.
          </h3>
        </div>
      </div>

      <div className="space-y-4">
        {coachedAnswers.map((ca, idx) => {
          const isExpanded = expandedIndex === idx;

          return (
            <div
              key={idx}
              className="rounded-3xl glass-panel border border-slate-800 overflow-hidden transition-all duration-200"
            >
              {/* Card Header (Collapsible toggle) */}
              <button
                onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                className="w-full p-5 md:p-6 flex items-start justify-between gap-4 text-left hover:bg-slate-900/40 transition-colors"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-[11px] font-semibold border border-indigo-500/30">
                      Question {ca.questionIndex || idx + 1}
                    </span>
                    <span className="px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 text-[11px] font-medium font-mono">
                      {ca.deliveryFormulaName}
                    </span>
                  </div>
                  <h4 className="text-sm md:text-base font-semibold text-white leading-snug">
                    {ca.questionText}
                  </h4>
                </div>

                <div className="p-2 rounded-xl bg-slate-800/80 text-slate-400 shrink-0 mt-1">
                  {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </div>
              </button>

              {/* Card Content */}
              {isExpanded && (
                <div className="p-5 md:p-6 pt-0 space-y-6 border-t border-slate-800/60 animate-fadeIn">
                  {/* Delivery Formula Steps */}
                  {ca.deliveryFormulaSteps && ca.deliveryFormulaSteps.length > 0 && (
                    <div className="p-4 rounded-2xl bg-indigo-950/30 border border-indigo-500/20 space-y-2">
                      <div className="text-[11px] font-semibold uppercase tracking-wider text-indigo-300 flex items-center gap-1.5">
                        <Layers className="w-3.5 h-3.5 text-indigo-400" />
                        <span>Delivery Formula ({ca.deliveryFormulaName})</span>
                      </div>
                      <div className="flex flex-wrap gap-2 text-xs">
                        {ca.deliveryFormulaSteps.map((step, sIdx) => (
                          <span
                            key={sIdx}
                            className="px-3 py-1 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 font-mono text-[11px]"
                          >
                            {step}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Side by Side: Original Answer vs Polished Answer */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    {/* YOUR ANSWER */}
                    <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800/80 space-y-2">
                      <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                        YOUR ANSWER
                      </div>
                      <p className="text-slate-300 italic leading-relaxed">
                        &ldquo;{ca.originalAnswer}&rdquo;
                      </p>
                    </div>

                    {/* INTERVIEW-READY VERSION */}
                    <div className="p-4 rounded-2xl bg-gradient-to-br from-indigo-950/60 to-slate-900 border border-indigo-500/40 space-y-2 shadow-lg shadow-indigo-950/20">
                      <div className="text-[10px] font-semibold text-indigo-300 uppercase tracking-wider flex items-center gap-1">
                        <Sparkles className="w-3 h-3 text-indigo-400" />
                        <span>INTERVIEW-READY VERSION (Preserves Your Knowledge)</span>
                      </div>
                      <p className="text-indigo-100 font-medium leading-relaxed">
                        &ldquo;{ca.interviewReadyVersion}&rdquo;
                      </p>
                    </div>
                  </div>

                  {/* Strengths & What Held It Back */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    {/* WHAT YOU DID WELL */}
                    <div className="p-4 rounded-2xl bg-emerald-950/30 border border-emerald-500/20 space-y-2">
                      <div className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>WHAT YOU DID WELL</span>
                      </div>
                      <ul className="space-y-1 text-slate-300">
                        {ca.strengths && ca.strengths.length > 0 ? (
                          ca.strengths.map((str, sIdx) => (
                            <li key={sIdx} className="flex items-start gap-1.5">
                              <span className="text-emerald-400 font-bold">•</span>
                              <span>{str}</span>
                            </li>
                          ))
                        ) : (
                          <li className="italic text-slate-400">Demonstrated initial conceptual attempt.</li>
                        )}
                      </ul>
                    </div>

                    {/* WHAT HELD IT BACK */}
                    <div className="p-4 rounded-2xl bg-amber-950/30 border border-amber-500/20 space-y-2">
                      <div className="text-[11px] font-semibold text-amber-300 flex items-center gap-1.5">
                        <AlertCircle className="w-4 h-4 text-amber-400" />
                        <span>WHAT HELD IT BACK</span>
                      </div>
                      <p className="text-slate-300 font-medium leading-relaxed">
                        {ca.whatHeldItBack}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
