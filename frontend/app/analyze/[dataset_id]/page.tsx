'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { 
  analyzeDataset, 
  AnalysisResponse, 
  getDatasetProfile, 
  DatasetProfileResponse,
  ColumnMetricInfo
} from '@/lib/api';
import ChatInterface from '@/app/components/ChatInterface';
import AnalysisResult from '@/app/components/AnalysisResult';

export default function AnalyzePage() {
  const params = useParams();
  const router = useRouter();
  const datasetId = params.dataset_id as string;
  
  const [profile, setProfile] = useState<DatasetProfileResponse | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSchema, setShowSchema] = useState(false);
  const [copiedId, setCopiedId] = useState(false);

  useEffect(() => {
    if (datasetId) {
      getDatasetProfile(datasetId)
        .then((data) => {
          setProfile(data);
        })
        .catch((err) => {
          console.error("Failed to load profile:", err);
        });
    }
  }, [datasetId]);

  const handleAskQuestion = async (question: string) => {
    setIsLoading(true);
    setError(null);
    setAnalysis(null);
    
    try {
      const result = await analyzeDataset(datasetId, question);
      setAnalysis(result);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to analyze dataset.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyId = () => {
    navigator.clipboard.writeText(datasetId);
    setCopiedId(true);
    setTimeout(() => setCopiedId(false), 2000);
  };

  return (
    <main className="min-h-screen bg-slate-50/50 flex flex-col items-center">
      {/* 1. TOP GLOBAL NAVIGATION BAR */}
      <header className="w-full bg-white border-b border-slate-200 sticky top-0 z-40 px-6 py-3.5 shadow-2xs no-print">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => router.push('/')}
              className="flex items-center gap-2 text-slate-900 font-bold text-lg hover:opacity-85 transition-opacity"
            >
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-sm font-black text-sm">
                A
              </div>
              <span className="tracking-tight">Autonomous Data Analyst</span>
            </button>
            <span className="text-slate-300">|</span>
            <div className="flex items-center gap-1.5 text-xs text-slate-500 font-mono bg-slate-100/80 px-2.5 py-1 rounded-lg">
              <span>ID: {datasetId ? `${datasetId.substring(0, 8)}…` : '—'}</span>
              <button 
                onClick={handleCopyId} 
                className="hover:text-blue-600 ml-0.5 text-slate-400"
                title="Copy Full Dataset ID"
              >
                {copiedId ? '✓' : '⧉'}
              </button>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowSchema(!showSchema)}
              className={`text-xs font-semibold px-3.5 py-2 rounded-xl border transition-all flex items-center gap-1.5 ${
                showSchema 
                  ? 'bg-blue-50 text-blue-700 border-blue-200' 
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
              }`}
            >
              <span>📋</span>
              <span>{showSchema ? 'Hide Schema' : 'Data Dictionary'}</span>
              {profile && (
                <span className="text-[10px] font-mono bg-slate-200/80 text-slate-700 px-1.5 py-0.2 rounded-md">
                  {profile.columns} cols
                </span>
              )}
            </button>

            <button 
              onClick={() => router.push('/')}
              className="text-xs font-semibold text-slate-700 hover:text-slate-900 bg-white hover:bg-slate-50 border border-slate-200 px-3.5 py-2 rounded-xl transition-all shadow-2xs"
            >
              + Upload Dataset
            </button>
          </div>
        </div>
      </header>

      {/* 2. MAIN WORKSPACE CONTAINER */}
      <div className="w-full max-w-7xl px-4 sm:px-6 py-8 space-y-6 flex-1">
        
        {/* Quick Dataset Summary Stats Banner */}
        {profile && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 no-print">
            <div className="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs">
              <span className="text-xs font-medium text-slate-500 block mb-1">Total Records</span>
              <div className="text-2xl font-extrabold text-slate-900 font-mono">
                {profile.rows.toLocaleString()}
              </div>
            </div>
            <div className="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs">
              <span className="text-xs font-medium text-slate-500 block mb-1">Total Features</span>
              <div className="text-2xl font-extrabold text-slate-900 font-mono">
                {profile.columns} <span className="text-xs font-sans text-slate-400 font-normal">columns</span>
              </div>
            </div>
            <div className="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs">
              <span className="text-xs font-medium text-slate-500 block mb-1">Duplicate Rows</span>
              <div className="text-2xl font-extrabold text-slate-900 font-mono">
                {profile.duplicate_rows}
              </div>
            </div>
            <div className="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs">
              <span className="text-xs font-medium text-slate-500 block mb-1">Execution Engine</span>
              <div className="text-sm font-bold text-emerald-600 flex items-center gap-1.5 mt-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                DuckDB + Sandbox
              </div>
            </div>
          </div>
        )}

        {/* Expandable Data Dictionary / Schema Inspector */}
        {showSchema && profile && (
          <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-sm no-print transition-all">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
              <div>
                <h3 className="font-bold text-slate-900 text-base">Dataset Schema & Profiling Summary</h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Detailed distribution of all {profile.columns} columns identified by the autonomous profiler.
                </p>
              </div>
              <button
                onClick={() => setShowSchema(false)}
                className="text-xs text-slate-400 hover:text-slate-600"
              >
                ✕ Close
              </button>
            </div>

            <div className="overflow-x-auto max-h-96">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 uppercase font-semibold sticky top-0 border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-3">Column Name</th>
                    <th className="py-2.5 px-3">Inferred Type</th>
                    <th className="py-2.5 px-3">Unique Values</th>
                    <th className="py-2.5 px-3">Missing Rate</th>
                    <th className="py-2.5 px-3">Statistical Summary</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {Object.entries(profile.columns_info || {}).map(([colName, colInfo]: [string, ColumnMetricInfo]) => (
                    <tr key={colName} className="hover:bg-slate-50/70">
                      <td className="py-2.5 px-3 font-semibold text-slate-900 font-mono">{colName}</td>
                      <td className="py-2.5 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                          colInfo.detected_type === 'numeric'
                            ? 'bg-blue-50 text-blue-700'
                            : colInfo.detected_type === 'datetime'
                            ? 'bg-purple-50 text-purple-700'
                            : 'bg-slate-100 text-slate-700'
                        }`}>
                          {colInfo.detected_type}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-mono text-slate-600">{colInfo.unique}</td>
                      <td className="py-2.5 px-3 font-mono">
                        {colInfo.missing_percentage > 0 ? (
                          <span className="text-amber-600 font-semibold">{colInfo.missing_percentage}%</span>
                        ) : (
                          <span className="text-slate-400">0%</span>
                        )}
                      </td>
                      <td className="py-2.5 px-3 text-slate-600">
                        {colInfo.detected_type === 'numeric' && colInfo.mean !== undefined ? (
                          <span className="font-mono text-[11px]">
                            avg: {typeof colInfo.mean === 'number' ? colInfo.mean.toFixed(2) : '—'} | min: {String(colInfo.min)} | max: {String(colInfo.max)}
                          </span>
                        ) : colInfo.date_format ? (
                          <span className="font-mono text-[11px] text-purple-600">Format: {colInfo.date_format}</span>
                        ) : (
                          <span className="text-slate-400">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Chat / Query Prompt Component */}
        <div className="w-full no-print">
          <ChatInterface onSendMessage={handleAskQuestion} isLoading={isLoading} />
        </div>

        {/* Executive BI Results Area */}
        <div className="w-full pb-16">
          <AnalysisResult 
            response={analysis} 
            isLoading={isLoading} 
            error={error} 
            onAskFollowUp={handleAskQuestion}
          />
        </div>
      </div>
    </main>
  );
}
