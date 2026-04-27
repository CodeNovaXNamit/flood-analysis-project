'use client';

import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Zap, XCircle } from 'lucide-react';

interface SimulationControlsProps {
  isActive: boolean;
  rainfallPct: number;
  onToggle: () => void;
  onRainfallChange: (val: number) => void;
  deltaCount: number;
}

export default function SimulationControls({ 
  isActive, 
  rainfallPct, 
  onToggle, 
  onRainfallChange,
  deltaCount 
}: SimulationControlsProps) {
  return (
    <div className={`p-4 rounded-xl border transition-all duration-300 ${
      isActive 
        ? 'border-yellow-500/50 bg-yellow-500/5 shadow-[0_0_15px_rgba(245,158,11,0.1)]' 
        : 'border-[var(--border-subtle)] bg-[var(--bg-card)]'
    }`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <Zap className={`w-4 h-4 ${isActive ? 'text-yellow-500' : 'text-[var(--text-muted)]'}`} />
          Predictive Simulation
        </h3>
        <Button 
          variant={isActive ? "destructive" : "outline"} 
          size="sm"
          onClick={onToggle}
          className="h-8 text-xs font-bold uppercase tracking-tight"
        >
          {isActive ? (
            <><XCircle className="w-3 h-3 mr-1" /> Exit Simulation</>
          ) : "Enable Simulation"}
        </Button>
      </div>

      {isActive && (
        <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
          <div className="flex justify-between items-center text-xs">
            <span className="text-[var(--text-muted)]">Simulated Rainfall Intensity</span>
            <span className="font-mono text-yellow-500 font-bold">+{rainfallPct}%</span>
          </div>
          <Slider 
            value={[rainfallPct]} 
            onValueChange={(vals) => onRainfallChange(vals[0])}
            max={100} 
            step={5} 
            className="cursor-pointer"
          />
          <div className="flex items-center justify-between p-2 rounded bg-yellow-500/10 border border-yellow-500/20">
            <span className="text-[10px] text-yellow-200 uppercase font-bold">Risk Impact</span>
            <span className="text-xs font-mono font-bold text-yellow-500">
              {deltaCount} Wards Elevated Risk
            </span>
          </div>
        </div>
      )}

      {!isActive && (
        <p className="text-[11px] text-[var(--text-muted)] italic">
          Simulate cloudburst conditions to predict infrastructure stress.
        </p>
      )}
    </div>
  );
}
