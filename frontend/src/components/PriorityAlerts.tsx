'use client';

import { WardProperties } from '@/app/types/flood.types';
import { getRiskColor } from '@/app/utils/riskHelpers';
import { TrendingUp, TrendingDown, Minus, ChevronRight } from 'lucide-react';

interface PriorityAlertsProps {
  wards: WardProperties[];
  onViewDetails: (ward: WardProperties) => void;
}

export default function PriorityAlerts({ wards, onViewDetails }: PriorityAlertsProps) {
  const priorityWards = wards
    .filter(w => w.flood_risk > 0.66)
    .sort((a, b) => b.flood_risk - a.flood_risk)
    .slice(0, 3);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-[var(--text-muted)]">
          Priority Action Required
        </h3>
        <span className="px-2 py-0.5 bg-red-900/30 text-red-400 text-[10px] font-bold rounded">
          {priorityWards.length} HOTSPOTS
        </span>
      </div>
      
      {priorityWards.length === 0 ? (
        <div className="p-4 rounded-xl border border-dashed border-[var(--border-subtle)] text-center text-xs text-[var(--text-muted)]">
          No critical alerts in current conditions.
        </div>
      ) : (
        priorityWards.map(ward => (
          <div 
            key={ward.ward_id}
            className="group flex flex-col gap-2 p-3 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] hover:border-l-4 hover:border-l-red-500 hover:translate-x-1 hover:bg-[var(--bg-elevated)] transition-all duration-250 cursor-pointer shadow-sm"
            onClick={() => onViewDetails(ward)}
          >
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-bold text-[var(--text-primary)] group-hover:text-red-400 transition-colors">
                  {ward.ward_name}
                </h4>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded" style={{ backgroundColor: `${getRiskColor(ward.flood_risk)}20`, color: getRiskColor(ward.flood_risk) }}>
                    RISK {Math.round(ward.flood_risk * 100)}%
                  </span>
                  <div className="flex items-center gap-1 text-[10px] text-[var(--text-muted)]">
                    {ward.trend === 'increasing' ? <TrendingUp className="w-3 h-3 text-red-400" /> : 
                     ward.trend === 'decreasing' ? <TrendingDown className="w-3 h-3 text-green-400" /> : 
                     <Minus className="w-3 h-3 text-blue-400" />}
                    <span className="capitalize">{ward.trend}</span>
                  </div>
                </div>
              </div>
              <ChevronRight className="w-4 h-4 text-[var(--text-muted)] group-hover:text-white transform transition-transform group-hover:translate-x-1" />
            </div>
          </div>
        ))
      )}
    </div>
  );
}