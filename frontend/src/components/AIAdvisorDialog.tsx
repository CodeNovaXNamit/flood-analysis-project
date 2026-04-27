'use client';

import { useState, useCallback } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import {
  BrainCircuit,
  Loader2,
  AlertTriangle,
  ChevronRight,
  ShieldAlert,
  MapPinned,
  Clock,
  Sparkles,
  Radar,
} from 'lucide-react';

import { PipelineRun } from '@/app/types/pipeline.types';
import { getMitigationAdvice, MitigationOutput } from '@/ai/flows/ai-mitigation-advisor-flow';

interface AdvisorWardInput {
  wardId: string;
  wardName: string;
  risk: number;
  populationAffected: number;
  trend: 'increasing' | 'stable' | 'decreasing';
}

interface AIAdvisorDialogProps {
  cityReadiness: number;
  hotspotsCount: number;
  rainfallMm: number;
  weatherCondition: string;
  avgRiskPercent: number;
  totalPopulationAtRisk: number;
  topWards: AdvisorWardInput[];
  latestPipelineRun: PipelineRun | null;
}

function getEscalationClass(level: MitigationOutput['escalationLevel']) {
  switch (level) {
    case 'SEVERE':
      return 'text-red-400 border-red-500/30 bg-red-500/10';
    case 'ELEVATED':
      return 'text-orange-300 border-orange-500/30 bg-orange-500/10';
    case 'GUARDED':
      return 'text-yellow-300 border-yellow-500/30 bg-yellow-500/10';
    default:
      return 'text-emerald-300 border-emerald-500/30 bg-emerald-500/10';
  }
}

function mapLatestRun(latestPipelineRun: PipelineRun | null) {
  if (!latestPipelineRun) return null;
  return {
    status: latestPipelineRun.status,
    latestPredictionDate: latestPipelineRun.latest_prediction_date,
    outputRows: latestPipelineRun.output_rows,
    maxRisk: latestPipelineRun.summary?.max_risk ?? null,
    meanRisk: latestPipelineRun.summary?.mean_risk ?? null,
    highRiskPoints: latestPipelineRun.summary?.high_risk_points ?? null,
    mediumRiskPoints: latestPipelineRun.summary?.medium_risk_points ?? null,
    lowRiskPoints: latestPipelineRun.summary?.low_risk_points ?? null,
  };
}

