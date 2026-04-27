'use client';

import { useState, useMemo } from 'react';
import { FeatureCollection, Polygon } from 'geojson';
import { WardProperties } from '../types/flood.types';

export function useSimulation(
  baseGeoJSON: FeatureCollection<Polygon, WardProperties>,
  liveRainfall: number = 0
) {
  const [isSimulationActive, setIsSimulationActive] = useState(false);
  const [rainfallIncreasePct, setRainfallIncrease] = useState(0);

  const simulatedGeoJSON = useMemo(() => {
    // Current Rainfall Impact: 1mm adds approx 0.015 to risk factor (max impact at 40mm)
    const liveImpact = Math.min(0.6, (liveRainfall / 40));

    return {
      ...baseGeoJSON,
      features: baseGeoJSON.features.map(feature => {
        const baseRisk = feature.properties.flood_risk;
        
        // Final risk = Base (Synthetic) + Live Weather Delta + Simulation Delta
        // Simulation IncreasePct adds up to 0.6 risk
        const simImpact = isSimulationActive ? (rainfallIncreasePct / 100) * 0.6 : 0;
        
        const finalRisk = Math.min(1, baseRisk + liveImpact + simImpact);

        return {
          ...feature,
          properties: {
            ...feature.properties,
            flood_risk: finalRisk,
          },
        };
      }),
    };
  }, [baseGeoJSON, isSimulationActive, rainfallIncreasePct, liveRainfall]);

  const toggleSimulation = () => {
    setIsSimulationActive(!isSimulationActive);
    if (isSimulationActive) setRainfallIncrease(0);
  };

  return {
    isSimulationActive,
    rainfallIncreasePct,
    simulatedGeoJSON,
    toggleSimulation,
    setRainfallIncrease,
  };
}
