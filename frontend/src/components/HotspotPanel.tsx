'use client';

import { useEffect, useState } from 'react';
import { WardProperties } from '@/app/types/flood.types';
import { getRiskColor, getRiskLabel, getRiskLevel, formatPopulation, getExplainabilityText } from '@/app/utils/riskHelpers';
import { X, TrendingUp, TrendingDown, Minus, Droplets, MapPin, Activity, Info, AlertCircle, Users, ShieldCheck, Wrench } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, registerables } from 'chart.js';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

ChartJS.register(...registerables);

interface HotspotPanelProps {
  ward: WardProperties | null;
  onClose: () => void;
}

export default function HotspotPanel({ ward, onClose }: HotspotPanelProps) {
  const [syncTime, setSyncTime] = useState('--:--:--');

  useEffect(() => {
    setSyncTime(new Date().toISOString().split('T')[1].slice(0, 8));
  }, []);

  if (!ward) return null;

  const readinessScore = Math.round((1 - ward.flood_risk) * 100);
  const trendColor = ward.trend === 'increasing' ? '#EF4444' : ward.trend === 'decreasing' ? '#22C55E' : '#3B82F6';
  const riskLevel = getRiskLevel(ward.flood_risk);

  const actionPlan = {
    low: {
      prevention: [
        'Keep drains and street inlets clear.',
        'Check pumps before heavy rainfall.',
        'Share local flood alerts early.',
      ],
      response: [
        'Inspect waterlogging points quickly.',
        'Clear minor blockages the same day.',
        'Monitor roads and low-lying lanes.',
      ],
    },
    medium: {
      prevention: [
        'Pre-clean drains and desilt choke points.',
        'Place sandbags near repeated flood spots.',
        'Keep emergency contacts and shelters ready.',
      ],
      response: [
        'Deploy drainage teams to blocked zones.',
        'Restrict traffic on waterlogged roads.',
        'Move exposed residents and assets early.',
      ],
    },
    high: {
      prevention: [
        'Run urgent drain desilting and pump checks.',
        'Pre-position rescue teams and barricades.',
        'Warn residents in low-lying pockets now.',
      ],
      response: [
        'Start pumping and emergency water removal.',
        'Close unsafe roads and power-risk areas.',
        'Evacuate vulnerable households if needed.',
      ],
    },
  }[riskLevel];

  const lineData = {
    labels: ['D-6', 'D-5', 'D-4', 'D-3', 'D-2', 'D-1', 'Now'],
    datasets: [
      {
        fill: 'start',
        label: 'Risk Index',
        data: ward.risk_history,
        borderColor: getRiskColor(ward.flood_risk),
        backgroundColor: `${getRiskColor(ward.flood_risk)}15`,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: getRiskColor(ward.flood_risk),
        pointBorderWidth: 2,
        pointBorderColor: '#fff',
      },
    ],
  };

  const lineOptions = {
    plugins: { 
      legend: { display: false },
      tooltip: {
        backgroundColor: '#0F1E35',
        titleFont: { size: 10 },
        bodyFont: { family: 'IBM Plex Mono', size: 12 },
        padding: 10,
        cornerRadius: 4,
        displayColors: false,
      }
    },
    scales: {
      y: { 
        min: 0, 
        max: 1, 
        grid: { color: 'rgba(255,255,255,0.05)' }, 
        ticks: { color: '#6B8EB3', font: { family: 'IBM Plex Mono', size: 9 } } 
      },
      x: { 
        grid: { display: false }, 
        ticks: { color: '#6B8EB3', font: { size: 9 } } 
      },
    },
    responsive: true,
    maintainAspectRatio: false,
  };

  return (
    <div className="absolute right-0 top-0 h-full w-full max-w-[480px] bg-[var(--bg-surface)] border-l border-[var(--border-strong)] z-[60] shadow-2xl animate-in slide-in-from-right duration-300 overflow-y-auto custom-scrollbar flex flex-col">
      {/* Header */}
      <div className="sticky top-0 bg-[var(--bg-surface)]/90 backdrop-blur-md z-20 px-8 py-6 border-b border-[var(--border-subtle)] flex justify-between items-start">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight">{ward.ward_name}</h2>
            <Badge variant="outline" className="text-[10px] h-5 py-0 px-2 font-mono" style={{ borderColor: getRiskColor(ward.flood_risk), color: getRiskColor(ward.flood_risk) }}>
              ID: {ward.ward_id}
            </Badge>
          </div>
          <div className="flex items-center gap-4">
             <div className="flex items-center gap-1.5">
               <div className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: getRiskColor(ward.flood_risk) }} />
               <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">{getRiskLabel(ward.flood_risk)} Severity Zone</span>
             </div>
            <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase" style={{ color: trendColor }}>
              {ward.trend === 'increasing' ? <TrendingUp className="w-3.5 h-3.5" /> : ward.trend === 'decreasing' ? <TrendingDown className="w-3.5 h-3.5" /> : <Minus className="w-3.5 h-3.5" />}
              {ward.trend} Trend
            </div>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full hover:bg-muted shrink-0 h-10 w-10">
          <X className="w-6 h-6 text-muted-foreground" />
        </Button>
      </div>

      <div className="p-8 space-y-10">
        {/* Risk Intelligence */}
        <section className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
              <Activity className="w-3.5 h-3.5 text-blue-500" /> Geospatial Risk Analysis
            </h3>
            <span className="text-[9px] font-mono text-muted-foreground opacity-60 uppercase">Telemetry: Active</span>
          </div>
          <div className="h-56 w-full p-4 bg-muted/10 rounded-2xl border border-[var(--border-subtle)]">
            <Line data={lineData} options={lineOptions} />
          </div>
        </section>

        {/* Impact Matrix */}
        <section className="grid grid-cols-2 gap-4">
          <div className="p-5 rounded-2xl border border-[var(--border-subtle)] bg-muted/5 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:scale-110 transition-transform">
              <Users className="w-8 h-8" />
            </div>
            <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider mb-2">Exposure Index</p>
            <p className="text-3xl font-mono font-bold">{formatPopulation(ward.population_affected)}</p>
            <p className="text-[9px] text-muted-foreground mt-1 uppercase font-semibold">Affected Residents</p>
          </div>
          <div className="p-5 rounded-2xl border border-[var(--border-subtle)] bg-muted/5 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:scale-110 transition-transform">
              <MapPin className="w-8 h-8" />
            </div>
            <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider mb-2">Hypsometry</p>
            <p className="text-3xl font-mono font-bold">{ward.elevation_m}m</p>
            <p className="text-[9px] text-muted-foreground mt-1 uppercase font-semibold">Height above MSL</p>
          </div>
        </section>

        {/* Infrastructure Load */}
        <section className="space-y-4">
           <h3 className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
            <Droplets className="w-3.5 h-3.5 text-cyan-500" /> Infrastructure Integrity
          </h3>
          <div className="space-y-6 p-6 rounded-2xl border bg-muted/5">
            <div className="space-y-3">
              <div className="flex justify-between text-[11px] font-bold uppercase tracking-tight">
                <span className="text-muted-foreground">Drainage Efficiency</span>
                <span className="text-blue-500 font-mono">{Math.round(ward.drainage_capacity * 100)}%</span>
              </div>
              <div className="h-2.5 w-full bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full transition-all duration-1000" style={{ width: `${ward.drainage_capacity * 100}%` }} />
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between text-[11px] font-bold uppercase tracking-tight">
                <span className="text-muted-foreground">Hydraulic Load</span>
                <span className="font-mono" style={{ color: getRiskColor(ward.flood_risk) }}>{Math.round(ward.flood_risk * 100)}%</span>
              </div>
              <div className="h-2.5 w-full bg-muted rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all duration-1000" style={{ width: `${ward.flood_risk * 100}%`, backgroundColor: getRiskColor(ward.flood_risk) }} />
              </div>
            </div>
            
            {ward.flood_risk > ward.drainage_capacity && (
              <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
                <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <p className="text-[11px] font-bold text-red-600 dark:text-red-400 uppercase tracking-tight">Drainage Criticality Detected</p>
                  <p className="text-[10px] text-red-500/80 leading-relaxed">Present rainfall intensity exceeds infrastructure design parameters. Immediate maintenance or catchment intervention required.</p>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Readiness Profile */}
        <section className="p-6 rounded-2xl border bg-muted/5 flex items-center gap-8 group">
          <div className="flex flex-col items-center justify-center bg-muted/20 rounded-xl p-4 w-24 h-24 shrink-0 transition-colors group-hover:bg-muted/30">
            <div className="text-4xl font-mono font-bold tracking-tighter" style={{ color: getRiskColor(1 - readinessScore/100) }}>
              {readinessScore}
            </div>
            <span className="text-[8px] uppercase tracking-widest font-black text-muted-foreground mt-1">Score</span>
          </div>
          <div className="space-y-2">
            <div className="text-sm font-bold flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${readinessScore >= 70 ? 'bg-green-500' : 'bg-red-500'}`} />
              {readinessScore >= 70 ? 'Adequate Response Readiness' : readinessScore >= 40 ? 'Moderate Prep. Required' : 'Critical Readiness Deficit'}
            </div>
            <p className="text-[11px] text-muted-foreground leading-relaxed italic">
              "{getExplainabilityText(readinessScore)}"
            </p>
          </div>
        </section>

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
              <ShieldCheck className="w-3.5 h-3.5 text-green-500" /> Action Window
            </h3>
            <Badge variant="outline" className="text-[10px] h-5 py-0 px-2 font-mono" style={{ borderColor: getRiskColor(ward.flood_risk), color: getRiskColor(ward.flood_risk) }}>
              {getRiskLabel(ward.flood_risk)} Risk
            </Badge>
          </div>
          <div className="grid grid-cols-1 gap-4">
            <div className="rounded-2xl border border-[var(--border-subtle)] bg-muted/5 p-5">
              <div className="mb-3 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-green-500" />
                <h4 className="text-[11px] font-bold uppercase tracking-[0.15em] text-[var(--text-primary)]">
                  Prevent
                </h4>
              </div>
              <div className="space-y-2">
                {actionPlan.prevention.map((item) => (
                  <div key={item} className="flex items-start gap-2 text-[11px] text-muted-foreground leading-relaxed">
                    <div className="mt-1.5 h-1.5 w-1.5 rounded-full bg-green-500 shrink-0" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-[var(--border-subtle)] bg-muted/5 p-5">
              <div className="mb-3 flex items-center gap-2">
                <Wrench className="w-4 h-4 text-orange-500" />
                <h4 className="text-[11px] font-bold uppercase tracking-[0.15em] text-[var(--text-primary)]">
                  Fix Situation
                </h4>
              </div>
              <div className="space-y-2">
                {actionPlan.response.map((item) => (
                  <div key={item} className="flex items-start gap-2 text-[11px] text-muted-foreground leading-relaxed">
                    <div className="mt-1.5 h-1.5 w-1.5 rounded-full bg-orange-500 shrink-0" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <div className="pt-4 grid grid-cols-1 gap-3">
          <Button className="w-full bg-[var(--accent-blue)] hover:bg-blue-600 text-white font-bold text-[11px] uppercase tracking-[0.15em] h-14 rounded-2xl shadow-xl shadow-blue-500/10">
            Dispatch Emergency Response Team
          </Button>
          <Button variant="outline" className="w-full font-bold text-[11px] uppercase tracking-[0.15em] h-14 rounded-2xl border-[var(--border-strong)]">
            Log Maintenance Ticket
          </Button>
        </div>
      </div>

      <div className="p-8 border-t bg-muted/10 mt-auto">
        <div className="flex items-center justify-between opacity-60">
          <div className="flex items-center gap-2 text-[9px] font-bold uppercase tracking-widest text-muted-foreground">
            <Info className="w-3 h-3" /> System Verified
          </div>
          <span className="text-[9px] font-mono text-muted-foreground">UTC Sync: {syncTime}</span>
        </div>
      </div>
    </div>
  );
}
