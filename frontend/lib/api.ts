export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface DatasetResponse {
  dataset_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  created_at: string;
  status: string;
}

export interface DatasetProfileResponse {
  dataset_id: string;
  rows: number;
  columns: number;
  column_names: string[];
  duplicate_rows: number;
  columns_info: Record<string, unknown>;
}

export interface AnalysisResponse {
  dataset_id: string;
  question: string;
  plan: Record<string, unknown>;
  results: Record<string, unknown>[];
  visualizations: Record<string, unknown>[];
  insights: {
    executive_answer?: string;
    key_findings?: string[];
    trends_and_anomalies?: string[];
    caveats?: string[];
    next_questions?: string[];
  };
  errors: string[];
  retry_count: number;
}

export async function uploadDataset(file: File): Promise<DatasetResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/datasets/upload`, {
    method: 'POST',
    body: formData,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.success === false) {
    throw new Error(data.error || data.detail || 'Failed to upload dataset');
  }

  return data.data !== undefined ? data.data : data;
}

export async function getDatasetProfile(datasetId: string): Promise<DatasetProfileResponse> {
  const response = await fetch(`${API_BASE_URL}/datasets/${datasetId}/profile`);
  
  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.success === false) {
    throw new Error(data.error || data.detail || 'Failed to fetch profile');
  }
  
  return data.data !== undefined ? data.data : data;
}

export async function analyzeDataset(datasetId: string, question: string): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/agent/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ dataset_id: datasetId, question }),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.success === false) {
    throw new Error(data.error || data.detail || 'Analysis failed');
  }
  
  return data.data !== undefined ? data.data : data;
}
