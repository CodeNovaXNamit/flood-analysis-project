'use client';

import { useState, useEffect } from 'react';
import { useTheme } from 'next-themes';
import { 
  Waves, 
  ChevronDown, 
  Info, 
  Code2, 
  Cpu, 
  Database, 
  Layers,
  Moon,
  Sun,
  ShieldCheck
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from '@/components/ui/button';

interface TopBarProps {
  cityScore: number;
  isSimulating: boolean;
}

export default function TopBar({ cityScore, isSimulating }: TopBarProps) {
  const [isInfoOpen, setIsInfoOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('tech');
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const getReadinessClass = (s: number) => {
    if (s >= 70) return 'bg-green-500/10 text-green-500 border-green-500/30';
    if (s >= 40) return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/30';
    return 'bg-red-500/10 text-red-500 border-red-500/30';
  };

  const openDoc = (tab: string) => {
    setActiveTab(tab);
    setIsInfoOpen(true);
  };

  return (
    <header className="h-[60px] w-full flex items-center justify-between px-6 bg-[var(--bg-surface)] border-b border-[var(--border-subtle)] shadow-sm relative z-[10000] shrink-0">
      <div className="flex items-center gap-8">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-[var(--accent-blue)] rounded-lg shadow-lg">
            <Waves className="w-5 h-5 text-white" />
          </div>
          <div className="flex flex-col">
            <h1 className="font-bold text-[var(--text-primary)] text-base tracking-tight leading-none uppercase">
              Predictive Hydrology Engine
            </h1>
            <p className="text-[10px] text-[var(--text-muted)] font-bold tracking-[0.15em] mt-1 uppercase">
              Pre-Monsoon Strategy Command
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 mr-2">
          {isSimulating && (
            <div className="flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/30 px-3 py-1.5 rounded-md">
              <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
              <span className="text-[10px] font-bold text-yellow-600 dark:text-yellow-500 uppercase tracking-tight">PREDICTIVE SCENARIO ACTIVE</span>
            </div>
          )}
          <div className={`px-4 py-1.5 rounded-md border text-[11px] font-bold font-mono ${getReadinessClass(cityScore)} shadow-sm flex items-center gap-2 transition-all duration-500 glow-readiness`}>
            <ShieldCheck className="w-3 h-3" />
            PRE-MONSOON READINESS {cityScore}%
          </div>
        </div>

        <div className="flex items-center border-l border-[var(--border-subtle)] pl-4 gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="text-[var(--text-muted)] hover:text-[var(--accent-blue)] h-9 w-9"
            onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
          >
            {mounted && resolvedTheme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="text-[var(--text-muted)] hover:text-[var(--text-primary)] h-9 px-3 gap-2">
                <Info className="w-4 h-4" />
                <span className="text-xs font-semibold">Project Spec</span>
                <ChevronDown className="w-3 h-3 opacity-50" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 z-[10001]">
              <DropdownMenuLabel className="text-[10px] uppercase text-muted-foreground tracking-widest">Hydrology Core</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="cursor-pointer" onClick={() => openDoc('tech')}>
                <Code2 className="w-4 h-4 mr-2" />
                <span>Actionable Intel</span>
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer" onClick={() => openDoc('technology')}>
                <Cpu className="w-4 h-4 mr-2" />
                <span>Micro-Hotspot Algorithm</span>
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer" onClick={() => openDoc('resources')}>
                <Database className="w-4 h-4 mr-2" />
                <span>Terrain & GIS Data</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <Dialog open={isInfoOpen} onOpenChange={setIsInfoOpen}>
        <DialogContent className="max-w-2xl p-0 gap-0 overflow-hidden shadow-2xl z-[10001]">
          <DialogHeader className="p-6 border-b bg-muted/30">
            <DialogTitle className="text-xl flex items-center gap-3">
              <div className="p-2 bg-[var(--accent-blue)] rounded-lg">
                <Layers className="w-5 h-5 text-white" />
              </div>
              Hackathon Outcome: Urban Flooding Solution
            </DialogTitle>
          </DialogHeader>
          
          <div className="p-8 space-y-6">
            <section className="space-y-2">
              <h4 className="text-sm font-bold uppercase tracking-tight text-blue-500">Actionable Intelligence at Scale</h4>
              <p className="text-xs text-muted-foreground leading-relaxed">
                This platform converts fragmented hydrological telemetry, terrain elevation, and historical rainfall into a unified GIS command interface. By identifying 2,500+ micro-hotspots, it enables proactive resource deployment before severe weather events.
              </p>
            </section>
            <section className="space-y-2">
              <h4 className="text-sm font-bold uppercase tracking-tight text-blue-500">Readiness Scoring</h4>
              <p className="text-xs text-muted-foreground leading-relaxed">
                The ward-level <strong>Pre-Monsoon Readiness Score</strong> is calculated by cross-referencing drainage capacity against simulated heavy rainfall scenarios, providing city administrators with a clear roadmap for maintenance and emergency prep.
              </p>
            </section>
          </div>
          
          <div className="p-6 border-t bg-muted/30 text-center">
            <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest">
              Submission Version v1.0.4 • Domain 1: Urban Solutions
            </p>
          </div>
        </DialogContent>
      </Dialog>
    </header>
  );
}
