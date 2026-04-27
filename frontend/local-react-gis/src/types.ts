import type { FeatureCollection, Polygon, MultiPolygon } from 'geojson';

export type WardGeometry = Polygon | MultiPolygon;

export interface SourceWardProperties {
  Ward_Name: string;
  Ward_No: string;
  risk: number;
}

export interface WardMetrics {
  wardId: string;
  wardName: string;
  floodRisk: number;
  drainageCapacity: number;
  affectedPopulation: number;
  elevationM: number;
  readinessScore: number;
  trend: 'increasing' | 'stable' | 'decreasing';
}

export type WardDataset = FeatureCollection<WardGeometry, SourceWardProperties>;
