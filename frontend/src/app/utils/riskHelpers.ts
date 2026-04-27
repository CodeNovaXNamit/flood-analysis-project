import { Feature } from 'geojson';
import { WardProperties, RiskLevel } from '../types/flood.types';

export function getRiskColor(flood_risk: number): string {
  if (flood_risk < 0.33) return '#4ADE80'; // Low Zone (Green)
  if (flood_risk < 0.66) return '#FDE047'; // Medium Zone (Yellow)
  return '#EF4444';                       // High Risk Zone (Red)
}

export function getRiskLabel(flood_risk: number): 'Low' | 'Medium' | 'High' {
  if (flood_risk < 0.33) return 'Low';
  if (flood_risk < 0.66) return 'Medium';
  return 'High';
}

export function getRiskLevel(flood_risk: number): RiskLevel {
  if (flood_risk < 0.33) return 'low';
  if (flood_risk < 0.66) return 'medium';
  return 'high';
}

export function computeCityReadiness(features: Feature<any, WardProperties>[]): number {
  if (features.length === 0) return 0;
  const avgRisk = features.reduce((sum, f) => sum + f.properties.flood_risk, 0) / features.length;
  // This is the "Pre-Monsoon Readiness Score" requested by the hackathon
  return Math.round((1 - avgRisk) * 100);
}

export function computeHotspots(features: Feature<any, WardProperties>[]): number {
  return features.filter(f => f.properties.flood_risk > 0.66).length;
}

export function formatPopulation(n: number): string {
  if (n >= 1000) {
    return (n / 1000).toFixed(1) + 'K';
  }
  return n.toLocaleString();
}

export function getExplainabilityText(score: number): string {
  if (score >= 80) return "Optimal Pre-Monsoon Readiness: Infrastructure capacity significantly exceeds predicted saturation levels.";
  if (score >= 60) return "Moderate Readiness: Strategic maintenance required in low-lying transit corridors before peak monsoon.";
  if (score >= 40) return "Readiness Deficit: Multiple micro-hotspots reporting drainage integrity below 60%. Proactive deployment advised.";
  return "Critical Readiness Gap: Systemic vulnerability detected. Widespread inundation predicted under nominal rainfall.";
}
