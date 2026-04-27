'use client';

import { useState, useEffect, useRef } from 'react';
import { useTheme } from 'next-themes';
import { MapContainer, TileLayer, GeoJSON, Popup, useMapEvents, useMap, Marker, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { FeatureCollection, Polygon, Point, Feature } from 'geojson';
import { WardProperties } from '@/app/types/flood.types';
import { HotspotProperties } from '@/app/data/microHotspots';
import { getRiskColor, getRiskLabel } from '@/app/utils/riskHelpers';
import { Badge } from '@/components/ui/badge';
import { Layers, MapPinned, Monitor, ShieldCheck, Cpu, Target } from 'lucide-react';

type MapDisplayMode = 'ward' | 'hotspot';

interface FloodMapProps {
  geoJSON: FeatureCollection<Polygon, WardProperties>;
  hotspots?: FeatureCollection<Point, HotspotProperties>;
  isSimulationActive: boolean;
  onWardClick: (ward: WardProperties) => void;
  focusedWardId?: string | null;
  mapDisplayMode: MapDisplayMode;
  onMapDisplayModeChange: (mode: MapDisplayMode) => void;
}

const pinIcon = L.divIcon({
  className: 'custom-professional-pin',
  html: `
    <div class="professional-pin-wrapper">
      <div class="pin-pulse"></div>
      <div class="pin-shadow"></div>
      <svg width="30" height="38" viewBox="0 0 30 38" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M15 0C6.71573 0 0 6.71573 0 15C0 26.25 15 38 15 38C15 38 30 26.25 30 15C30 6.71573 23.2843 0 15 0Z" fill="#3B82F6"/>
        <path d="M15 2C7.8203 2 2 7.8203 2 15C2 25.125 15 35.5 15 35.5C15 35.5 28 25.125 28 15C28 7.8203 22.1797 2 15 2Z" fill="#2563EB"/>
        <circle cx="15" cy="15" r="5" fill="white"/>
      </svg>
    </div>
  `,
  iconSize: [30, 38],
  iconAnchor: [15, 38],
  popupAnchor: [0, -34],
});

function MapController({ 
  focusedWardId, 
  geoJsonLayer, 
  onCenterCalculated 
}: { 
  focusedWardId?: string | null, 
  geoJsonLayer: L.GeoJSON | null,
  onCenterCalculated: (latlng: L.LatLng | null) => void
}) {
  const map = useMap();

  useEffect(() => {
    if (focusedWardId && geoJsonLayer) {
      const layers = geoJsonLayer.getLayers();
      const targetLayer = layers.find((l: any) => l.feature.properties.ward_id === focusedWardId) as L.Polygon;
      
      if (targetLayer) {
        const center = targetLayer.getBounds().getCenter();
        onCenterCalculated(center);
        map.flyToBounds(targetLayer.getBounds(), { padding: [100, 100], duration: 1.5 });
      }
    } else {
      onCenterCalculated(null);
    }
  }, [focusedWardId, geoJsonLayer, map, onCenterCalculated]);

  return null;
}

function ZoomHandler({ onZoom }: { onZoom: (z: number) => void }) {
  const map = useMapEvents({
    zoomend: () => onZoom(map.getZoom()),
  });
  return null;
}

export default function FloodMap({
  geoJSON,
  hotspots,
  isSimulationActive,
  onWardClick,
  focusedWardId,
  mapDisplayMode,
  onMapDisplayModeChange,
}: FloodMapProps) {
  const [showDrainage, setShowDrainage] = useState(false);
  const [drainageData, setDrainageData] = useState<any>(null);
  const [isReady, setIsReady] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentZoom, setCurrentZoom] = useState(11);
  const [geoJsonLayer, setGeoJsonLayer] = useState<L.GeoJSON | null>(null);
  const [focusedCenter, setFocusedCenter] = useState<L.LatLng | null>(null);
  const [statusText, setStatusText] = useState('INITIALIZING GEOSPATIAL ENGINE');
  const [popCounter, setPopCounter] = useState(0);
  const [showFlash, setShowFlash] = useState(false);
  
  const { resolvedTheme } = useTheme();
  const audioRef = useRef<AudioContext | null>(null);

  const playBeep = () => {
    if (typeof window === 'undefined') return;
    try {
      if (!audioRef.current) audioRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      const osc = audioRef.current.createOscillator();
      const gain = audioRef.current.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(880, audioRef.current.currentTime);
      gain.gain.setValueAtTime(0.05, audioRef.current.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioRef.current.currentTime + 0.1);
      osc.connect(gain);
      gain.connect(audioRef.current.destination);
      osc.start();
      osc.stop(audioRef.current.currentTime + 0.1);
    } catch (e) {}
  };

  useEffect(() => {
    const statuses = [
      'INITIALIZING GEOSPATIAL ENGINE',
      'MAPPING WARD BOUNDARIES...',
      'CONNECTING LIVE TELEMETRY...',
      'RUNNING HYDRAULIC MODELS...',
      'SYSTEM READY'
    ];

    const timer = setInterval(() => {
      setProgress(p => {
        const next = p < 100 ? p + 1.2 : 100;
        const statusIdx = Math.min(Math.floor(next / 20), statuses.length - 1);
        if (statuses[statusIdx] !== statusText) {
          setStatusText(statuses[statusIdx]);
          playBeep();
        }
        return next;
      });
      setPopCounter(prev => Math.min(215300, prev + 2153));
    }, 25);

    const readyTimer = setTimeout(() => {
      setShowFlash(true);
      setTimeout(() => {
        setIsReady(true);
        setShowFlash(false);
      }, 400);
    }, 2500);

    return () => {
      clearInterval(timer);
      clearTimeout(readyTimer);
    };
  }, [statusText]);

  useEffect(() => {
    if (showDrainage && !drainageData) {
      fetch('/delhi_drainage.geojson')
        .then(r => r.json())
        .then(data => setDrainageData(data))
        .catch(err => console.error('Drainage fetch failed:', err));
    }
  }, [showDrainage, drainageData]);

  const onEachFeature = (feature: Feature<Polygon, WardProperties>, layer: L.Layer, index: number) => {
    if (currentZoom >= 12) {
      layer.bindTooltip(feature.properties.ward_name, {
        permanent: true,
        direction: 'center',
        className: 'ward-label-tooltip',
        opacity: 0.7
      });
    }

    const path = (layer as any)._path as SVGPathElement;
    if (path && !isReady) {
      path.style.opacity = '0';
      path.style.animation = `ward-entrance 0.5s ease-out forwards`;
      path.style.animationDelay = `${index * 30}ms`;
    }

    layer.on({
      mouseover: (e) => {
        const l = e.target;
        l.setStyle({ weight: 3, color: resolvedTheme === 'dark' ? '#ffffff' : '#000000', fillOpacity: 0.9 });
        l.bringToFront();
      },
      mouseout: (e) => {
        const l = e.target;
        l.setStyle(wardStyle(feature));
      },
      click: (e) => {
        L.DomEvent.stopPropagation(e);
        onWardClick(feature.properties);
      },
    });
  };

  const wardStyle = (feature?: any) => {
    const risk = feature?.properties?.flood_risk || 0;
    const isFocused = focusedWardId === feature?.properties?.ward_id;
    return {
      fillColor: getRiskColor(risk),
      weight: isFocused ? 3 : 1.5,
      opacity: 1,
      color: isFocused ? (resolvedTheme === 'dark' ? '#ffffff' : '#000000') : '#000000',
      fillOpacity: isFocused ? 0.95 : 0.75,
    };
  };

  const focusedWardData = focusedWardId 
    ? geoJSON.features.find(f => f.properties.ward_id === focusedWardId)?.properties 
    : null;

  return (
    <div className={`relative h-full w-full bg-[var(--bg-base)] overflow-hidden ${showFlash ? 'animate-[system-flash_0.4s_ease-out]' : ''}`}>
      {!isReady && (
        <div className="absolute inset-0 z-[10001] bg-[#060D1A] flex flex-col items-center justify-center hex-grid scanlines">
          {/* Corner Brackets */}
          <div className="absolute top-10 left-10 w-12 h-12 border-t-2 border-l-2 border-cyan-500 animate-[bracket-tl_0.5s_ease-out_forwards]" />
          <div className="absolute top-10 right-10 w-12 h-12 border-t-2 border-r-2 border-cyan-500 animate-[bracket-tr_0.5s_ease-out_forwards]" />
          <div className="absolute bottom-10 left-10 w-12 h-12 border-b-2 border-l-2 border-cyan-500 animate-[bracket-bl_0.5s_ease-out_forwards]" />
          <div className="absolute bottom-10 right-10 w-12 h-12 border-b-2 border-r-2 border-cyan-500 animate-[bracket-br_0.5s_ease-out_forwards]" />

          {/* Telemetry Overlay */}
          <div className="absolute top-12 left-12 font-mono text-[10px] text-cyan-500/60 space-y-1">
            <div className="flex items-center gap-2"><Cpu className="w-3 h-3" /> COORD: 28.6139° N, 77.2090° E</div>
            <div>SECTOR: DELHI_NCT_ALPHA</div>
          </div>

          <div className="absolute bottom-12 right-12 font-mono text-[8px] text-cyan-500/40 text-right">
            <div>VERSION: v2.4.1-STABLE</div>
            <div className="font-bold">CLASSIFICATION: RESTRICTED</div>
          </div>

          {/* Background Number Pulse */}
          <div className="absolute inset-0 flex items-center justify-center opacity-[0.03] pointer-events-none overflow-hidden select-none">
            <div className="text-[20vw] font-mono font-black text-cyan-500 tracking-tighter">
              {popCounter.toLocaleString().padStart(6, '0')}
            </div>
          </div>

          {/* Main Radar */}
          <div className="relative w-72 h-72 mb-12">
            <div className="absolute inset-0 rounded-full border border-cyan-500/20" />
            <div className="absolute inset-0 rounded-full border border-cyan-500/10 scale-75" />
            <div className="absolute inset-0 rounded-full border border-cyan-500/5 scale-50" />
            <div className="absolute inset-0 animate-radar rounded-full border-2 border-cyan-500/40" />
            <div className="absolute inset-0 animate-scan border-r-2 border-cyan-400 rounded-full" 
                 style={{ background: 'conic-gradient(from 0deg, transparent 0%, rgba(6, 182, 212, 0.25) 100%)' }} />
            <div className="absolute inset-0 flex items-center justify-center">
              <Monitor className="w-8 h-8 text-cyan-500/40 animate-pulse" />
            </div>
          </div>
          
          <div className="text-center space-y-8 w-full max-w-sm px-12">
            <div className="flex flex-col gap-2">
              <div className="text-cyan-400 font-mono text-sm tracking-[0.3em] font-bold h-6 animate-glitch key={statusText}">
                {statusText}
              </div>
              <div className="text-cyan-500/40 font-mono text-[9px] uppercase tracking-widest">
                System Hash: {Math.random().toString(36).substring(7).toUpperCase()}
              </div>
            </div>
            
            <div className="relative w-full h-1.5 bg-cyan-950/50 rounded-full overflow-hidden border border-cyan-900/30">
              <div className="h-full bg-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.8)] transition-all duration-300 ease-out relative" 
                   style={{ width: `${progress}%` }}>
                <div className="absolute right-0 top-1/2 -translate-y-1/2 w-4 h-4 bg-cyan-400 rounded-full blur-md opacity-80" />
              </div>
            </div>
          </div>
        </div>
      )}

      <div className={`h-full w-full transition-all duration-1000 ${isReady ? 'scale-100 opacity-100' : 'scale-95 opacity-0'}`}>
        <MapContainer 
          center={[28.6139, 77.2090]} 
          zoom={11} 
          minZoom={10}
          maxZoom={14}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={true}
          zoomControl={false}
        >
          <MapController 
            focusedWardId={focusedWardId} 
            geoJsonLayer={geoJsonLayer} 
            onCenterCalculated={setFocusedCenter}
          />
          <ZoomHandler onZoom={setCurrentZoom} />
          <TileLayer
            key={resolvedTheme}
            url={resolvedTheme === 'light' 
              ? "https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png"
              : "https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png"
            }
            attribution='&copy; CARTO'
          />
          {mapDisplayMode === 'ward' && (
            <GeoJSON 
              key={`${JSON.stringify(geoJSON)}-${isSimulationActive ? 'sim' : 'base'}-${currentZoom}`}
              data={geoJSON} 
              style={wardStyle}
              onEachFeature={(feature, layer) => {
                const index = geoJSON.features.indexOf(feature as any);
                onEachFeature(feature as any, layer, index);
              }}
              ref={(ref) => setGeoJsonLayer(ref)}
            />
          )}

          {mapDisplayMode === 'hotspot' && hotspots?.features.map((feature, idx) => {
            const risk = feature.properties.hotspot_risk;
            const priority = risk > 0.75 ? 'CRITICAL' : risk > 0.5 ? 'HIGH' : 'MEDIUM';
            return (
              <CircleMarker
                key={`hotspot-${idx}`}
                center={[feature.geometry.coordinates[1], feature.geometry.coordinates[0]]}
                radius={currentZoom > 12 ? 6 : 4}
                pathOptions={{
                  fillColor: getRiskColor(risk),
                  color: priority === 'CRITICAL' ? '#fff' : 'transparent',
                  weight: 1,
                  fillOpacity: 0.8,
                }}
              >
                <Popup className="flood-popup">
                  <div className="p-3 space-y-2 min-w-[150px]">
                    <div className="flex items-center gap-2 border-b border-[var(--border-subtle)] pb-2 mb-1">
                      <Target className="w-3.5 h-3.5 text-blue-500" />
                      <span className="text-[10px] font-bold uppercase text-[var(--text-muted)]">Micro-Hotspot Analysis</span>
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between items-center">
                        <span className="text-[9px] text-[var(--text-muted)] uppercase">Risk Index</span>
                        <span className="font-mono text-xs font-bold" style={{ color: getRiskColor(risk) }}>{(risk * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-[9px] text-[var(--text-muted)] uppercase">Deployment</span>
                        <Badge className={`text-[8px] h-4 px-1.5 font-bold ${
                          priority === 'CRITICAL' ? 'bg-red-500 text-white' : 
                          priority === 'HIGH' ? 'bg-orange-500 text-black' : 'bg-yellow-500 text-black'
                        }`}>
                          {priority}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}

          {focusedCenter && focusedWardData && (
            <Marker position={focusedCenter} icon={pinIcon} key={`pin-${focusedWardId}`} zIndexOffset={1000}>
              <Popup className="flood-popup" closeButton={false} autoPan={false}>
                <div className="p-4 space-y-2 min-w-[180px]">
                  <h3 className="font-bold text-sm border-b border-[var(--border-subtle)] pb-2 text-[var(--text-primary)]">
                    {focusedWardData.ward_name}
                  </h3>
                  <div className="grid grid-cols-2 gap-2 pt-1">
                    <div className="flex flex-col">
                      <span className="text-[10px] text-[var(--text-muted)] uppercase font-bold">Risk Index</span>
                      <span className="font-mono text-sm font-bold" style={{ color: getRiskColor(focusedWardData.flood_risk) }}>
                        {focusedWardData.flood_risk.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[10px] text-[var(--text-muted)] uppercase font-bold">Severity</span>
                      <Badge variant="outline" className="text-[9px] h-4 py-0 px-1.5 font-bold uppercase mt-0.5" style={{ color: '#000', backgroundColor: getRiskColor(focusedWardData.flood_risk), borderColor: 'transparent' }}>
                        {getRiskLabel(focusedWardData.flood_risk)}
                      </Badge>
                    </div>
                  </div>
                </div>
              </Popup>
            </Marker>
          )}

          <div className="absolute top-6 right-6 z-[1000] p-3 bg-[var(--bg-card)]/90 backdrop-blur-md border border-[var(--border-strong)] rounded-xl shadow-2xl space-y-3 min-w-[220px]">
            <h4 className="text-[10px] uppercase tracking-[0.2em] font-bold text-[var(--text-muted)] border-b border-[var(--border-subtle)] pb-2 flex items-center gap-2">
              <MapPinned className="w-3 h-3" /> Map View
            </h4>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => onMapDisplayModeChange('ward')}
                className={`rounded-lg border px-3 py-2 text-[11px] font-bold uppercase tracking-wide transition-colors ${
                  mapDisplayMode === 'ward'
                    ? 'border-blue-500 bg-blue-500 text-white'
                    : 'border-[var(--border-subtle)] bg-[var(--bg-elevated)] text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                }`}
              >
                Ward Map
              </button>
              <button
                type="button"
                onClick={() => onMapDisplayModeChange('hotspot')}
                className={`rounded-lg border px-3 py-2 text-[11px] font-bold uppercase tracking-wide transition-colors ${
                  mapDisplayMode === 'hotspot'
                    ? 'border-blue-500 bg-blue-500 text-white'
                    : 'border-[var(--border-subtle)] bg-[var(--bg-elevated)] text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                }`}
              >
                Dot Map
              </button>
            </div>
          </div>

          <div className="absolute bottom-10 left-6 z-[1000] p-5 bg-[var(--bg-card)]/90 backdrop-blur-md border border-[var(--border-strong)] rounded-xl shadow-2xl space-y-4 min-w-[220px]">
            <h4 className="text-[10px] uppercase tracking-[0.2em] font-bold text-[var(--text-muted)] border-b border-[var(--border-subtle)] pb-2 flex items-center gap-2">
              <Layers className="w-3 h-3" /> Mission Zonation
            </h4>
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-xs">
                <div className="w-5 h-5 rounded border border-black" style={{ backgroundColor: '#4ADE80' }} />
                <div className="flex flex-col">
                  <span className="text-[var(--text-primary)] font-bold">Safe Zone</span>
                  <span className="text-[9px] text-[var(--text-muted)]">Readiness &gt; 70%</span>
                </div>
              </div>
               <div className="flex items-center gap-3 text-xs">
                <div className="w-5 h-5 rounded border border-black" style={{ backgroundColor: '#FDE047' }} />
                <div className="flex flex-col">
                  <span className="text-[var(--text-primary)] font-bold">Cautionary Zone</span>
                  <span className="text-[9px] text-[var(--text-muted)]">Readiness 40 - 70%</span>
                </div>
              </div>
               <div className="flex items-center gap-3 text-xs">
                <div className="w-5 h-5 rounded border border-black" style={{ backgroundColor: '#EF4444' }} />
                <div className="flex flex-col">
                  <span className="text-[var(--text-primary)] font-bold">Critical Vulnerability</span>
                  <span className="text-[9px] text-[var(--text-muted)]">Immediate Deployment</span>
                </div>
              </div>
            </div>
          </div>
        </MapContainer>
      </div>
    </div>
  );
}
