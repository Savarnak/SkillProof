"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Check, Cpu, Code, CpuIcon, Layers, UserCheck } from "lucide-react";

export interface CategoryData {
  id: string;
  title: string;
  icon: any;
  items: string[];
}

export const CATEGORIES: CategoryData[] = [
  {
    id: "core_cs",
    title: "Core CS",
    icon: Cpu,
    items: [
      "Operating Systems",
      "Computer Networks",
      "DBMS",
      "Data Structures & Algorithms",
      "Computer Organization & Architecture",
      "Software Engineering",
      "Object-Oriented Programming",
      "Theory of Computation",
      "Compiler Design",
    ],
  },
  {
    id: "frameworks",
    title: "Frameworks & Development",
    icon: Layers,
    items: [
      "Spring Boot",
      "React",
      "Angular",
      "Node.js",
      "Express.js",
      "Django",
      "Flask",
      "Flutter",
      ".NET",
      "Next.js",
    ],
  },
  {
    id: "technical_emerging",
    title: "Technical / Emerging Tech",
    icon: CpuIcon,
    items: [
      "Cloud Computing",
      "AWS",
      "Azure",
      "GCP",
      "Git",
      "GitHub",
      "Docker",
      "Kubernetes",
      "RAG",
      "Vector Databases",
      "LLMs",
      "Generative AI",
      "Agentic AI",
      "MCP",
      "Machine Learning",
      "Data Science",
      "DevOps",
    ],
  },
  {
    id: "languages",
    title: "Programming Languages",
    icon: Code,
    items: [
      "Core Java",
      "Python",
      "C",
      "C++",
      "JavaScript",
      "TypeScript",
      "SQL",
      "Go",
      "C#",
    ],
  },
];

export const TARGET_ROLES: string[] = [
  "Full Stack Developer",
  "Backend Developer",
  "Frontend Developer",
  "Java Developer",
  "Python Developer",
  "Software Engineer",
  "Data Engineer",
  "Data Scientist",
  "ML Engineer",
  "AI Engineer",
  "DevOps Engineer",
  "Cloud Engineer",
  "QA / Test Engineer",
  "Android Developer",
];

interface CategorySelectorProps {
  selectedTopics: string[];
  onToggleTopic: (topic: string) => void;
  selectedRole: string | null;
  onSelectRole: (role: string) => void;
}

export default function CategorySelector({
  selectedTopics,
  onToggleTopic,
  selectedRole,
  onSelectRole,
}: CategorySelectorProps) {
  const [expandedCategory, setExpandedCategory] = useState<string | null>("core_cs");
  const [roleExpanded, setRoleExpanded] = useState(true);

  return (
    <div className="space-y-4 text-left">
      {/* Target Role Accordion */}
      <div className="rounded-2xl glass-panel border border-slate-800 overflow-hidden">
        <button
          onClick={() => setRoleExpanded(!roleExpanded)}
          className="w-full p-4 flex items-center justify-between hover:bg-slate-900/60 transition-all"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
              <UserCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Target Role</h3>
              <p className="text-xs text-slate-400">
                {selectedRole ? `Selected: ${selectedRole}` : "Select your target engineering role"}
              </p>
            </div>
          </div>
          {roleExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
        </button>

        {roleExpanded && (
          <div className="p-4 bg-slate-950/60 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
            {TARGET_ROLES.map((role) => {
              const isSelected = selectedRole === role;
              return (
                <button
                  key={role}
                  onClick={() => onSelectRole(role)}
                  className={`p-2.5 rounded-xl text-xs font-semibold text-left transition-all flex items-center justify-between border ${
                    isSelected
                      ? "bg-indigo-600/20 border-indigo-500 text-indigo-200"
                      : "bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700"
                  }`}
                >
                  <span className="truncate">{role}</span>
                  {isSelected && <Check className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* 4 Category Accordions */}
      {CATEGORIES.map((cat) => {
        const Icon = cat.icon;
        const isExpanded = expandedCategory === cat.id;
        const selectedCount = cat.items.filter((item) => selectedTopics.includes(item)).length;

        return (
          <div key={cat.id} className="rounded-2xl glass-panel border border-slate-800 overflow-hidden">
            <button
              onClick={() => setExpandedCategory(isExpanded ? null : cat.id)}
              className="w-full p-4 flex items-center justify-between hover:bg-slate-900/60 transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">{cat.title}</h3>
                  <p className="text-xs text-slate-400">
                    {selectedCount > 0 ? `${selectedCount} selected` : "Select topics"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {selectedCount > 0 && (
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-950 border border-indigo-500/40 text-indigo-300 font-mono">
                    {selectedCount}
                  </span>
                )}
                {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
              </div>
            </button>

            {isExpanded && (
              <div className="p-4 bg-slate-950/60 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                {cat.items.map((item) => {
                  const isChecked = selectedTopics.includes(item);
                  return (
                    <button
                      key={item}
                      onClick={() => onToggleTopic(item)}
                      className={`p-2.5 rounded-xl text-xs font-semibold text-left transition-all flex items-center justify-between border ${
                        isChecked
                          ? "bg-indigo-600/20 border-indigo-500 text-indigo-200"
                          : "bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700"
                      }`}
                    >
                      <span className="truncate">{item}</span>
                      {isChecked && <Check className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />}
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
