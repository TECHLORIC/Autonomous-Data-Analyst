'use client';

import React, { useState } from 'react';

interface ChatInterfaceProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const SUGGESTIONS = [
  '🏆 Breakdown by top revenue drivers',
  '📈 Show month-over-month trends',
  '⚠️ Detect statistical anomalies & outliers',
  '📊 Compare category performance metrics',
];

export default function ChatInterface({ onSendMessage, isLoading }: ChatInterfaceProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleSelectSuggestion = (suggestion: string) => {
    if (!isLoading) {
      // strip icon
      const clean = suggestion.replace(/^[^\w]+/, '').trim();
      onSendMessage(clean);
    }
  };

  return (
    <div className="w-full space-y-3">
      {/* Suggestions Strip */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 no-print">
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider whitespace-nowrap">
          Quick Prompts:
        </span>
        {SUGGESTIONS.map((s, i) => (
          <button
            key={i}
            type="button"
            disabled={isLoading}
            onClick={() => handleSelectSuggestion(s)}
            className="text-xs font-medium text-slate-600 hover:text-blue-600 bg-white hover:bg-blue-50/70 border border-slate-200/90 hover:border-blue-200 px-3 py-1.5 rounded-xl whitespace-nowrap transition-all shadow-2xs disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {s}
          </button>
        ))}
      </div>

      {/* Main Input Form */}
      <form onSubmit={handleSubmit} className="relative w-full">
        <div className="relative flex items-center">
          <div className="absolute left-4.5 text-slate-400 pointer-events-none">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>

          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            placeholder="Ask anything about your data... (e.g. 'What are the top 5 revenue drivers and their growth rates?')"
            className="w-full pl-12 pr-36 py-4 rounded-2xl bg-white border border-slate-200/90 shadow-sm focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none text-slate-800 placeholder-slate-400 text-sm md:text-base font-normal transition-all disabled:bg-slate-50 disabled:cursor-not-allowed"
          />

          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold text-sm rounded-xl shadow-sm hover:shadow transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5"
          >
            {isLoading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <span>Generate BI</span>
                <span className="text-xs opacity-75 font-mono">↵</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
