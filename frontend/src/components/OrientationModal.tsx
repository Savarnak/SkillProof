"use client";

import { ShieldCheck, Heart, ArrowRight, RefreshCw } from "lucide-react";

interface OrientationModalProps {
  candidateName?: string;
  onProceed?: () => void;
  isOpen?: boolean;
  onConfirm?: () => void;
  onClose?: () => void;
  isLoading?: boolean;
}

export default function OrientationModal({
  candidateName = "Candidate",
  onProceed,
  isOpen = true,
  onConfirm,
  onClose,
  isLoading = false,
}: OrientationModalProps) {
  if (!isOpen) return null;

  const handleAction = () => {
    if (isLoading) return;
    if (onConfirm) onConfirm();
    else if (onProceed) onProceed();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="w-full max-w-xl p-8 rounded-3xl glass-panel border border-indigo-500/20 shadow-2xl space-y-6 text-left relative">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
            <ShieldCheck className="w-7 h-7" />
          </div>
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">Personalized Orientation</span>
            <h2 className="text-2xl font-bold text-white tracking-tight">Welcome, {candidateName}</h2>
          </div>
        </div>

        <p className="text-slate-300 text-sm leading-relaxed">
          SkillProof will explore your chosen technical topics and discover how deeply you can reason and apply them.
        </p>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Heart className="w-4 h-4 text-rose-400" />
            This isn’t a test designed to catch you out.
          </h3>
          <ul className="text-xs text-slate-300 space-y-2 pl-6 list-disc marker:text-indigo-400">
            <li>There are <strong>no trick questions</strong>.</li>
            <li>You can freely say <strong>&ldquo;I don&apos;t know yet&rdquo;</strong> — we&apos;ll reframe or simplify.</li>
            <li>If you&apos;re stuck, you can ask for another angle.</li>
            <li>The interviewer adapts continuously to how you respond.</li>
          </ul>
        </div>

        <div className="flex items-center gap-3">
          {onClose && (
            <button
              onClick={onClose}
              disabled={isLoading}
              className="py-4 px-5 rounded-2xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 font-semibold text-xs transition-all disabled:opacity-50"
            >
              Cancel
            </button>
          )}

          <button
            onClick={handleAction}
            disabled={isLoading}
            className="flex-1 py-4 px-6 rounded-2xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-base flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/25 transition-all transform active:scale-[0.99] cursor-pointer"
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>Starting Interview...</span>
              </>
            ) : (
              <>
                <span>Ready when you are</span>
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
