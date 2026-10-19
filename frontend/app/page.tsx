import React from 'react';
import FileUpload from './components/FileUpload';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50 flex flex-col items-center">
      {/* Top Navbar */}
      <header className="w-full bg-white/80 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-40 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-sm font-black text-base">
              A
            </div>
            <div>
              <span className="font-bold text-slate-900 tracking-tight text-base block">
                Autonomous Data Analyst
              </span>
              <span className="text-[10px] text-slate-400 font-mono tracking-wider uppercase block">
                Enterprise BI Platform
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Engine Online
            </span>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="w-full max-w-4xl px-4 pt-16 pb-12 text-center">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold mb-6 shadow-2xs">
          <span>✨ Autonomous Multi-Agent Synthesis</span>
          <span className="text-blue-300">•</span>
          <span>Zero Hallucination Guarantee</span>
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-950 tracking-tight leading-[1.15] mb-6">
          Turn Raw Datasets into <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 bg-clip-text text-transparent">
            Executive BI Dashboards
          </span>
        </h1>

        <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed mb-10">
          Upload any CSV, Excel, or JSON dataset. Ask questions in plain English. 
          Our deterministic LangGraph orchestrator writes constrained DuckDB SQL & Python, 
          generating boardroom-ready KPI cards and interactive charts.
        </p>

        {/* Upload Container */}
        <FileUpload />
      </section>

      {/* Feature Highlights Grid */}
      <section className="w-full max-w-6xl px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
            Architecture Highlights
          </h2>
          <p className="text-2xl font-bold text-slate-900 tracking-tight">
            Built for Deterministic Analytical Rigor
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard 
            title="Read-Only DuckDB Engine"
            description="Ultra-fast in-process columnar SQL analysis that executes strict read-only queries with zero SQL injection risks."
            icon="⚡"
            badge="Deterministic"
          />
          <FeatureCard 
            title="Isolated Python Sandbox"
            description="Executes complex statistical modeling, outlier detection (IQR), and correlation analysis inside a secure Docker container."
            icon="🛡️"
            badge="Secure Sandbox"
          />
          <FeatureCard 
            title="Executive BI Synthesis"
            description="Translates raw data aggregations into deterministic KPI cards, variance percentages, and strategic 30/90-day action plans."
            icon="📊"
            badge="Executive Dashboard"
          />
        </div>
      </section>

      {/* Footer */}
      <footer className="w-full border-t border-slate-200/80 py-8 text-center text-xs text-slate-400">
        Autonomous Data Analyst • Production Grade SaaS Architecture
      </footer>
    </main>
  );
}

function FeatureCard({ 
  title, 
  description, 
  icon,
  badge 
}: { 
  title: string; 
  description: string; 
  icon: string;
  badge: string;
}) {
  return (
    <div className="bg-white p-7 rounded-3xl border border-slate-200/90 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-4">
          <span className="text-3xl">{icon}</span>
          <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2.5 py-1 rounded-md border border-blue-100">
            {badge}
          </span>
        </div>
        <h3 className="font-bold text-base text-slate-900 mb-2">{title}</h3>
        <p className="text-slate-600 text-sm leading-relaxed">{description}</p>
      </div>
    </div>
  );
}
