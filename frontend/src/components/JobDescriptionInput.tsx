"use client";

import { FileText, Sparkles } from "lucide-react";

interface JobDescriptionInputProps {
  jobDescription: string;
  onChange: (val: string) => void;
}

export default function JobDescriptionInput({
  jobDescription,
  onChange,
}: JobDescriptionInputProps) {
  return (
    <div className="space-y-4 text-left">
      <div className="p-6 rounded-3xl glass-panel border border-slate-800 space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Interview me for a specific job</h3>
            <p className="text-xs text-slate-400">
              Paste a job description and SkillProof will build the interview around the skills, technologies, and requirements it contains.
            </p>
          </div>
        </div>

        <textarea
          value={jobDescription}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Paste the Job Description here (e.g. 'Looking for a Senior Java Developer with Spring Boot, Microservices, SQL, AWS, and Docker experience...')"
          className="w-full h-44 p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all font-mono leading-relaxed resize-none"
        />

        {jobDescription.trim().length > 30 && (
          <div className="p-3.5 rounded-2xl bg-indigo-950/40 border border-indigo-500/30 text-xs text-indigo-300 flex items-center gap-2 animate-fadeIn">
            <Sparkles className="w-4 h-4 text-indigo-400 flex-shrink-0" />
            <span>Job Description detected! SkillProof will extract requirements and track your job readiness.</span>
          </div>
        )}
      </div>
    </div>
  );
}