export default function AIAdvisorDialog({
  cityReadiness,
  hotspotsCount,
  rainfallMm,
  weatherCondition,
  avgRiskPercent,
  totalPopulationAtRisk,
  topWards,
  latestPipelineRun,
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
        avgRiskPercent,
        totalPopulationAtRisk,
        topWards,
        latestRun: mapLatestRun(latestPipelineRun),
      });
      setAdvice(result);
    } catch (err) {
      console.error(err);
      setError('Gemini advisory request failed. Check AI configuration and connectivity.');
    } finally {
      setLoading(false);
    }
  }, [
    avgRiskPercent,
    cityReadiness,
    hotspotsCount,
    latestPipelineRun,
    rainfallMm,
    topWards,
    totalPopulationAtRisk,
    weatherCondition,
  ]);

  const handleManualRefresh = () => {
    setAdvice(null);
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
          Gemini Flood Copilot
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl bg-[#060D1A] border-[#1E3A5F] text-white p-0 overflow-hidden shadow-[0_0_50px_rgba(59,130,246,0.2)]">
        <DialogHeader className="p-6 border-b border-[#1E3A5F] bg-blue-950/20">
          <DialogTitle className="flex items-center gap-3 text-blue-400 font-mono tracking-tighter text-xl">
            <BrainCircuit className="w-6 h-6 animate-pulse" />
            GEMINI FLOOD RESPONSE COPILOT
          </DialogTitle>
        </DialogHeader>

        <div className="p-8 space-y-8 max-h-[70vh] overflow-y-auto custom-scrollbar hex-grid">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20 space-y-4">
              <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
              <div className="text-center">
                <p className="text-blue-400 font-mono text-xs animate-pulse tracking-[0.2em] uppercase">Generating Gemini Advisory...</p>
                <p className="text-[10px] text-slate-500 font-mono mt-2">Grounding model output on live flood telemetry and latest pipeline results</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
              <AlertTriangle className="w-12 h-12 text-red-500" />
              <p className="text-red-400 font-mono text-sm max-w-xs">{error}</p>
              <Button onClick={generateAdvice} variant="link" className="text-blue-400 uppercase text-[10px] font-bold">Retry Advisory Request</Button>
            </div>
          ) : advice ? (
            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="grid grid-cols-3 gap-4">
                <div className={`border p-4 rounded-xl ${getEscalationClass(advice.escalationLevel)}`}>
                  <p className="text-[9px] font-bold uppercase tracking-widest opacity-75">Escalation</p>
                  <p className="mt-2 text-xl font-mono font-bold">{advice.escalationLevel}</p>
                </div>
                <div className="bg-blue-500/5 border border-blue-500/20 p-4 rounded-xl">
                  <p className="text-[9px] font-bold uppercase tracking-widest text-slate-500">Model Source</p>
                  <p className="mt-2 text-lg font-mono font-bold text-blue-400">{advice.source}</p>
                  <p className="text-[10px] text-slate-500 mt-1">{advice.modelUsed}</p>
                </div>
                <div className="bg-blue-500/5 border border-blue-500/20 p-4 rounded-xl">
                  <p className="text-[9px] font-bold uppercase tracking-widest text-slate-500">Telemetry</p>
                  <p className="mt-2 text-lg font-mono font-bold text-cyan-400">{hotspotsCount} hotspots</p>
                  <p className="text-[10px] text-slate-500 mt-1">{rainfallMm.toFixed(1)} mm rain</p>
                </div>
              </div>

              <section className="bg-blue-500/5 border border-blue-500/20 p-6 rounded-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                  <Sparkles className="w-12 h-12 text-blue-400" />
                </div>
                <h3 className="text-[10px] font-bold text-blue-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                  <ChevronRight className="w-3 h-3" /> Strategic Summary
                </h3>
                <p className="text-sm leading-relaxed text-slate-300 italic font-medium">
                  "{advice.strategicSummary}"
                </p>
              </section>

              <section className="space-y-4">
                <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                  <ShieldAlert className="w-3.5 h-3.5 text-orange-500" /> Recommended Actions
                </h3>
                <div className="grid gap-3">
                  {advice.actions.map((action, i) => (
                    <div key={i} className="bg-slate-900/50 border border-slate-800 p-4 rounded-xl flex gap-4 group hover:border-blue-500/40 transition-colors">
                      <div className="mt-1 shrink-0">
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
                        <p className="text-xs text-slate-400 leading-relaxed">{action.rationale}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              <section className="grid grid-cols-2 gap-4">
                <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 p-4">
                  <h4 className="text-[10px] font-bold uppercase tracking-widest text-cyan-400 mb-3 flex items-center gap-2">
                    <MapPinned className="w-3.5 h-3.5" /> Ward Focus
                  </h4>
                  <div className="space-y-3">
                    {advice.wardFocus.map((ward, index) => (
                      <div key={`${ward.wardName}-${index}`}>
                        <p className="text-sm font-semibold text-slate-200">{ward.wardName}</p>
                        <p className="text-xs text-slate-400 leading-relaxed">{ward.reason}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 p-4">
                  <h4 className="text-[10px] font-bold uppercase tracking-widest text-cyan-400 mb-3 flex items-center gap-2">
                    <Radar className="w-3.5 h-3.5" /> Projection
                  </h4>
                  <p className="text-xs text-slate-300 leading-relaxed">{advice.riskProjection}</p>
                  <div className="mt-4 border-t border-blue-500/10 pt-4">
                    <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-2">Public Advisory</p>
                    <p className="text-xs text-slate-400 leading-relaxed">{advice.publicAdvisory}</p>
                  </div>
                </div>
              </section>

              <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
                <h4 className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-2">Grounding Notes</h4>
                <p className="text-xs text-slate-400 leading-relaxed">{advice.groundingNotes}</p>
              </section>
            </div>
          ) : null}
        </div>

        <div className="p-6 border-t border-[#1E3A5F] bg-blue-950/10 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <p className="text-[9px] text-slate-500 font-mono uppercase tracking-widest">
              Source: {advice?.source === 'Gemini' ? 'Google Gemini via Genkit' : 'Local fallback advisory'}
            </p>
            {advice && (
              <div className="flex items-center gap-1 text-[9px] text-blue-500/60 font-mono">
                <Clock className="w-2.5 h-2.5" />
                GENERATED: {new Date(advice.generatedAt).toLocaleTimeString()}
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
                <><Loader2 className="w-3 h-3 animate-spin mr-2" /> RE-GENERATING...</>
              ) : (
                'REFRESH GEMINI ADVICE'
              )}
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
