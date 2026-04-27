'use client';

import { useState, useCallback } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { 
  BrainCircuit, 
  Loader2, 
  AlertTriangle, 
  Zap,
  ChevronRight,
  ShieldAlert,
  Droplets,
  Waves,
  Clock
} from 'lucide-react';
import { getMitigationAdvice, MitigationOutput } from '@/ai/flows/ai-mitigation-advisor-flow';

interface AIAdvisorDialogProps {
  cityReadiness: number;
  hotspotsCount: number;
  rainfallMm: number;
  weatherCondition: string;
}

export default function AIAdvisorDialog({ 
  cityReadiness, 
  hotspotsCount, 
  rainfallMm, 
  weatherCondition 
}: AIAdvisorDialogProps) {
  const [advice, setAdvice] = useState<MitigationOutput | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateAdvice = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getMitigationAdvice({
        cityReadiness,
        hotspotsCount,
        rainfallMm,
        weatherCondition,
      });
      setAdvice(result);
    } catch (err) {
      console.error(err);
      setError('Intelligence Core handshake failed. Check connectivity.');
    } finally {
      setLoading(false);
    }
  }, [cityReadiness, hotspotsCount, rainfallMm, weatherCondition]);

  const handleManualRefresh = () => {
    setAdvice(null); // Clear to force visual loader reset
    // Small timeout to ensure the clear-state re-render happens before the new fetch starts
    setTimeout(() => {
      generateAdvice();
    }, 150);
  };

  return (
    <Dialog onOpenChange={(open) => { if (open && !advice) generateAdvice(); }}>
      <DialogTrigger asChild>
        <Button 
          variant="outline" 
          className="w-full h-12 bg-blue-500/10 border-blue-500/30 text-blue-400 hover:bg-blue-500/20 hover:text-blue-300 gap-2 font-bold text-[10px] uppercase tracking-widest transition-all hover:shadow-[0_0_15px_rgba(59,130,246,0.3)]"
        >
          <BrainCircuit className="w-4 h-4" />
          Aqua-Sentinel Command
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl bg-[#060D1A] border-[#1E3A5F] text-white p-0 overflow-hidden shadow-[0_0_50px_rgba(59,130,246,0.2)]">
        <DialogHeader className="p-6 border-b border-[#1E3A5F] bg-blue-950/20">
          <DialogTitle className="flex items-center gap-3 text-blue-400 font-mono tracking-tighter text-xl">
            <BrainCircuit className="w-6 h-6 animate-pulse" />
            AQUA-SENTINEL: STRATEGIC OVERWATCH
          </DialogTitle>
        </DialogHeader>

        <div className="p-8 space-y-8 max-h-[70vh] overflow-y-auto custom-scrollbar hex-grid">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20 space-y-4">
              <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
              <div className="text-center">
                <p className="text-blue-400 font-mono text-xs animate-pulse tracking-[0.2em] uppercase">Calculating Hydrological Vectors...</p>
                <p className="text-[10px] text-slate-500 font-mono mt-2">QUERYING OPEN-METEO GLOBAL FLOOD MODEL</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
              <AlertTriangle className="w-12 h-12 text-red-500" />
              <p className="text-red-400 font-mono text-sm max-w-xs">{error}</p>
              <Button onClick={generateAdvice} variant="link" className="text-blue-400 uppercase text-[10px] font-bold">Retry Telemetry Handshake</Button>
            </div>
          ) : advice ? (
            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              
              {/* Telemetry Strip */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-500/5 border border-blue-500/20 p-4 rounded-xl flex items-center gap-4">
                  <div className="p-2 bg-blue-500/20 rounded-lg">
                    <Waves className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest leading-none mb-1">River Discharge</p>
                    <p className="text-xl font-mono font-bold text-blue-400">{advice.riverDischarge.toFixed(1)} <span className="text-xs">m³/s</span></p>
                  </div>
                </div>
                <div className="bg-blue-500/5 border border-blue-500/20 p-4 rounded-xl flex items-center gap-4">
                  <div className="p-2 bg-blue-500/20 rounded-lg">
                    <Droplets className="w-5 h-5 text-cyan-400" />
                  </div>
                  <div>
                    <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest leading-none mb-1">Catchment Status</p>
                    <p className="text-xl font-mono font-bold text-cyan-400">{cityReadiness}% <span className="text-xs">Operational</span></p>
                  </div>
                </div>
              </div>

              {/* Summary */}
              <section className="bg-blue-500/5 border border-blue-500/20 p-6 rounded-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                  <Zap className="w-12 h-12 text-blue-400" />
                </div>
                <h3 className="text-[10px] font-bold text-blue-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                  <ChevronRight className="w-3 h-3" /> Tactical Overview
                </h3>
                <p className="text-sm leading-relaxed text-slate-300 italic font-medium font-mono">
                  "{advice.strategicSummary}"
                </p>
              </section>

              {/* Actions */}
              <section className="space-y-4">
                <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                  <ShieldAlert className="w-3.5 h-3.5 text-orange-500" /> Strategic Deployments
                </h3>
                <div className="grid gap-3">
                  {advice.actions.map((action, i) => (
                    <div key={i} className="bg-slate-900/50 border border-slate-800 p-4 rounded-xl flex gap-4 group hover:border-blue-500/40 transition-colors">
                      <div className={`mt-1 shrink-0`}>
                        {action.priority === 'CRITICAL' ? (
                          <div className="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]" />
                        ) : action.priority === 'HIGH' ? (
                          <div className="w-2 h-2 rounded-full bg-orange-500" />
                        ) : (
                          <div className="w-2 h-2 rounded-full bg-yellow-500" />
                        )}
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className={`text-[9px] font-black tracking-tighter ${
                            action.priority === 'CRITICAL' ? 'text-red-500' : 'text-slate-400'
                          }`}>[{action.priority}]</span>
                          <p className="text-sm font-bold text-slate-200">{action.task}</p>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed font-mono">{action.rationale}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* Projection */}
              <section className="border-t border-[#1E3A5F] pt-6">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-cyan-500/10 rounded-lg">
                    <Zap className="w-5 h-5 text-cyan-400" />
                  </div>
                  <div>
                    <h4 className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest mb-1">Predictive Vector</h4>
                    <p className="text-xs text-slate-400 leading-relaxed italic">{advice.riskProjection}</p>
                  </div>
                </div>
              </section>
            </div>
          ) : null}
        </div>

        <div className="p-6 border-t border-[#1E3A5F] bg-blue-950/10 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <p className="text-[9px] text-slate-500 font-mono uppercase tracking-widest">Source: Open-Meteo GFM-V2.1</p>
            {advice && (
              <div className="flex items-center gap-1 text-[9px] text-blue-500/60 font-mono">
                <Clock className="w-2.5 h-2.5" />
                LAST SYNC: {advice.generatedAt}
              </div>
            )}
          </div>
          {(advice || error) && (
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={handleManualRefresh} 
              disabled={loading}
              className="h-8 text-[9px] font-bold text-blue-400 hover:text-blue-300 disabled:opacity-50 border border-blue-500/20"
            >
              {loading ? (
                <><Loader2 className="w-3 h-3 animate-spin mr-2" /> RE-CALCULATING...</>
              ) : (
                'REFRESH HYDRAULIC MODELS'
              )}
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
