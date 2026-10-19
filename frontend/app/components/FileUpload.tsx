'use client';

import React, { useCallback, useState } from 'react';
import { useRouter } from 'next/navigation';
import { uploadDataset } from '@/lib/api';

export default function FileUpload() {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const router = useRouter();

  const handleUpload = useCallback(async (file: File) => {
    setSelectedFile(file);
    setIsUploading(true);
    setError(null);
    try {
      const response = await uploadDataset(file);
      router.push(`/analyze/${response.dataset_id}`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to upload file');
      }
      setSelectedFile(null);
    } finally {
      setIsUploading(false);
    }
  }, [router]);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleUpload(e.dataTransfer.files[0]);
    }
  }, [handleUpload]);

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleUpload(e.target.files[0]);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={`relative border-2 border-dashed rounded-3xl p-10 md:p-14 text-center transition-all bg-white shadow-sm hover:shadow-md
          ${isDragging 
            ? 'border-blue-500 bg-blue-50/60 ring-4 ring-blue-500/10' 
            : 'border-slate-200 hover:border-slate-300'}
          ${isUploading ? 'opacity-70 cursor-wait' : 'cursor-pointer'}
        `}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => !isUploading && document.getElementById('file-upload')?.click()}
      >
        <input
          id="file-upload"
          type="file"
          className="hidden"
          onChange={onFileChange}
          disabled={isUploading}
          accept=".csv,.xlsx,.json"
        />
        
        <div className="flex flex-col items-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center shadow-inner">
            {isUploading ? (
              <div className="w-8 h-8 border-3 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
            ) : (
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            )}
          </div>
          
          <div className="space-y-1.5">
            {isUploading ? (
              <div>
                <p className="font-bold text-lg text-slate-800">
                  Uploading & Profiling {selectedFile?.name}...
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  Parsing tabular schema and inferring column data types...
                </p>
              </div>
            ) : (
              <>
                <p className="font-bold text-lg text-slate-900 tracking-tight">
                  Drop your dataset here, or <span className="text-blue-600 hover:underline">browse files</span>
                </p>
                <p className="text-xs text-slate-500">
                  Instant profiling for structured business datasets up to 50MB
                </p>
              </>
            )}
          </div>

          {/* Supported Format Pills */}
          <div className="pt-2 flex items-center justify-center gap-2">
            <span className="px-2.5 py-1 text-[11px] font-mono font-semibold bg-slate-100 text-slate-600 rounded-lg">.CSV</span>
            <span className="px-2.5 py-1 text-[11px] font-mono font-semibold bg-slate-100 text-slate-600 rounded-lg">.XLSX</span>
            <span className="px-2.5 py-1 text-[11px] font-mono font-semibold bg-slate-100 text-slate-600 rounded-lg">.JSON</span>
          </div>
        </div>
      </div>
      
      {error && (
        <div className="mt-4 p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-2xl text-xs flex items-center gap-2">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
