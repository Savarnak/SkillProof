"use client";

import { useState } from "react";
import { Mic, Send, HelpCircle, RefreshCw } from "lucide-react";

interface AnswerInputProps {
  onSubmitAnswer: (text: string) => void;
  onDontKnow: () => void;
  isLoading: boolean;
}

export default function AnswerInput({
  onSubmitAnswer,
  onDontKnow,
  isLoading,
}: AnswerInputProps) {
  const [answerText, setAnswerText] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!answerText.trim() || isLoading) return;
    onSubmitAnswer(answerText.trim());
    setAnswerText("");
  };

  return (
    <div className="w-full space-y-3">
      <form onSubmit={handleSubmit} className="relative rounded-3xl glass-panel border border-slate-800 focus-within:border-indigo-500/50 shadow-2xl transition-all">
        <textarea
          value={answerText}
          onChange={(e) => setAnswerText(e.target.value)}
          placeholder="Explain it in your own words..."
          disabled={isLoading}
          rows={4}
          className="w-full p-5 md:p-6 bg-transparent text-slate-100 placeholder-slate-500 text-sm md:text-base focus:outline-none resize-none"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />

        <div className="flex items-center justify-between p-3 border-t border-slate-800/80 bg-slate-950/40 rounded-b-3xl">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onDontKnow}
              disabled={isLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 text-xs font-medium transition-all"
            >
              <HelpCircle className="w-3.5 h-3.5 text-amber-400" />
              <span>I don&apos;t know yet</span>
            </button>

            <button
              type="button"
              title="Voice mode placeholder"
              onClick={() => alert("Voice input pipeline placeholder. Text mode is active.")}
              className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-indigo-300 text-xs transition-all"
            >
              <Mic className="w-4 h-4" />
            </button>
          </div>

          <button
            type="submit"
            disabled={!answerText.trim() || isLoading}
            className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-xs md:text-sm transition-all ${
              answerText.trim() && !isLoading
                ? "bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20"
                : "bg-slate-800 text-slate-500 cursor-not-allowed"
            }`}
          >
            <span>{isLoading ? "Analyzing..." : "Send Answer"}</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </form>
    </div>
  );
}
