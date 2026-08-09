"use client";

import { TopicEvidenceExpander } from "../types/interview";

interface TopicEvidenceMapProps {
  expanders: TopicEvidenceExpander[];
}

export default function TopicEvidenceMap({ expanders }: TopicEvidenceMapProps) {
  const getBadgeStyle = (tag: string) => {
    switch (tag) {
      case "Strong":
        return "bg-emerald-950/60 border-emerald-500/40 text-emerald-400";
      case "Demonstrated":
        return "bg-indigo-950/60 border-indigo-500/40 text-indigo-300";
      case "Developing":
        return "bg-amber-950/60 border-amber-500/40 text-amber-300";
      case "Not Assessed":
        return "bg-slate-900 border-slate-800 text-slate-500";
      default:
        return "bg-slate-900 border-slate-800 text-slate-400";
    }
  };

  return (
    <div className="w-full grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
      {expanders.map((item) => (
        <div
          key={item.topic_id}
          className="p-4 rounded-2xl glass-panel border border-slate-800 space-y-2 text-left"
        >
          <div className="flex items-center justify-between">
            <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${getBadgeStyle(item.statusTag)}`}>
              {item.statusTag}
            </span>
            {item.statusTag !== "Not Assessed" && (
              <span className="text-xs font-mono font-bold text-indigo-400">{Math.round(item.score * 100)}%</span>
            )}
          </div>
          <h4 className="text-xs font-semibold text-white truncate">{item.topic_name}</h4>
        </div>
      ))}
    </div>
  );
}
