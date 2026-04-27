'use client';

import { useState, useEffect, useCallback } from 'react';
import { FeatureCollection, Polygon, Point } from 'geojson';
import { WardProperties, WeatherData } from '../types/flood.types';
import { PipelinePoint, PipelineRun } from '../types/pipeline.types';
import { mockGeoJSON } from '../data/mockGeoJSON';
import { mockWeather } from '../data/mockWeather';
import { microHotspotsData, HotspotProperties } from '../data/microHotspots';

const REFRESH_INTERVAL = 120000; // 2 minutes
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

function toHotspotCollection(points: PipelinePoint[]): FeatureCollection<Point, HotspotProperties> {
  return {
    type: 'FeatureCollection',
    features: points.map((point) => ({
      type: 'Feature',
      properties: {
        lat: point.lat,
        lon: point.lon,
        hotspot_risk: point.risk,
      },
      geometry: {
        type: 'Point',
        coordinates: [point.lon, point.lat],
      },
    })),
  };
}

export function useFloodData() {
  const [geoJSON, setGeoJSON] = useState<FeatureCollection<Polygon, WardProperties>>(mockGeoJSON);
  const [hotspots, setHotspots] = useState<FeatureCollection<Point, HotspotProperties>>(microHotspotsData);
  const [weather, setWeather] = useState<WeatherData>(mockWeather);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSync, setLastSync] = useState<Date>(new Date());
  const [latestPipelineRun, setLatestPipelineRun] = useState<PipelineRun | null>(null);
  const [pipelineUploading, setPipelineUploading] = useState(false);

  const fetchWeather = useCallback(async () => {
    try {
      const response = await fetch('https://wttr.in/Delhi?format=j1');
      if (!response.ok) throw new Error('Weather fetch failed');
      const data = await response.json();
      
      const current = data.current_condition[0];
      const todayForecast = data.weather[0];
      
      setWeather({
        temperature_c: parseFloat(current.temp_C),
        temp_min_c: parseFloat(todayForecast.mintempC),
        temp_max_c: parseFloat(todayForecast.maxtempC),
        rainfall_mm: parseFloat(current.precipMM),
        humidity_pct: parseInt(current.humidity),
        condition: current.weatherDesc[0].value,
        forecast: "Live telemetry active from wttr.in"
      });
      setLastSync(new Date());
    } catch (err) {
      console.warn("Weather sync failed, using fallback", err);
    }
  }, []);

  const fetchLatestPipelineRun = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/pipeline/runs/latest`, { cache: 'no-store' });
      if (!response.ok) {
        throw new Error('Latest pipeline request failed');
      }
      const data = await response.json();
      const run = (data.run ?? null) as PipelineRun | null;
      setLatestPipelineRun(run);
    } catch (err) {
      console.warn('Pipeline sync failed, keeping bundled hotspots', err);
    }
  }, []);

  const fetchGeoData = async () => {
    setGeoJSON(mockGeoJSON);
  };

  const syncAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    await Promise.all([fetchWeather(), fetchGeoData(), fetchLatestPipelineRun()]);
    setLoading(false);
  }, [fetchLatestPipelineRun, fetchWeather]);

  const uploadScenario = useCallback(async (file: File, scenarioName: string) => {
    setPipelineUploading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('scenario_name', scenarioName);

      const response = await fetch(`${API_BASE_URL}/api/pipeline/runs`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Scenario upload failed');
      }

      const run = data.run as PipelineRun;
      setLatestPipelineRun(run);
      setHotspots(run.result_points?.length ? toHotspotCollection(run.result_points) : microHotspotsData);
      setLastSync(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scenario upload failed');
      throw err;
    } finally {
      setPipelineUploading(false);
    }
  }, []);

  useEffect(() => {
    syncAll();
    const interval = setInterval(syncAll, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [syncAll]);

  return {
    apiBaseUrl: API_BASE_URL,
    geoJSON,
    hotspots,
    weather,
    loading,
    error,
    lastSync,
    latestPipelineRun,
    pipelineUploading,
    refetch: syncAll,
    uploadScenario,
  };
}
