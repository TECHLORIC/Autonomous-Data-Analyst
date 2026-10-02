import React from 'react';
import FileUpload from './components/FileUpload';

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center py-20 px-4">
      <div className="text-center max-w-3xl mb-12">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight mb-4">
          Autonomous Data Analyst
        </h1>
        <p className="text-xl text-gray-600">
          Upload your dataset and ask questions in natural language. 
          The AI will profile the data, plan the analysis, execute code, and provide insights.
        </p>
      </div>

      <FileUpload />
      
      <div className="mt-20 max-w-4xl w-full grid grid-cols-1 md:grid-cols-3 gap-8">
        <FeatureCard 
          title="Natural Language"
          description="Ask questions about your data as if you're talking to a human data analyst."
          icon="💬"
        />
        <FeatureCard 
          title="Deterministic Engine"
          description="Powered by DuckDB and Pandas for accurate, reproducible analytical results."
          icon="⚙️"
        />
        <FeatureCard 
          title="Actionable Insights"
          description="Get clear executive summaries, visual charts, and trend explanations."
          icon="📊"
        />
      </div>
    </main>
  );
}

function FeatureCard({ title, description, icon }: { title: string, description: string, icon: string }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center text-center">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="font-bold text-lg text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  );
}
