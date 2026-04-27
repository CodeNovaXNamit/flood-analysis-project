'use client';

import { useState, useMemo } from 'react';
import { Search, ChevronRight } from 'lucide-react';
import { WardProperties } from '@/app/types/flood.types';
import { getRiskColor } from '@/app/utils/riskHelpers';
import { Input } from '@/components/ui/input';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { ScrollArea } from '@/components/ui/scroll-area';

interface WardSearchProps {
  wards: WardProperties[];
  onSelect: (ward: WardProperties) => void;
}

export default function WardSearch({ wards, onSelect }: WardSearchProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');

  const filteredWards = useMemo(() => {
    if (!query) return wards.slice(0, 10);
    return wards
      .filter((w) => 
        w.ward_name.toLowerCase().includes(query.toLowerCase()) ||
        w.ward_id.toLowerCase().includes(query.toLowerCase())
      )
      .slice(0, 15);
  }, [query, wards]);

  return (
    <div className="relative w-full max-w-[320px]">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <div className="relative group cursor-pointer">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)] group-hover:text-blue-400 transition-colors" />
            <Input
              placeholder="Search ward or location..."
              className="pl-9 h-11 bg-[var(--bg-card)]/95 backdrop-blur-md border-[var(--border-strong)] focus:border-blue-500/50 transition-all text-sm font-semibold shadow-2xl"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                if (!open) setOpen(true);
              }}
              onFocus={() => setOpen(true)}
            />
          </div>
        </PopoverTrigger>
        <PopoverContent 
          className="w-[320px] p-0 bg-[var(--bg-card)] border-[var(--border-strong)] shadow-2xl z-[10001]" 
          align="start"
          onOpenAutoFocus={(e) => e.preventDefault()}
        >
          <div className="p-2 border-b border-[var(--border-subtle)] bg-[var(--bg-elevated)]/50">
            <p className="text-[10px] uppercase font-bold text-[var(--text-muted)] tracking-widest px-2">
              Sensed Locations ({wards.length})
            </p>
          </div>
          <ScrollArea className="h-[300px]">
            {filteredWards.length === 0 ? (
              <div className="p-4 text-center text-xs text-[var(--text-muted)]">
                No matching wards found.
              </div>
            ) : (
              <div className="p-1">
                {filteredWards.map((ward) => (
                  <button
                    key={ward.ward_id}
                    suppressHydrationWarning
                    className="w-full flex items-center justify-between p-2 hover:bg-[var(--bg-elevated)] rounded-md transition-colors group text-left"
                    onClick={() => {
                      onSelect(ward);
                      setOpen(false);
                      setQuery('');
                    }}
                  >
                    <div className="flex items-center gap-3">
                      <div 
                        className="w-1.5 h-1.5 rounded-full" 
                        style={{ backgroundColor: getRiskColor(ward.flood_risk) }} 
                      />
                      <div>
                        <p className="text-xs font-bold text-[var(--text-primary)] group-hover:text-blue-400">
                          {ward.ward_name}
                        </p>
                        <p className="text-[9px] text-[var(--text-muted)] uppercase font-mono">
                          ID: {ward.ward_id}
                        </p>
                      </div>
                    </div>
                    <ChevronRight className="w-3 h-3 text-[var(--text-muted)] opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
            )}
          </ScrollArea>
        </PopoverContent>
      </Popover>
    </div>
  );
}
