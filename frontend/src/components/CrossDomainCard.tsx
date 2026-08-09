"use client";

import { Compass, Sparkles, ArrowUpRight } from "lucide-react";

interface CrossDomainCardProps {
  domainName: string;
  topicName: string;
}

export default function CrossDomainCard({ domainName, topicName }: CrossDomainCardProps) {
  return (
    <div className="w-full p-6 md:p-8 rounded-3xl bg-gradient-to-br from-indigo-950/80 via-slate-900 to-slate-950 border border-indigo-500/30 shadow-2xl space-y-4 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>Cross-Domain Transfer Challenge</span>
        </div>
        <span className="text-xs font-mono text-slate-400">Level 6 Transfer</span>
      </div>

      <div className="space-y-2">
        <h3 className="text-xl md:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <span>Let&apos;s change the context.</span>
        </h3>
        <p className="text-slate-300 text-sm md:text-base leading-relaxed">
          You&apos;ve demonstrated a solid understanding of <strong className="text-indigo-300">{topicName}</strong>. Now let&apos;s see whether you can carry that reasoning into an unfamiliar real-world scenario:
        </p>
      </div>

      <div className="p-4 rounded-2xl bg-indigo-950/40 border border-indigo-500/20 text-xs md:text-sm text-indigo-200 font-medium flex items-center justify-between">
        <span>Target Scenario: <strong>{domainName}</strong></span>
        <ArrowUpRight className="w-4 h-4 text-indigo-400 shrink-0" />
      </div>
    </div>
  );
}
