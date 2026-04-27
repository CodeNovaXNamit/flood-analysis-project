'use client';

import { useState, useMemo } from 'react';
import { FeatureCollection, Polygon, Point } from 'geojson';
import { WardProperties, WeatherData } from '@/app/types/flood.types';
import { PipelineRun } from '@/app/types/pipeline.types';
import { HotspotProperties } from '@/app/data/microHotspots';
import { computeHotspots, computeCityReadiness, getRiskColor } from '@/app/utils/riskHelpers';
import { 
  Activity, 
  ShieldAlert, 
  Users, 
  MapPin, 
  Search, 
  BarChart3,
  ShieldCheck,
  LayoutGrid,
  Target,
  ChevronRight
} from 'lucide-react';
import WeatherWidget from './WeatherWidget';
import SimulationControls from './SimulationControls';
import PriorityAlerts from './PriorityAlerts';
import RiskPieChart from './RiskPieChart';
import ReadinessGauge from './ReadinessGauge';
import CountUp from './CountUp';
import AIAdvisorDialog from './AIAdvisorDialog';
import ScenarioUploadCard from './ScenarioUploadCard';

interface SidebarProps {
  geoJSON: FeatureCollection<Polygon, WardProperties>;
  hotspots?: FeatureCollection<Point, HotspotProperties>;
  weather: WeatherData;
  lastSync: Date;
  simActive: boolean;
  simRainfall: number;
  onToggleSim: () => void;
  onValueChange: (val: number) => void;
  onViewDetails: (ward: WardProperties) => void;
  latestPipelineRun: PipelineRun | null;
  pipelineUploading: boolean;
  pipelineError: string | null;
  onUploadScenario: (file: File, scenarioName: string) => Promise<void>;
  apiBaseUrl: string;
}

