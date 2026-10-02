'use client';

import React from 'react';
import { AnalysisResponse } from '@/lib/api';
import ChartRenderer from './ChartRenderer';

interface AnalysisResultProps {
  response: AnalysisResponse | null;
  isLoading: boolean;
  error: string | null;
}

export default function AnalysisResult({ response, isLoading, error }: AnalysisResultProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin mb-4"></div>
        <h3 className="text-lg font-medium text-gray-700">Analyzing dataset...</h3>
        <p className="text-gray-500 text-sm mt-2">The AI is planning, executing SQL/Python, and generating insights.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 text-red-700 rounded-xl border border-red-100">
        <h3 className="font-bold text-lg mb-2">Analysis Failed</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (!response) {
    return (
      <div className="flex items-center justify-center p-12 bg-gray-50 rounded-xl border border-dashed border-gray-300 text-gray-500">
        Ask a question to start your analysis.
      </div>
    );
  }

  const { insights, visualizations, results } = response;
  
  return (
    <div className="space-y-6">
      {/* Executive Answer */}
      {insights.executive_answer && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-3">Executive Summary</h2>
          <p className="text-gray-700 text-lg leading-relaxed">{insights.executive_answer}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Findings & Trends */}
        <div className="space-y-6">
          {insights.key_findings && insights.key_findings.length > 0 && (
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <h3 className="font-bold text-gray-900 mb-3 flex items-center">
                <span className="mr-2">💡</span> Key Findings
              </h3>
              <ul className="list-disc pl-5 space-y-2 text-gray-700">
                {insights.key_findings.map((finding, i) => (
                  <li key={i}>{finding}</li>
                ))}
              </ul>
            </div>
          )}

          {insights.trends_and_anomalies && insights.trends_and_anomalies.length > 0 && (
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <h3 className="font-bold text-gray-900 mb-3 flex items-center">
                <span className="mr-2">📈</span> Trends & Anomalies
              </h3>
              <ul className="list-disc pl-5 space-y-2 text-gray-700">
                {insights.trends_and_anomalies.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Caveats & Next Steps */}
        <div className="space-y-6">
          {insights.caveats && insights.caveats.length > 0 && (
            <div className="bg-yellow-50 p-6 rounded-xl shadow-sm border border-yellow-200">
              <h3 className="font-bold text-yellow-900 mb-3 flex items-center">
                <span className="mr-2">⚠️</span> Caveats
              </h3>
              <ul className="list-disc pl-5 space-y-2 text-yellow-800">
                {insights.caveats.map((caveat, i) => (
                  <li key={i}>{caveat}</li>
                ))}
              </ul>
            </div>
          )}

          {insights.next_questions && insights.next_questions.length > 0 && (
            <div className="bg-blue-50 p-6 rounded-xl shadow-sm border border-blue-200">
              <h3 className="font-bold text-blue-900 mb-3 flex items-center">
                <span className="mr-2">🔍</span> Recommended Follow-ups
              </h3>
              <ul className="list-disc pl-5 space-y-2 text-blue-800">
                {insights.next_questions.map((q, i) => (
                  <li key={i}>{q}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Visualizations Placeholder */}
      {visualizations && visualizations.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="font-bold text-gray-900 mb-4 flex items-center">
            <span className="mr-2">📊</span> Generated Chart Specification
          </h3>
          <ChartRenderer spec={visualizations[0]} rawResults={results} />
        </div>
      )}

      {/* Raw Data Results for transparency */}
      {results && results.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 overflow-x-auto">
          <h3 className="font-bold text-gray-900 mb-4 text-sm uppercase tracking-wider">Raw Execution Trace</h3>
          {results.map((res, index) => (
            <div key={index} className="mb-4 last:mb-0 border-l-2 border-blue-200 pl-4">
              <div className="text-xs font-semibold text-gray-500 mb-1">
                Step: {String(res.task || res.query || 'Execution')} (Tool: {String(res.tool || 'unknown')})
              </div>
              <pre className="bg-gray-50 p-2 rounded text-xs overflow-x-auto text-gray-800">
                {JSON.stringify(res.results, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
