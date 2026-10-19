'use client';

import React, { useState } from 'react';
import { AnalysisResponse, KPICard, PerformanceItem, VisualizationSpec, ExecutionStepResult } from '@/lib/api';
import ChartRenderer from './ChartRenderer';

interface AnalysisResultProps {
  response: AnalysisResponse | null;
  isLoading: boolean;
  error: string | null;
  onAskFollowUp?: (question: string) => void;
}

export default function AnalysisResult({ response, isLoading, error, onAskFollowUp }: AnalysisResultProps) {
  const [activeTab, setActiveTab] = useState<'executive' | 'charts' | 'performance' | 'audit'>('executive');
  const [copiedCodeIndex, setCopiedCodeIndex] = useState<number | null>(null);
  const [copiedJson, setCopiedJson] = useState(false);

  if (isLoading) {
    return (
      <div className="w-full bg-white border border-slate-200/90 rounded-2xl p-12 shadow-sm flex flex-col items-center justify-center text-center">
        <div className="relative mb-6">
          <div className="w-16 h-16 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin" />
          <div className="absolute inset-0 flex items-center justify-center text-blue-600">
            <svg className="w-6 h-6 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
        </div>
        <h3 className="text-xl font-bold text-slate-900 tracking-tight">Autonomous Synthesis in Progress</h3>
        <p className="text-slate-500 text-sm mt-2 max-w-md">
          Executing DuckDB SQL aggregations, sandboxed statistical modeling, and deterministic KPI validation...
        </p>
        <div className="mt-6 flex items-center gap-2 text-xs font-medium text-slate-400 bg-slate-50 px-4 py-2 rounded-full border border-slate-200">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
          LangGraph Orchestrator Active
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full bg-rose-50/70 border border-rose-200 rounded-2xl p-8 text-rose-900 shadow-sm">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-rose-100 rounded-xl text-rose-600">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div>
            <h3 className="font-bold text-lg text-rose-950">Analysis Pipeline Error</h3>
            <p className="text-rose-700 text-sm mt-0.5">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!response) {
    return (
      <div className="w-full bg-white border border-dashed border-slate-300 rounded-2xl p-16 text-center text-slate-500">
        <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <h3 className="text-lg font-bold text-slate-800">Ready for Analysis</h3>
        <p className="text-sm text-slate-500 mt-1 max-w-sm mx-auto">
          Type an analytical question or choose a prompt to generate executive metrics, charts, and recommendations.
        </p>
      </div>
    );
  }

  const { insights, results } = response;
  const {
    metadata,
    executive_summary,
    kpi_cards = [],
    visualizations = [],
    performance_breakdown,
    recommendations,
  } = insights;

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(insights, null, 2));
    setCopiedJson(true);
    setTimeout(() => setCopiedJson(false), 2000);
  };

  const handleCopyCode = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedCodeIndex(index);
    setTimeout(() => setCopiedCodeIndex(null), 2000);
  };

  return (
    <div className="space-y-6 w-full">
      {/* 1. TOP EXECUTIVE HEADER BAR */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-blue-600 mb-1">
            <span className="w-2 h-2 rounded-full bg-blue-600" />
            Executive Synthesis Report
          </div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
            &ldquo;{response.question}&rdquo;
          </h2>
          {metadata && (
            <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-slate-500 font-medium">
              {metadata.dataset_timeframe && (
                <span className="flex items-center gap-1 bg-slate-100 px-2.5 py-1 rounded-md text-slate-700">
                  📅 {metadata.dataset_timeframe}
                </span>
              )}
              {metadata.records_analyzed !== undefined && (
                <span className="flex items-center gap-1 bg-slate-100 px-2.5 py-1 rounded-md text-slate-700">
                  📊 {metadata.records_analyzed.toLocaleString()} records processed
                </span>
              )}
              {metadata.confidence_level && (
                <span className={`px-2.5 py-1 rounded-md capitalize font-semibold ${
                  metadata.confidence_level === 'high' 
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
                    : metadata.confidence_level === 'medium'
                    ? 'bg-amber-50 text-amber-700 border border-amber-200'
                    : 'bg-slate-100 text-slate-700'
                }`}>
                  Confidence: {metadata.confidence_level}
                </span>
              )}
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 self-start md:self-auto no-print">
          <button
            onClick={handleCopyJson}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors"
            title="Copy Raw Deterministic JSON"
          >
            {copiedJson ? '✓ Copied' : '📋 Copy JSON'}
          </button>
          <button
            onClick={() => window.print()}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-xl shadow-sm transition-all"
            title="Print or Save PDF Report"
          >
            🖨️ Export PDF
          </button>
        </div>
      </div>

      {/* 2. TAB NAVIGATION */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 no-print">
        <button
          onClick={() => setActiveTab('executive')}
          className={`px-4 py-2 text-sm font-semibold rounded-xl transition-all ${
            activeTab === 'executive'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          Executive Summary & KPIs
        </button>
        <button
          onClick={() => setActiveTab('charts')}
          className={`px-4 py-2 text-sm font-semibold rounded-xl transition-all ${
            activeTab === 'charts'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          Visual Analytics ({visualizations.length})
        </button>
        <button
          onClick={() => setActiveTab('performance')}
          className={`px-4 py-2 text-sm font-semibold rounded-xl transition-all ${
            activeTab === 'performance'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          Performance & Strategy
        </button>
        <button
          onClick={() => setActiveTab('audit')}
          className={`px-4 py-2 text-sm font-semibold rounded-xl transition-all ${
            activeTab === 'audit'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          Audit Trace ({results?.length || 0} Steps)
        </button>
      </div>

      {/* 3. TAB CONTENT */}

      {/* TAB 1: EXECUTIVE & KPIS */}
      {(activeTab === 'executive' || typeof window === 'undefined') && (
        <div className="space-y-6">
          {/* Executive Summary Card */}
          {executive_summary && (
            <div className="bg-gradient-to-br from-white via-white to-blue-50/40 border border-slate-200/90 rounded-2xl p-6 shadow-sm relative overflow-hidden">
              <div className="absolute top-0 left-0 w-2 h-full bg-blue-600" />
              <div className="pl-2">
                <span className="text-xs font-bold text-blue-600 tracking-wider uppercase">Direct Answer</span>
                <h3 className="text-xl font-extrabold text-slate-900 tracking-tight mt-1 mb-2">
                  {executive_summary.headline}
                </h3>
                <p className="text-slate-700 text-base leading-relaxed mb-4">
                  {executive_summary.context}
                </p>

                {executive_summary.key_drivers && executive_summary.key_drivers.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-slate-100">
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">
                      Key Performance Drivers
                    </span>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {executive_summary.key_drivers.map((driver, i) => (
                        <div key={i} className="flex items-start gap-2 bg-white/80 p-3 rounded-xl border border-slate-200/80 text-sm text-slate-800">
                          <span className="text-blue-600 font-bold">›</span>
                          <span>{driver}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* KPI Cards Grid */}
          {kpi_cards.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Core Performance Metrics
                </h4>
                <span className="text-xs text-slate-500">{kpi_cards.length} metrics monitored</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {kpi_cards.map((kpi: KPICard) => (
                  <div
                    key={kpi.id}
                    className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between text-xs font-medium text-slate-500 mb-1">
                        <span>{kpi.label}</span>
                        {kpi.status === 'positive' && (
                          <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full text-[11px] font-semibold border border-emerald-200 flex items-center gap-0.5">
                            ▲ +{kpi.variance_pct ?? 0}%
                          </span>
                        )}
                        {kpi.status === 'negative' && (
                          <span className="text-rose-700 bg-rose-50 px-2 py-0.5 rounded-full text-[11px] font-semibold border border-rose-200 flex items-center gap-0.5">
                            ▼ {kpi.variance_pct ?? 0}%
                          </span>
                        )}
                        {kpi.status === 'neutral' && (
                          <span className="text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full text-[11px] font-medium">
                            • {kpi.variance_pct ? `${kpi.variance_pct}%` : 'Flat'}
                          </span>
                        )}
                      </div>
                      <div className="text-3xl font-extrabold text-slate-900 tracking-tight mt-2">
                        {kpi.formatted_value || (kpi.value !== null && kpi.value !== undefined ? kpi.value.toLocaleString() : 'N/A')}
                      </div>
                    </div>

                    {kpi.comparison_label && (
                      <div className="mt-3 pt-3 border-t border-slate-100 text-xs text-slate-400 font-medium">
                        {kpi.comparison_label}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick Chart Preview in Overview */}
          {visualizations.length > 0 && (
            <div className="pt-2">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Primary Data Visualization
                </h4>
                <button
                  onClick={() => setActiveTab('charts')}
                  className="text-xs font-semibold text-blue-600 hover:text-blue-800 no-print"
                >
                  View All Charts ({visualizations.length}) →
                </button>
              </div>
              <ChartRenderer spec={visualizations[0]} />
            </div>
          )}
        </div>
      )}

      {/* TAB 2: VISUAL ANALYTICS */}
      {activeTab === 'charts' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-lg">Visual Data Intelligence</h3>
            <span className="text-xs text-slate-500 bg-slate-100 px-3 py-1 rounded-full">
              {visualizations.length} Interactive Charts
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {visualizations.map((viz: VisualizationSpec) => (
              <ChartRenderer key={viz.chart_id} spec={viz} />
            ))}
          </div>

          {visualizations.length === 0 && (
            <div className="p-12 text-center text-slate-400 bg-white border border-slate-200 rounded-2xl">
              No specific charts were returned for this query.
            </div>
          )}
        </div>
      )}

      {/* TAB 3: PERFORMANCE & STRATEGY */}
      {activeTab === 'performance' && (
        <div className="space-y-6">
          {/* Top Performers and Risks Matrix */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Top Performers */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm">
              <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
                <div className="p-1.5 bg-emerald-50 text-emerald-600 rounded-lg">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <h4 className="font-bold text-slate-900 text-base">Top Performers & Growth Leaders</h4>
              </div>

              {performance_breakdown?.top_performers && performance_breakdown.top_performers.length > 0 ? (
                <div className="space-y-3">
                  {performance_breakdown.top_performers.map((item: PerformanceItem, i: number) => (
                    <div key={i} className="p-3 bg-emerald-50/40 border border-emerald-100 rounded-xl flex items-center justify-between gap-3">
                      <div>
                        <div className="font-semibold text-slate-900 text-sm">{item.name}</div>
                        {item.impact && <div className="text-xs text-emerald-800 mt-0.5">{item.impact}</div>}
                      </div>
                      <div className="font-mono font-bold text-emerald-700 text-sm whitespace-nowrap">
                        {item.metric_value}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">No specific top performers identified.</p>
              )}
            </div>

            {/* Underperformers & Risks */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm">
              <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
                <div className="p-1.5 bg-rose-50 text-rose-600 rounded-lg">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <h4 className="font-bold text-slate-900 text-base">Vulnerabilities & Risk Drivers</h4>
              </div>

              {performance_breakdown?.underperformers_or_risks && performance_breakdown.underperformers_or_risks.length > 0 ? (
                <div className="space-y-3">
                  {performance_breakdown.underperformers_or_risks.map((item: PerformanceItem, i: number) => (
                    <div key={i} className="p-3 bg-rose-50/40 border border-rose-100 rounded-xl flex items-center justify-between gap-3">
                      <div>
                        <div className="font-semibold text-slate-900 text-sm">{item.name}</div>
                        {item.mitigation && <div className="text-xs text-rose-800 mt-0.5">Mitigation: {item.mitigation}</div>}
                      </div>
                      <div className="font-mono font-bold text-rose-700 text-sm whitespace-nowrap">
                        {item.metric_value}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">No underperformers or active risks detected.</p>
              )}
            </div>
          </div>

          {/* Strategic Roadmap Cards */}
          {recommendations && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {recommendations.immediate_30_days && (
                <div className="bg-gradient-to-br from-white to-amber-50/40 border border-amber-200/80 rounded-2xl p-6 shadow-sm">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-amber-700 bg-amber-100 px-2.5 py-0.5 rounded-full">
                      Immediate Action
                    </span>
                    <span className="text-xs text-slate-500 font-medium">30-Day Decision</span>
                  </div>
                  <h4 className="text-base font-bold text-slate-900 mb-2">Operational Execution</h4>
                  <p className="text-sm text-slate-700 leading-relaxed">
                    {recommendations.immediate_30_days}
                  </p>
                </div>
              )}

              {recommendations.strategic_90_days && (
                <div className="bg-gradient-to-br from-white to-indigo-50/40 border border-indigo-200/80 rounded-2xl p-6 shadow-sm">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-indigo-700 bg-indigo-100 px-2.5 py-0.5 rounded-full">
                      Strategic Realignment
                    </span>
                    <span className="text-xs text-slate-500 font-medium">90-Day Horizon</span>
                  </div>
                  <h4 className="text-base font-bold text-slate-900 mb-2">Long-Term Impact</h4>
                  <p className="text-sm text-slate-700 leading-relaxed">
                    {recommendations.strategic_90_days}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Data Caveats & Notes */}
          {performance_breakdown?.data_notes && performance_breakdown.data_notes.length > 0 && (
            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 text-xs text-slate-600">
              <span className="font-bold text-slate-800 uppercase tracking-wider block mb-2">
                Operational Caveats & Calculation Footnotes
              </span>
              <ul className="list-disc pl-5 space-y-1">
                {performance_breakdown.data_notes.map((note: string, i: number) => (
                  <li key={i}>{note}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* TAB 4: AUDIT TRACE */}
      {activeTab === 'audit' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-900 text-lg">Autonomous Execution Trace</h3>
              <p className="text-xs text-slate-500">
                Complete deterministic audit trail of all SQL queries and Python sandbox calculations.
              </p>
            </div>
            <span className="text-xs font-mono bg-slate-100 text-slate-700 px-3 py-1 rounded-full">
              DuckDB Engine + Docker Sandbox
            </span>
          </div>

          {results && results.length > 0 ? (
            results.map((res: ExecutionStepResult, index: number) => {
              const queryCode = res.query || '';
              return (
                <div key={index} className="bg-slate-900 text-slate-100 rounded-2xl overflow-hidden border border-slate-800 shadow-md">
                  <div className="bg-slate-800 px-5 py-3 flex items-center justify-between border-b border-slate-700">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 bg-blue-500/20 text-blue-300 font-mono text-xs rounded uppercase font-semibold">
                        {res.tool || 'sql'}
                      </span>
                      <span className="text-sm font-semibold text-slate-200">
                        Step {index + 1}: {res.task || 'Aggregating Data'}
                      </span>
                    </div>

                    {queryCode && (
                      <button
                        onClick={() => handleCopyCode(queryCode, index)}
                        className="text-xs font-mono text-slate-400 hover:text-white bg-slate-700 px-2.5 py-1 rounded transition-colors"
                      >
                        {copiedCodeIndex === index ? 'Copied!' : 'Copy Query'}
                      </button>
                    )}
                  </div>

                  {queryCode && (
                    <div className="p-4 bg-slate-950/80 font-mono text-xs text-emerald-400 overflow-x-auto border-b border-slate-800">
                      <pre className="whitespace-pre-wrap">{queryCode}</pre>
                    </div>
                  )}

                  <div className="p-4 bg-slate-900">
                    <div className="text-[11px] font-mono text-slate-400 mb-2 uppercase tracking-wider">Computed Result Rows</div>
                    <pre className="font-mono text-xs text-slate-300 overflow-x-auto max-h-60 bg-slate-950 p-3 rounded-lg">
                      {JSON.stringify(res.results, null, 2)}
                    </pre>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="p-12 text-center text-slate-400 bg-white border border-slate-200 rounded-2xl">
              No execution trace available for this session.
            </div>
          )}
        </div>
      )}

      {/* Suggested Follow-up Prompts */}
      {onAskFollowUp && (
        <div className="mt-8 pt-6 border-t border-slate-200 no-print">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-3">
            Suggested Follow-Up Inquiries
          </span>
          <div className="flex flex-wrap gap-2">
            {[
              "Show month-over-month growth rate",
              "Which categories drive 80% of volume?",
              "Detect any statistical outliers or anomalies",
              "Predict next quarter trajectory"
            ].map((prompt, i) => (
              <button
                key={i}
                onClick={() => onAskFollowUp(prompt)}
                className="text-xs font-medium text-slate-700 bg-white hover:bg-blue-50 hover:text-blue-700 border border-slate-200 hover:border-blue-200 px-3.5 py-2 rounded-xl transition-all shadow-2xs"
              >
                💬 {prompt}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
