"use client";

import { AlertCircle, ArrowLeft, Play } from "lucide-react";

interface LeaveInterviewModalProps {
  isOpen: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

export default function LeaveInterviewModal({
  isOpen,
  onCancel,
  onConfirm,
}: LeaveInterviewModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="w-full max-w-md p-6 rounded-3xl glass-panel border border-slate-800 space-y-6 text-left shadow-2xl">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-amber-950/60 text-amber-400 border border-amber-500/30">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Leave this interview?</h3>
            <p className="text-xs text-slate-400">Your current turn progress will be saved in your session.</p>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
          <button
            onClick={onCancel}
            className="w-full py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold inline-flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20 transition-all"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>Continue Interview</span>
          </button>
          
          <button
            onClick={onConfirm}
            className="w-full py-3 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-semibold inline-flex items-center justify-center gap-2 transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Home</span>
          </button>
        </div>
      </div>
    </div>
  );
}
