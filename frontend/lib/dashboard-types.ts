import type { PresentationApiStatus, SatelliteStatus, WatchFactor } from "@/lib/watch-presentation";

export type ApiStatus = "connecting" | "connected" | "error";
export type Factor = WatchFactor;

export interface DataSourceInfo {
  name: string;
  source_type: string;
  status: string;
  observed_at: string | null;
  age_hours: number | null;
  note: string;
  url?: string | null;
}

export interface PredictionData {
  station_id: string;
  assessment_status: "model_demo" | "operational_model" | "environmental_watch" | "insufficient_data";
  risk_score: number | null;
  score_label: string;
  score_is_probability: boolean;
  risk_level: string;
  alert_status: string;
  shap_explanation: string;
  location: string;
  lat: number;
  lon: number;
  timestamp: string;
  recommendations: string[];
  features: Factor[];
  history_trend: number[];
  data_status: "synthetic_model_demo" | "live_context" | "live_watch" | "live_operational";
  data_source: string;
  observed_at: string;
  is_demo: boolean;
  data_age_hours: number | null;
  confidence_score: number | null;
  confidence_level: string;
  confidence_note: string;
  imagery_status: "simulated" | "available" | "stale" | "unavailable";
  imagery_mode: "simulated_fresh" | "context_only" | "no_imagery";
  analysis_method: "xgboost_shap_demo" | "xgboost_shap_operational" | "weather_first_xgboost_shap_rule_watch" | "insufficient_data";
  history_period_days: number;
  data_sources: DataSourceInfo[];
  limitations: string[];
  model_name: string | null;
  model_version: string | null;
  forecast_horizon: string | null;
  shap_output_space: "raw_margin" | "watch_index_points" | null;
  rule_basis: string[];
}

export interface StationMetadata {
  location: string;
  lat: number;
  lon: number;
  data_mode: "synthetic_model_demo" | "live_context" | "live_weather_watch";
}

export interface TestState {
  score: number;
  factors: Factor[];
  satelliteStatus: SatelliteStatus;
  fieldVerificationCount: number;
  apiStatus: Extract<PresentationApiStatus, "connected" | "mocked">;
}

export type TestScenarioKey = "normal" | "watch" | "urgent";

export type MonitoringStatus = "normal" | "watch" | "warning" | "unavailable";

export interface MonitoringStation {
  id: string;
  name: string;
  location: string;
  latitude: number;
  longitude: number;
  status: MonitoringStatus;
  score: number | null;
  updatedAt: string;
  history: number[];
  historyPeriodDays: number;
}
