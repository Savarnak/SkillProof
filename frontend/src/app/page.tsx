"use client";

import { useEffect, useState } from "react";
import { Sparkles, ShieldCheck, Cpu, ArrowRight, CheckCircle2, AlertCircle } from "lucide-react";

interface HealthStatus {
  status: string;
  version: string;
  environment: string;
  deterministic_rules: {
    min_required_questions: number;
    min_required_curriculum_days: number;
  };
  sample_data: {
    curriculum_loaded: boolean;
    modules_count: number;
    candidates_loaded: boolean;
    synthetic_candidates_count: number;
  };
}

export default function Home() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${apiUrl}/api/health`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setHealth(data);
      } catch (err: any) {
        setError(err.message || "Failed to connect to SkillProof engine backend");
      } finally {
        setLoading(false);
      }
    };

    fetchHealth();
  }, []);

  return (
    <main className="min-h-screen flex flex-col items-center justify-between p-6 md:p-12 bg-gradient-to-b from-[#0b0f19] via-[#0f172a] to-[#0b0f19]">
      <header className="w-full max-w-5xl flex items-center justify-between py-4 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-400">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">SkillProof</h1>
            <p className="text-xs text-slate-400">Adaptive AI Technical Interviewer</p>
          </div>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium glass-panel border border-slate-700/50">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-slate-300">Phase 1 Foundation</span>
        </div>
      </header>

      {/* Hero Section */}
      <section className="w-full max-w-4xl text-center my-12 space-y-6">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-950/60 border border-indigo-500/30 text-indigo-300 text-sm font-medium">
          <Sparkles className="w-4 h-4 text-indigo-400" />
          <span>Know it. Show it. Prove it.</span>
        </div>

        <h2 className="text-4xl md:text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white via-indigo-100 to-indigo-300 tracking-tight">
          Build the interviewer, not the interview.
        </h2>

        <p className="text-lg md:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
          An adaptive AI technical interviewer that continuously measures candidate depth, provides scaffolding during difficulties, and probes misconceptions without rigid exam pressure.
        </p>

        {/* Backend Health Diagnostics */}
        <div className="mt-8 p-6 rounded-2xl glass-panel text-left border border-slate-800 space-y-4 max-w-2xl mx-auto">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="font-semibold text-sm text-slate-200 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
              Engine Health & Deterministic Rules
            </h3>
            <span className="text-xs font-mono text-slate-400">GET /api/health</span>
          </div>

          {loading && (
            <div className="text-sm text-slate-400 animate-pulse">
              Connecting to FastAPI backend (localhost:8000)...
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 text-sm text-rose-400 bg-rose-950/40 p-3 rounded-lg border border-rose-900/50">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>Backend Connection Pending: {error}. Ensure `uvicorn app.main:app` is running on port 8000.</span>
            </div>
          )}

          {health && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800/80 space-y-1">
                <div className="text-slate-400 font-medium">Deterministic Engine Rules</div>
                <div className="text-emerald-400 font-mono font-semibold flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Min {health.deterministic_rules.min_required_questions} Questions
                </div>
                <div className="text-emerald-400 font-mono font-semibold flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Min {health.deterministic_rules.min_required_curriculum_days} Curriculum Days
                </div>
              </div>

              <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800/80 space-y-1">
                <div className="text-slate-400 font-medium">Synthetic Demo Datasets</div>
                <div className="text-indigo-300 font-mono">
                  Curriculum: {health.sample_data.modules_count} Modules Loaded
                </div>
                <div className="text-indigo-300 font-mono">
                  Synthetic Candidates: {health.sample_data.synthetic_candidates_count} Profiles
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      <footer className="w-full max-w-5xl py-6 border-t border-slate-800/80 text-center text-xs text-slate-500">
        SkillProof Hackathon Project — Phase 1 Verification Ready
      </footer>
    </main>
  );
}
