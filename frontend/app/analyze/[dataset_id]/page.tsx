'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { analyzeDataset, AnalysisResponse, getDatasetProfile, DatasetProfileResponse } from '@/lib/api';
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

  useEffect(() => {
    if (datasetId) {
      getDatasetProfile(datasetId)
        .then(setProfile)
        .catch((err) => {
          console.error("Failed to load profile:", err);
          // For MVP, we might still proceed even if profile fails to load in UI, but it's good to show
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

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
      <div className="w-full max-w-5xl mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analysis Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Dataset ID: <span className="font-mono">{datasetId}</span></p>
        </div>
        <button 
          onClick={() => router.push('/')}
          className="text-sm font-medium text-blue-600 hover:text-blue-800 bg-blue-50 px-4 py-2 rounded-lg"
        >
          Upload New Dataset
        </button>
      </div>

      {profile && (
        <div className="w-full max-w-5xl mb-8 bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex space-x-8 text-sm">
          <div><span className="font-semibold text-gray-500">Rows:</span> <span className="font-mono text-gray-900">{profile.rows}</span></div>
          <div><span className="font-semibold text-gray-500">Columns:</span> <span className="font-mono text-gray-900">{profile.columns}</span></div>
          <div className="flex-1"><span className="font-semibold text-gray-500">Fields:</span> <span className="text-gray-900 truncate block max-w-lg">{profile.column_names?.join(', ')}</span></div>
        </div>
      )}

      <div className="w-full max-w-5xl mb-12">
        <ChatInterface onSendMessage={handleAskQuestion} isLoading={isLoading} />
      </div>

      <div className="w-full max-w-5xl pb-20">
        <AnalysisResult response={analysis} isLoading={isLoading} error={error} />
      </div>
    </main>
  );
}
