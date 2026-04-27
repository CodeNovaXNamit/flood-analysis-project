'use client';

import { useState, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { useFloodData } from './hooks/useFloodData';
import { useSimulation } from './hooks/useSimulation';
import { computeCityReadiness } from './utils/riskHelpers';
import { WardProperties } from './types/flood.types';

const FloodMap = dynamic(() => import('@/components/FloodMap'), {
  ssr: false,
  loading: () => <div className="h-full w-full bg-[#060D1A] flex items-center justify-center text-[var(--text-muted)] font-mono animate-pulse tracking-[0.3em] text-xs uppercase">GEOSPATIAL ENGINE INITIALIZING...</div>,
});

const TopBar = dynamic(() => import('@/components/TopBar'), {
  ssr: false,
  loading: () => <div className="h-[60px] w-full shrink-0 border-b border-[var(--border-subtle)] bg-[var(--bg-surface)]" />,
});

const Sidebar = dynamic(() => import('@/components/Sidebar'), {
  ssr: false,
  loading: () => <div className="h-full w-full border-l border-[var(--border-subtle)] bg-[var(--bg-base)]" />,
});

const HotspotPanel = dynamic(() => import('@/components/HotspotPanel'), {
  ssr: false,
});

const WardSearch = dynamic(() => import('@/components/WardSearch'), {
  ssr: false,
});

export default function Home() {
  const {
    apiBaseUrl,
    geoJSON,
    hotspots,
    weather,
    loading,
    error,
    lastSync,
    latestPipelineRun,
    pipelineUploading,
    uploadScenario,
  } = useFloodData();
  
  const { 
    isSimulationActive, 
    rainfallIncreasePct, 
    simulatedGeoJSON, 
    toggleSimulation, 
    setRainfallIncrease 
  } = useSimulation(geoJSON, weather.rainfall_mm);

  const [selectedWard, setSelectedWard] = useState<WardProperties | null>(null);
  const [focusedWardId, setFocusedWardId] = useState<string | null>(null);
  const [mapDisplayMode, setMapDisplayMode] = useState<'ward' | 'hotspot'>('ward');

  const cityReadiness = useMemo(() => computeCityReadiness(simulatedGeoJSON.features), [simulatedGeoJSON]);
  const wardProperties = useMemo(() => simulatedGeoJSON.features.map((feature) => feature.properties), [simulatedGeoJSON]);
  
  const handleWardSelect = (ward: WardProperties) => {
    setSelectedWard(ward);
    setFocusedWardId(ward.ward_id);
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-[var(--bg-base)] overflow-hidden font-sans">
      <TopBar 
        cityScore={cityReadiness} 
        isSimulating={isSimulationActive} 
      />
      
      <main className="flex-1 flex overflow-hidden">
        <div className="w-[60%] h-full relative border-r border-[var(--border-subtle)] overflow-hidden">
          <div className="absolute left-6 top-6 z-[1001] w-[320px] max-w-[calc(100%-3rem)]">
            <WardSearch wards={wardProperties} onSelect={handleWardSelect} />
          </div>
          <FloodMap 
            geoJSON={simulatedGeoJSON} 
            hotspots={hotspots}
            isSimulationActive={isSimulationActive}
            onWardClick={handleWardSelect}
            focusedWardId={focusedWardId}
            mapDisplayMode={mapDisplayMode}
            onMapDisplayModeChange={setMapDisplayMode}
          />
        </div>

        <div className="w-[40%] h-full relative">
          <Sidebar 
            geoJSON={simulatedGeoJSON}
            hotspots={hotspots}
            weather={weather}
            lastSync={lastSync}
            simActive={isSimulationActive}
            simRainfall={rainfallIncreasePct}
            onToggleSim={toggleSimulation}
            onValueChange={setRainfallIncrease}
            onViewDetails={handleWardSelect}
            latestPipelineRun={latestPipelineRun}
            pipelineUploading={pipelineUploading}
            pipelineError={error}
            onUploadScenario={uploadScenario}
            apiBaseUrl={apiBaseUrl}
          />
          
          <HotspotPanel 
            ward={selectedWard} 
            onClose={() => {
              setSelectedWard(null);
              setFocusedWardId(null);
            }} 
          />
        </div>
      </main>

      {(loading || error) && (
        <div className="fixed bottom-4 left-4 z-[9999] pointer-events-none">
          {loading && (
            <div className="bg-[var(--bg-elevated)] border border-[var(--border-subtle)] px-4 py-2 rounded-full text-xs font-mono animate-pulse shadow-2xl">
              SYNCING REAL-TIME TELEMETRY STREAM...
            </div>
          )}
          {error && (
            <div className="bg-red-900/80 border border-red-500 px-4 py-2 rounded-full text-xs font-mono text-red-200 mt-2 shadow-2xl backdrop-blur-md">
              ERROR: {error}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
