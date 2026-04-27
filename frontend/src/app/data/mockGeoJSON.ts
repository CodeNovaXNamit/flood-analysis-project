import { FeatureCollection, Polygon } from 'geojson';
import { WardProperties } from '../types/flood.types';
import delhiWardsData from '../../../data/Delhi_Wards_with_rebalanced_risk.json';

const clamp01 = (value: number) => Math.max(0, Math.min(1, value));
const buildDeterministicWardId = (name: string) => {
  const normalized = name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 24);

  return normalized ? `W-${normalized}` : 'W-unnamed-ward';
};

// Helper to generate consistent synthetic data for real Delhi wards based on their name.
const genProps = (name: string | null, no: string | null, baseRisk?: number | null): WardProperties => {
  const safeName = name || "Unnamed Ward";
  const safeId = no || buildDeterministicWardId(safeName);
  
  // Seed based on name for consistent random values across renders
  let seed = 0;
  for (let i = 0; i < safeName.length; i++) {
    seed += safeName.charCodeAt(i);
  }
  
  const random = () => {
    const x = Math.sin(seed++) * 10000;
    return x - Math.floor(x);
  };

  const normalizedRisk = clamp01(baseRisk ?? random());
  const riskHistory = Array.from({ length: 7 }, () =>
    clamp01(normalizedRisk + (random() * 0.28 - 0.14))
  );

  return {
    ward_id: safeId,
    ward_name: safeName,
    flood_risk: normalizedRisk,
    drainage_capacity: clamp01(0.35 + random() * 0.45),
    population_affected: Math.round(random() * 50000),
    elevation_m: 200 + Math.round(random() * 50),
    trend: random() > 0.6 ? 'increasing' : random() > 0.3 ? 'stable' : 'decreasing',
    risk_history: riskHistory
  };
};

export const mockGeoJSON: FeatureCollection<Polygon, WardProperties> = {
  type: "FeatureCollection",
  features: delhiWardsData.features.map((f: any) => ({
    type: "Feature",
    geometry: f.geometry as Polygon,
    properties: genProps(f.properties.Ward_Name, f.properties.Ward_No, f.properties.risk)
  }))
};