export default function Sidebar({
  geoJSON,
  hotspots,
  weather,
  lastSync,
  simActive,
  simRainfall,
  onToggleSim,
  onValueChange,
  onViewDetails,
  latestPipelineRun,
  pipelineUploading,
  pipelineError,
  onUploadScenario,
  apiBaseUrl,
}: SidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  
  const wardRiskHotspots = useMemo(() => computeHotspots(geoJSON.features), [geoJSON]);
  const avgRisk = geoJSON.features.reduce((sum, f) => sum + f.properties.flood_risk, 0) / geoJSON.features.length;
  const cityScore = computeCityReadiness(geoJSON.features);
  const totalPopAtRisk = geoJSON.features
    .filter(f => f.properties.flood_risk > 0.66)
    .reduce((sum, f) => sum + f.properties.population_affected, 0);

  const wardProperties = useMemo(() => geoJSON.features.map(f => f.properties), [geoJSON]);

  const filteredWards = useMemo(() => {
    if (!searchQuery) return wardProperties;
    return wardProperties.filter(w => 
      w.ward_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      w.ward_id.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [wardProperties, searchQuery]);

  return (
    <aside className="h-full w-full flex flex-col bg-[var(--bg-base)] border-l border-[var(--border-subtle)] overflow-hidden">
      {/* Strategic Environment Telemetry Section */}
      <div className="p-6 pb-0 space-y-6">
        <div className="space-y-1">
          <h2 className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em] mb-4">Environment Telemetry</h2>
          <WeatherWidget weather={weather} lastSync={lastSync} />
        </div>

        {/* Operational Awareness Section */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em]">Operational Awareness</h2>
            <span className="text-[8px] bg-blue-500/10 text-blue-500 px-1.5 py-0.5 rounded font-black uppercase tracking-tighter">Strategic KPI</span>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="flex flex-col p-4 rounded-xl bg-[var(--bg-card)] depth-card group">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-3.5 h-3.5 text-red-500" />
                <span className="text-[9px] text-muted-foreground font-bold uppercase tracking-tight">Hotspots</span>
              </div>
              <span className="text-2xl font-mono font-bold text-red-500 tracking-tighter">
                <CountUp end={wardRiskHotspots} />
              </span>
            </div>
            <div className="flex flex-col p-4 rounded-xl bg-[var(--bg-card)] depth-card group">
              <div className="flex items-center gap-2 mb-2">
                <ShieldCheck className="w-3.5 h-3.5 text-blue-500" />
                <span className="text-[9px] text-muted-foreground font-bold uppercase tracking-tight">Avg Risk</span>
              </div>
              <span className="text-2xl font-mono font-bold tracking-tighter text-[var(--accent-blue)]">
                <CountUp end={Math.round((100 - cityScore))} suffix="%" />
              </span>
            </div>
            <div className="flex flex-col p-4 rounded-xl bg-[var(--bg-card)] depth-card group">
              <div className="flex items-center gap-2 mb-2">
                <Users className="w-3.5 h-3.5 text-blue-400" />
                <span className="text-[9px] text-muted-foreground font-bold uppercase tracking-tight">At Risk</span>
              </div>
              <span className="text-2xl font-mono font-bold text-blue-400 tracking-tighter">
                <CountUp end={totalPopAtRisk / 1000} decimals={1} suffix="K" />
              </span>
            </div>
          </div>
        </section>

        <section className="pb-2">
          <AIAdvisorDialog 
            cityReadiness={cityScore}
            hotspotsCount={wardRiskHotspots}
            rainfallMm={weather.rainfall_mm}
            weatherCondition={weather.condition}
          />
        </section>

      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-10 pb-12">
        <section className="space-y-4">
          <ScenarioUploadCard
            latestRun={latestPipelineRun}
            isUploading={pipelineUploading}
            error={pipelineError}
            onUpload={onUploadScenario}
            apiBaseUrl={apiBaseUrl}
          />
        </section>

        {/* System Simulation Section */}
        <section className="space-y-4">
          <h2 className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em]">System Simulation</h2>
          <SimulationControls 
            isActive={simActive}
            rainfallPct={simRainfall}
            onToggle={onToggleSim}
            onRainfallChange={onValueChange}
            deltaCount={wardRiskHotspots}
          />
        </section>

        {/* Intelligence Summary Section */}
        <section className="space-y-4">
          <h2 className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em]">Intelligence Summary Distribution</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)] shadow-sm">
              <h3 className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-4 flex items-center gap-2">
                <BarChart3 className="w-3 h-3 text-blue-500" /> Sensed Critical Wards
              </h3>
              <RiskPieChart wards={wardProperties} />
            </div>
            <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)] shadow-sm flex flex-col items-center justify-between">
              <h3 className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-2 flex items-center gap-2">
                <ShieldCheck className="w-3 h-3 text-yellow-500" /> Readiness
              </h3>
              <ReadinessGauge score={cityScore} />
            </div>
          </div>
        </section>

        {/* Priority Action Queue Section */}
        <section className="space-y-4">
          <h2 className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em]">Priority Action Queue</h2>
          <PriorityAlerts 
            wards={wardProperties} 
            onViewDetails={onViewDetails} 
          />
        </section>

        {/* Sensed Locations Command Registry Section */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
              <LayoutGrid className="w-3 h-3" /> Monitored Registry
            </h2>
            <div className="flex items-center gap-2 px-2 py-1 bg-muted/10 border border-[var(--border-subtle)] focus-within:border-blue-500/50 rounded-md transition-all">
              <Search className="w-3 h-3 text-muted-foreground" />
              <input 
                type="text" 
                placeholder="SEARCH..." 
                className="bg-transparent border-none outline-none text-[9px] font-bold uppercase tracking-tight w-16 focus:w-24 transition-all text-[var(--text-primary)]"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
          
          <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl overflow-hidden flex flex-col max-h-[340px] shadow-sm shadow-black/20">
            <div className="p-3 border-b border-[var(--border-subtle)] bg-[var(--bg-elevated)]/30 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MapPin className="w-3 h-3 text-blue-500" />
                <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">
                  Monitored Zones
                </span>
              </div>
              <span className="text-[10px] font-mono text-blue-500 font-bold">{filteredWards.length} Regions</span>
            </div>
            <div className="overflow-y-auto custom-scrollbar p-1">
              {filteredWards.map(ward => (
                <button 
                  key={ward.ward_id}
                  suppressHydrationWarning
                  onClick={() => onViewDetails(ward)}
                  className="w-full flex items-center justify-between p-2.5 hover:bg-[var(--bg-elevated)] rounded-lg transition-all group text-left border border-transparent hover:border-[var(--border-subtle)] mb-0.5"
                >
                  <div className="flex items-center gap-3">
                    <div className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-40" style={{ backgroundColor: getRiskColor(ward.flood_risk) }}></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 shadow-[0_0_4px_rgba(0,0,0,0.5)]" style={{ backgroundColor: getRiskColor(ward.flood_risk) }}></span>
                    </div>
                    <div>
                      <p className="text-xs font-bold text-[var(--text-primary)] group-hover:text-blue-400 transition-colors leading-none">{ward.ward_name}</p>
                      <p className="text-[9px] text-[var(--text-muted)] font-mono mt-1 opacity-60 uppercase">ID: {ward.ward_id}</p>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span className="text-[10px] font-mono font-bold tracking-tighter" style={{ color: getRiskColor(ward.flood_risk) }}>
                      {Math.round(ward.flood_risk * 100)}%
                    </span>
                    <div className={`w-12 h-1 rounded-full bg-muted/30 overflow-hidden`}>
                      <div className="h-full transition-all duration-500" style={{ width: `${ward.flood_risk * 100}%`, backgroundColor: getRiskColor(ward.flood_risk) }} />
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </section>
      </div>
    </aside>
  );
}
