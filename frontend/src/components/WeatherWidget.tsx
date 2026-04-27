'use client';

import { useState, useEffect } from 'react';
import { WeatherData } from '@/app/types/flood.types';
import { CloudRain, Thermometer, Droplets, AlertTriangle, Wind, ArrowDown, ArrowUp, Timer } from 'lucide-react';

interface WeatherWidgetProps {
  weather: WeatherData;
  lastSync: Date;
}

const REFRESH_INTERVAL_MS = 120000; // 2 minutes

export default function WeatherWidget({ weather, lastSync }: WeatherWidgetProps) {
  const [secondsUntilRefresh, setSecondsUntilRefresh] = useState(REFRESH_INTERVAL_MS / 1000);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    setSecondsUntilRefresh(REFRESH_INTERVAL_MS / 1000);
  }, [lastSync]);

  useEffect(() => {
    const timer = setInterval(() => {
      setSecondsUntilRefresh((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatCountdown = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const isSevere = weather.rainfall_mm > 15;

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-2 p-4 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] shadow-sm relative overflow-hidden group shimmer-bg">
        <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-2 mb-1">
          <div className="flex items-center gap-2">
            <div className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </div>
            <span className="text-[9px] font-mono font-bold text-[var(--text-primary)] uppercase tracking-widest">
              Live Telemetry Stream
            </span>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-[8px] font-mono text-[var(--text-muted)] bg-[var(--bg-base)] px-1.5 py-0.5 rounded border border-[var(--border-subtle)]">
              <Timer className="w-2.5 h-2.5 text-[var(--accent-blue)]" />
              <span>NEXT SYNC IN {formatCountdown(secondsUntilRefresh)}</span>
            </div>
            <span className="text-[8px] font-mono text-[var(--text-muted)] opacity-60">
              SYNCED: {mounted ? lastSync.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--:--'}
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 group-hover:scale-110 transition-transform">
              <CloudRain className="w-4 h-4 text-blue-400" />
              <span className="font-mono text-sm font-bold">{weather.rainfall_mm}mm</span>
            </div>
            
            <div className="flex flex-col">
              <div className="flex items-center gap-2 group-hover:scale-110 transition-transform">
                <Thermometer className="w-4 h-4 text-orange-400" />
                <span className="font-mono text-sm font-bold">{weather.temperature_c}°C</span>
              </div>
              <div className="flex items-center gap-2 text-[10px] text-[var(--text-muted)] mt-0.5">
                <span className="flex items-center gap-0.5"><ArrowDown className="w-2 h-2 text-blue-400" />{weather.temp_min_c}°</span>
                <span className="flex items-center gap-0.5"><ArrowUp className="w-2 h-2 text-red-400" />{weather.temp_max_c}°</span>
              </div>
            </div>

            <div className="flex items-center gap-2 group-hover:scale-110 transition-transform">
              <Droplets className="w-4 h-4 text-blue-300" />
              <span className="font-mono text-sm font-bold">{weather.humidity_pct}%</span>
            </div>
          </div>
          
          <div className="text-sm font-medium text-[var(--text-primary)] border-l border-[var(--border-subtle)] pl-4 flex items-center gap-2 max-w-[120px] truncate">
            <Wind className="w-3 h-3 text-[var(--text-muted)] shrink-0" />
            <span className="truncate">{weather.condition}</span>
          </div>
        </div>
      </div>
      
      {isSevere && (
        <div className="flex items-center gap-3 px-4 py-3 bg-red-900/30 border border-red-500/50 rounded-xl text-red-400 text-xs font-bold animate-pulse">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <div className="flex flex-col">
            <span className="uppercase tracking-tighter text-[10px]">Critical Precipitation Detected</span>
            <span className="text-[9px] opacity-80 font-normal">Real-time flood risk threshold exceeded in catchment basins.</span>
          </div>
        </div>
      )}
    </div>
  );
}
