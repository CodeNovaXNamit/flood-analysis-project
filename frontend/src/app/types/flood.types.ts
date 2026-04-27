export interface WardProperties {
  ward_id: string;
  ward_name: string;
  flood_risk: number;          // 0.0 – 1.0
  drainage_capacity: number;   // 0.0 – 1.0
  population_affected: number; // integer
  elevation_m: number;         // meters
  trend: 'increasing' | 'stable' | 'decreasing';
  risk_history: number[];      // last 7 days flood_risk values
}

export interface MicroHotspot {
  id: string;
  lat: number;
  lng: number;
  risk_score: number;
  type: 'drain_blockage' | 'low_lying' | 'clogged_outfall' | 'terrain_depression';
  last_inspected: string;
  deployment_priority: 'CRITICAL' | 'HIGH' | 'MEDIUM';
}

export type RiskLevel = 'low' | 'medium' | 'high';

export interface WeatherData {
  temperature_c: number;
  temp_min_c: number;
  temp_max_c: number;
  rainfall_mm: number;
  humidity_pct: number;
  condition: string;
  forecast: string;
}
