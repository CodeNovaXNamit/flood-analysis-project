export interface PipelinePoint {
  lat: number;
  lon: number;
  risk: number;
}

export interface PipelineSummary {
  latest_prediction_date: string;
  max_risk: number;
  mean_risk: number;
  high_risk_points: number;
  medium_risk_points: number;
  low_risk_points: number;
  top_points: PipelinePoint[];
}

export interface PipelineRun {
  run_id: string;
  scenario_name: string;
  uploaded_filename: string;
  status: string;
  created_at: string;
  updated_at: string;
  input_rows: number | null;
  interpolated_rows: number | null;
  output_rows: number | null;
  latest_prediction_date: string | null;
  upload_path: string | null;
  interpolated_path: string | null;
  enriched_path: string | null;
  predictions_path: string | null;
  final_output_path: string | null;
  summary: PipelineSummary | null;
  error_message: string | null;
  download_url: string;
  result_points: PipelinePoint[];
}
