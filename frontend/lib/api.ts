export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface DatasetResponse {
  dataset_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  created_at: string;
  status: string;
}

export interface ColumnMetricInfo {
  dtype: string;
  detected_type: 'numeric' | 'datetime' | 'categorical' | 'boolean';
  missing: number;
  missing_percentage: number;
  unique: number;
  date_format?: string;
  min?: number | string | null;
  max?: number | string | null;
  mean?: number | null;
  median?: number | null;
  std?: number | null;
}

export interface DatasetProfileResponse {
  dataset_id: string;
  rows: number;
  columns: number;
  column_names: string[];
  duplicate_rows: number;
  columns_info: Record<string, ColumnMetricInfo>;
  numeric_columns?: string[];
  datetime_columns?: string[];
  categorical_columns?: string[];
}

export interface KPICard {
  id: string;
  label: string;
  value: number;
  formatted_value: string;
  comparison_label?: string;
  variance_pct?: number;
  status: 'positive' | 'negative' | 'neutral';
}

export interface VisualizationSpec {
  chart_id: string;
  title: string;
  chart_type: 'line' | 'bar' | 'donut' | 'area';
  x_axis_key: string;
  y_axis_key: string;
  series_keys?: string[];
  data: Record<string, string | number>[];
  takeaway?: string;
}

export interface PerformanceItem {
  name: string;
  metric_value: string;
  impact?: string;
  mitigation?: string;
}

export interface ExecutiveInsights {
  status?: string;
  query?: string;
  metadata?: {
    dataset_timeframe?: string;
    records_analyzed?: number;
    confidence_level?: 'high' | 'medium' | 'low';
  };
  executive_summary?: {
    headline: string;
    context: string;
    key_drivers: string[];
  };
  kpi_cards?: KPICard[];
  visualizations?: VisualizationSpec[];
  performance_breakdown?: {
    top_performers?: PerformanceItem[];
    underperformers_or_risks?: PerformanceItem[];
    data_notes?: string[];
  };
  recommendations?: {
    immediate_30_days?: string;
    strategic_90_days?: string;
  };
  executive_answer?: string;
  key_findings?: string[];
  trends_and_anomalies?: string[];
  caveats?: string[];
  next_questions?: string[];
}

export interface ExecutionStepResult {
  tool?: string;
  task?: string;
  query?: string;
  results?: unknown;
}

export interface AnalysisResponse {
  dataset_id: string;
  question: string;
  plan: Record<string, unknown>;
  results: ExecutionStepResult[];
  visualizations: Record<string, unknown>[];
  insights: ExecutiveInsights;
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
