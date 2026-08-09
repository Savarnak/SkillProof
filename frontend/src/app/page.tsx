"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, ArrowRight, Layers, FileText, CheckCircle2, RefreshCw, Compass, Play, BookOpen } from "lucide-react";
import CategorySelector from "../components/CategorySelector";
import JobDescriptionInput from "../components/JobDescriptionInput";
import OrientationModal from "../components/OrientationModal";
import { startInterview } from "../lib/api";

export default function Home() {
  const router = useRouter();

  // Mode: "topics" | "jd"
  const [activeTab, setActiveTab] = useState<"topics" | "jd">("topics");

  // Selection states
  const [selectedTopics, setSelectedTopics] = useState<string[]>(["Operating Systems", "DBMS", "Spring Boot", "Core Java"]);
  const [selectedRole, setSelectedRole] = useState<string | null>("Backend Developer");
  const [jobDescription, setJobDescription] = useState<string>("");

  const [showOrientation, setShowOrientation] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Recent session state
  const [recentSession, setRecentSession] = useState<{ id: string; role: string; topics: string[] } | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem("skillproof_last_session");
    if (saved) {
      try {
        setRecentSession(JSON.parse(saved));
      } catch (e) {
        // ignore
      }
    }
  }, []);

  const handleToggleTopic = (topic: string) => {
    if (selectedTopics.includes(topic)) {
      setSelectedTopics(selectedTopics.filter((t) => t !== topic));
    } else {
      setSelectedTopics([...selectedTopics, topic]);
    }
  };

  const handleStartRequest = () => {
    if (activeTab === "topics" && selectedTopics.length === 0 && !selectedRole) {
      setError("Choose at least one area or role you'd like to explore.");
      return;
    }
    if (activeTab === "jd" && jobDescription.trim().length < 20) {
      setError("Please paste a valid job description before starting.");
      return;
    }
    setError(null);
    setShowOrientation(true);
  };

  const executeStartInterview = async () => {
    try {
      setIsStarting(true);
      const res = await startInterview({
        selectedTopics: activeTab === "topics" ? selectedTopics : [],
        selectedCategories: activeTab === "topics" ? ["custom_topics"] : [],
        targetRole: selectedRole || undefined,
        jobDescription: activeTab === "jd" ? jobDescription : undefined,
        mode: activeTab === "jd" ? "job_description" : "learning_journey",
      });

      // Save to recent session
      const lastSession = {
        id: res.state.interviewId,
        role: selectedRole || "Software Engineer",
        topics: selectedTopics,
      };
      localStorage.setItem("skillproof_last_session", JSON.stringify(lastSession));

      router.push(`/interview/${res.state.interviewId}`);
    } catch (err: any) {
      setError(err.message || "Failed to start interview session.");
      setIsStarting(false);
      setShowOrientation(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-between p-6 md:p-12 bg-gradient-to-b from-[#0b0f19] via-[#0f172a] to-[#0b0f19] text-slate-100">
      {/* Header */}
      <header className="w-full max-w-4xl flex items-center justify-between py-4 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-400">
            <Compass className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">SkillProof</h1>
            <p className="text-xs text-slate-400">Adaptive AI Technical Interviewer</p>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium glass-panel border border-slate-700/50">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span className="text-slate-300">Build the interviewer, not the interview.</span>
        </div>
      </header>

      {/* Hero Section */}
      <section className="w-full max-w-4xl my-8 text-center space-y-6">
        {recentSession && (
          <div className="p-4 rounded-2xl bg-indigo-950/40 border border-indigo-500/30 max-w-xl mx-auto flex items-center justify-between gap-4 text-xs text-left animate-fadeIn">
            <div>
              <span className="text-[10px] font-semibold text-indigo-400 uppercase tracking-wider">Continue where you left off</span>
              <div className="font-semibold text-white">{recentSession.role}</div>
              <div className="text-slate-400 truncate max-w-xs">{recentSession.topics.join(" · ")}</div>
            </div>
            <button
              onClick={() => router.push(`/interview/${recentSession.id}`)}
              className="px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold flex items-center gap-1.5 whitespace-nowrap shadow-md shadow-indigo-600/20"
            >
              <span>Resume</span>
              <Play className="w-3.5 h-3.5 fill-white" />
            </button>
          </div>
        )}

        <div className="space-y-3">
          <span className="inline-block text-xs font-semibold uppercase tracking-wider text-indigo-400 px-3 py-1 rounded-full bg-indigo-950/60 border border-indigo-500/30">
            Adaptive AI Interview Experience
          </span>
          <h2 className="text-3xl md:text-5xl font-extrabold text-white tracking-tight leading-tight">
            What do you want to be challenged on?
          </h2>
          <p className="text-slate-400 text-sm md:text-base max-w-2xl mx-auto">
            Pick your focus areas or paste a job description. SkillProof continuously decides what evidence it needs and adaptively constructs the interview.
          </p>
        </div>

        {/* Setup Mode Tabs */}
        <div className="flex items-center justify-center gap-3 p-1.5 rounded-2xl glass-panel border border-slate-800 max-w-md mx-auto">
          <button
            onClick={() => setActiveTab("topics")}
            className={`flex-1 py-2.5 px-4 rounded-xl text-xs font-semibold transition-all flex items-center justify-center gap-2 ${
              activeTab === "topics"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/25"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Choose Topics & Role</span>
          </button>

          <button
            onClick={() => setActiveTab("jd")}
            className={`flex-1 py-2.5 px-4 rounded-xl text-xs font-semibold transition-all flex items-center justify-center gap-2 ${
              activeTab === "jd"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/25"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Paste Job Description</span>
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === "topics" ? (
          <CategorySelector
            selectedTopics={selectedTopics}
            onToggleTopic={handleToggleTopic}
            selectedRole={selectedRole}
            onSelectRole={setSelectedRole}
          />
        ) : (
          <JobDescriptionInput
            jobDescription={jobDescription}
            onChange={setJobDescription}
          />
        )}

        {/* Error message */}
        {error && (
          <div className="p-3.5 rounded-2xl bg-rose-950/40 border border-rose-900/50 text-rose-300 text-xs font-medium max-w-lg mx-auto">
            {error}
          </div>
        )}

        {/* Scope Confirmation Box */}
        <div className="p-6 md:p-8 rounded-3xl glass-panel border border-indigo-500/30 max-w-2xl mx-auto space-y-6 text-left">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
            <div>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-indigo-400">Your Interview Scope</span>
              <h3 className="text-xl font-bold text-white">
                {activeTab === "jd" ? "Custom Job Description Interview" : selectedRole || "Software Engineering"}
              </h3>
            </div>
            <div className="text-xs text-slate-400 font-mono">
              Estimated: <strong className="text-indigo-300">8–12 adaptive turns</strong>
            </div>
          </div>

          {activeTab === "topics" ? (
            <div className="space-y-2 text-xs">
              <span className="text-slate-400 font-medium">Selected Focus Areas:</span>
              <div className="flex flex-wrap gap-2">
                {selectedTopics.length > 0 ? (
                  selectedTopics.map((t) => (
                    <span key={t} className="px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-slate-200 font-medium">
                      {t}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-500 italic">No specific topics selected (general technical coverage).</span>
                )}
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-300 leading-relaxed italic">
              Interview Engine will extract requirements directly from your pasted Job Description.
            </p>
          )}

          <button
            onClick={handleStartRequest}
            disabled={isStarting}
            className="w-full py-4 px-6 rounded-2xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-base flex items-center justify-center gap-3 shadow-xl shadow-indigo-600/25 transition-all cursor-pointer"
          >
            {isStarting ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>Building Your Interview Strategy...</span>
              </>
            ) : (
              <>
                <span>Start My Interview</span>
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </div>
      </section>

      {/* Psychological Safety Orientation Modal */}
      <OrientationModal
        isOpen={showOrientation}
        isLoading={isStarting}
        onConfirm={executeStartInterview}
        onClose={() => setShowOrientation(false)}
      />

      <footer className="w-full max-w-4xl py-6 border-t border-slate-800/80 text-center text-xs text-slate-500">
        SkillProof — Build the interviewer, not the interview.
      </footer>
    </main>
  );
}
