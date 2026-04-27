import type { Feature } from 'geojson';
import type { SourceWardProperties, WardGeometry, WardMetrics } from '../types';

const createSeed = (value: string) => {
  let seed = 0;
  for (let index = 0; index < value.length; index += 1) {
    seed = (seed << 5) - seed + value.charCodeAt(index);
    seed |= 0;
  }
  return Math.abs(seed);
};

const seededUnit = (seed: number, offset: number) => {
  const x = Math.sin(seed + offset) * 10000;
  return x - Math.floor(x);
};

export const getRiskColor = (risk: number) => {
  if (risk < 0.2) return '#4ade80';
  if (risk < 0.4) return '#a3e635';
  if (risk < 0.6) return '#facc15';
  if (risk < 0.8) return '#fb923c';
  return '#ef4444';
};

export const getRiskLabel = (risk: number) => {
  if (risk < 0.2) return 'Low';
  if (risk < 0.4) return 'Guarded';
  if (risk < 0.6) return 'Elevated';
  if (risk < 0.8) return 'High';
  return 'Critical';
};

export const createWardMetrics = (
  feature: Feature<WardGeometry, SourceWardProperties>,
): WardMetrics => {
  const wardName = feature.properties.Ward_Name;
  const wardId = feature.properties.Ward_No;
  const floodRisk = feature.properties.risk;
  const seed = createSeed(`${wardId}:${wardName}`);
  const drainageCapacity = Math.round((0.35 + seededUnit(seed, 1) * 0.5) * 100);
  const affectedPopulation = Math.round(8000 + seededUnit(seed, 2) * 62000);
  const elevationM = Math.round(198 + seededUnit(seed, 3) * 42);
  const readinessScore = Math.max(0, Math.round((1 - floodRisk) * 100));
  const trendValue = seededUnit(seed, 4);

  return {
    wardId,
    wardName,
    floodRisk,
    drainageCapacity,
    affectedPopulation,
    elevationM,
    readinessScore,
    trend: trendValue > 0.66 ? 'increasing' : trendValue > 0.33 ? 'stable' : 'decreasing',
  };
};
