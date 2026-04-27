'use client';

import { FormEvent, useState } from 'react';
import { Upload, Database, Download, Activity } from 'lucide-react';

import { PipelineRun } from '@/app/types/pipeline.types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface ScenarioUploadCardProps {
  latestRun: PipelineRun | null;
  isUploading: boolean;
  error: string | null;
  onUpload: (file: File, scenarioName: string) => Promise<void>;
  apiBaseUrl: string;
}

export default function ScenarioUploadCard({
  latestRun,
  isUploading,
  error,
  onUpload,
  apiBaseUrl,
}: ScenarioUploadCardProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [scenarioName, setScenarioName] = useState('');

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedFile) return;
    const resolvedName = scenarioName.trim() || selectedFile.name.replace(/\.csv$/i, '');
    try {
      await onUpload(selectedFile, resolvedName);
    } catch {
      return;
    }
    setSelectedFile(null);
    setScenarioName('');
    event.currentTarget.reset();
  };

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em]">Scenario Pipeline</h2>
        <span className="text-[8px] bg-emerald-500/10 text-emerald-500 px-1.5 py-0.5 rounded font-black uppercase tracking-tight">
          Live API
        </span>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4">
        <div className="space-y-2">
          <label className="text-[10px] font-bold uppercase tracking-[0.15em] text-muted-foreground">Scenario Name</label>
          <Input
            value={scenarioName}
            onChange={(event) => setScenarioName(event.target.value)}
            placeholder="delhi-weekly-upload"
            className="border-[var(--border-subtle)] bg-[var(--bg-elevated)] text-sm"
          />
        </div>

        <div className="space-y-2">
          <label className="text-[10px] font-bold uppercase tracking-[0.15em] text-muted-foreground">Rainfall CSV</label>
          <Input
            type="file"
            accept=".csv"
            onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
            className="border-[var(--border-subtle)] bg-[var(--bg-elevated)] text-sm file:mr-3 file:rounded-md file:border-0 file:bg-[var(--accent-blue)] file:px-3 file:py-2 file:text-white"
          />
          <p className="text-[10px] text-[var(--text-muted)]">
            Upload a CSV shaped like `sample_new_data.csv` with `date`, `lat`, `lon`, `rainfall`.
          </p>
        </div>

        <Button
          type="submit"
          disabled={!selectedFile || isUploading}
          className="w-full h-11 rounded-xl bg-[var(--accent-blue)] hover:bg-blue-600 text-white font-bold uppercase tracking-[0.15em] text-[11px]"
        >
          <Upload className="mr-2 h-4 w-4" />
          {isUploading ? 'Running Pipeline...' : 'Upload And Predict'}
        </Button>

        {error && (
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-[10px] text-red-300">
            {error}
          </div>
        )}
      </form>

      {latestRun && (
        <div className="space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-xs font-bold text-[var(--text-primary)]">{latestRun.scenario_name}</p>
              <p className="mt-1 text-[10px] uppercase tracking-[0.15em] text-[var(--text-muted)]">
                Latest prediction date: {latestRun.latest_prediction_date ?? 'n/a'}
              </p>
            </div>
            <a
              href={`${apiBaseUrl}${latestRun.download_url}`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 rounded-lg border border-[var(--border-subtle)] px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-[0.12em] text-[var(--text-primary)]"
            >
              <Download className="h-3 w-3" />
              CSV
            </a>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="rounded-xl bg-[var(--bg-elevated)] p-3">
              <div className="flex items-center gap-2 text-[9px] font-bold uppercase tracking-[0.12em] text-muted-foreground">
                <Database className="h-3 w-3 text-blue-500" />
                Input
              </div>
              <p className="mt-2 font-mono text-lg font-bold text-[var(--text-primary)]">{latestRun.input_rows ?? 0}</p>
            </div>
            <div className="rounded-xl bg-[var(--bg-elevated)] p-3">
              <div className="flex items-center gap-2 text-[9px] font-bold uppercase tracking-[0.12em] text-muted-foreground">
                <Activity className="h-3 w-3 text-yellow-500" />
                Grid
              </div>
              <p className="mt-2 font-mono text-lg font-bold text-[var(--text-primary)]">{latestRun.interpolated_rows ?? 0}</p>
            </div>
            <div className="rounded-xl bg-[var(--bg-elevated)] p-3">
              <div className="flex items-center gap-2 text-[9px] font-bold uppercase tracking-[0.12em] text-muted-foreground">
                <Upload className="h-3 w-3 text-red-500" />
                Output
              </div>
              <p className="mt-2 font-mono text-lg font-bold text-[var(--text-primary)]">{latestRun.output_rows ?? 0}</p>
            </div>
          </div>

          {latestRun.summary && (
            <div className="rounded-xl bg-[var(--bg-elevated)] p-3">
              <div className="flex items-center justify-between text-[10px] uppercase tracking-[0.12em] text-muted-foreground">
                <span>Risk snapshot</span>
                <span>Max {(latestRun.summary.max_risk * 100).toFixed(1)}%</span>
              </div>
              <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                <div>
                  <p className="text-[9px] uppercase text-muted-foreground">High</p>
                  <p className="font-mono text-base font-bold text-red-400">{latestRun.summary.high_risk_points}</p>
                </div>
                <div>
                  <p className="text-[9px] uppercase text-muted-foreground">Medium</p>
                  <p className="font-mono text-base font-bold text-yellow-300">{latestRun.summary.medium_risk_points}</p>
                </div>
                <div>
                  <p className="text-[9px] uppercase text-muted-foreground">Low</p>
                  <p className="font-mono text-base font-bold text-emerald-400">{latestRun.summary.low_risk_points}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
