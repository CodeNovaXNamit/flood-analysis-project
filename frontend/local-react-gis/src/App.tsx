import { useEffect, useMemo, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { Feature } from 'geojson';
import type { SourceWardProperties, WardDataset, WardGeometry, WardMetrics } from './types';
import { createWardMetrics, getRiskColor, getRiskLabel } from './utils/risk';

type ViewMode = 'risk' | 'readiness';

function App() {
  const mapRef = useRef<L.Map | null>(null);
  const geoJsonLayerRef = useRef<L.GeoJSON | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);
  const mapElementRef = useRef<HTMLDivElement | null>(null);
  const [dataset, setDataset] = useState<WardDataset | null>(null);
  const [selectedWardId, setSelectedWardId] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [viewMode, setViewMode] = useState<ViewMode>('risk');
  const [showTiles, setShowTiles] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDataset = async () => {
      try {
        const response = await fetch('/data/Delhi_Wards_with_rebalanced_risk.geojson');
        if (!response.ok) {
          throw new Error('Unable to load ward GeoJSON.');
        }
        const data = (await response.json()) as WardDataset;
        setDataset(data);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : 'Unknown load error');
      } finally {
        setLoading(false);
      }
    };

    void loadDataset();
  }, []);

  const wardMetrics = useMemo(() => {
    if (!dataset) {
      return [];
    }

    return dataset.features.map((feature) => createWardMetrics(feature));
  }, [dataset]);

  const metricMap = useMemo(() => {
    return new Map(wardMetrics.map((metric) => [metric.wardId, metric]));
  }, [wardMetrics]);

  const filteredWards = useMemo(() => {
    const needle = search.trim().toLowerCase();
    if (!needle) {
      return wardMetrics;
    }

    return wardMetrics.filter((ward) => {
      return (
        ward.wardName.toLowerCase().includes(needle) ||
        ward.wardId.toLowerCase().includes(needle)
      );
    });
  }, [search, wardMetrics]);

  const selectedWard = selectedWardId ? metricMap.get(selectedWardId) ?? null : null;

  const cityStats = useMemo(() => {
    if (wardMetrics.length === 0) {
      return {
        averageRisk: 0,
        averageReadiness: 0,
        criticalCount: 0,
        totalPopulation: 0,
      };
    }

    const totalRisk = wardMetrics.reduce((sum, ward) => sum + ward.floodRisk, 0);
    const totalReadiness = wardMetrics.reduce((sum, ward) => sum + ward.readinessScore, 0);
    const totalPopulation = wardMetrics.reduce((sum, ward) => sum + ward.affectedPopulation, 0);

    return {
      averageRisk: totalRisk / wardMetrics.length,
      averageReadiness: Math.round(totalReadiness / wardMetrics.length),
      criticalCount: wardMetrics.filter((ward) => ward.floodRisk >= 0.8).length,
      totalPopulation,
    };
  }, [wardMetrics]);

  useEffect(() => {
    if (!mapElementRef.current || mapRef.current) {
      return;
    }

    const map = L.map(mapElementRef.current, {
      zoomControl: true,
      attributionControl: false,
    }).setView([28.6139, 77.209], 10);

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current) {
      return;
    }

    if (showTiles) {
      if (!tileLayerRef.current) {
        tileLayerRef.current = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; OpenStreetMap contributors',
          maxZoom: 18,
        }).addTo(mapRef.current);
      }
      return;
    }

    if (tileLayerRef.current) {
      tileLayerRef.current.remove();
      tileLayerRef.current = null;
    }
  }, [showTiles]);

  useEffect(() => {
    if (!mapRef.current || !dataset) {
      return;
    }

    geoJsonLayerRef.current?.remove();

    const createStyle = (feature?: Feature) => {
      const sourceFeature = feature as Feature<WardGeometry, SourceWardProperties> | undefined;
      const wardId = sourceFeature?.properties.Ward_No;
      const metrics = wardId ? metricMap.get(wardId) : null;
      const isSelected = selectedWardId === wardId;
      const fillValue =
        viewMode === 'risk'
          ? metrics?.floodRisk ?? 0
          : 1 - (metrics?.readinessScore ?? 0) / 100;

      return {
        color: isSelected ? '#f8fafc' : '#0f172a',
        weight: isSelected ? 2.5 : 1,
        fillOpacity: isSelected ? 0.92 : 0.76,
        fillColor: getRiskColor(fillValue),
      };
    };

    const layer = L.geoJSON(dataset as GeoJSON.GeoJsonObject, {
      style: createStyle,
      onEachFeature: (feature, leafletLayer) => {
        const sourceFeature = feature as Feature<WardGeometry, SourceWardProperties>;
        const metrics = createWardMetrics(sourceFeature);
        leafletLayer.bindPopup(`
          <div style="min-width: 190px; font-family: Arial, sans-serif;">
            <div style="font-weight: 700; margin-bottom: 8px;">${metrics.wardName}</div>
            <div>Ward ID: ${metrics.wardId}</div>
            <div>Flood Risk: ${(metrics.floodRisk * 100).toFixed(1)}%</div>
            <div>Readiness: ${metrics.readinessScore}%</div>
            <div>Drainage Capacity: ${metrics.drainageCapacity}%</div>
          </div>
        `);

        leafletLayer.on({
          click: () => setSelectedWardId(metrics.wardId),
          mouseover: () => {
            if ('setStyle' in leafletLayer) {
              (leafletLayer as L.Path).setStyle({
                weight: 2.5,
                color: '#f8fafc',
                fillOpacity: 0.92,
              });
            }
          },
          mouseout: () => {
            geoJsonLayerRef.current?.resetStyle(leafletLayer);
          },
        });
      },
    });

    layer.addTo(mapRef.current);
    geoJsonLayerRef.current = layer;

    if (selectedWardId) {
      const target = layer
        .getLayers()
        .find((item) => (item as L.Layer & { feature?: Feature<WardGeometry, SourceWardProperties> }).feature?.properties.Ward_No === selectedWardId);

      if (target && 'getBounds' in target) {
        mapRef.current.fitBounds((target as L.Polygon).getBounds(), {
          padding: [24, 24],
          maxZoom: 13,
        });
      }
    } else {
      mapRef.current.fitBounds(layer.getBounds(), { padding: [20, 20] });
    }
  }, [dataset, metricMap, selectedWardId, viewMode]);

  const handleWardClick = (wardId: string) => {
    setSelectedWardId(wardId);
  };

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="panel hero">
          <div className="eyebrow">Local React GIS Copy</div>
          <h1>Delhi Flood Intelligence</h1>
          <p>
            Local-only React dashboard with integrated GIS ward choropleth, search,
            ward inspection, and readiness metrics.
          </p>
        </div>

        <div className="panel stats-grid">
          <div className="stat-card">
            <span>Average Risk</span>
            <strong>{(cityStats.averageRisk * 100).toFixed(1)}%</strong>
          </div>
          <div className="stat-card">
            <span>Readiness</span>
            <strong>{cityStats.averageReadiness}%</strong>
          </div>
          <div className="stat-card">
            <span>Critical Wards</span>
            <strong>{cityStats.criticalCount}</strong>
          </div>
          <div className="stat-card">
            <span>Exposed Population</span>
            <strong>{cityStats.totalPopulation.toLocaleString()}</strong>
          </div>
        </div>

        <div className="panel controls">
          <label className="field">
            <span>Search ward</span>
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Ward name or number"
            />
          </label>

          <div className="toggle-row">
            <button
              className={viewMode === 'risk' ? 'active' : ''}
              onClick={() => setViewMode('risk')}
            >
              Risk View
            </button>
            <button
              className={viewMode === 'readiness' ? 'active' : ''}
              onClick={() => setViewMode('readiness')}
            >
              Readiness View
            </button>
          </div>

          <label className="checkbox">
            <input
              type="checkbox"
              checked={showTiles}
              onChange={(event) => setShowTiles(event.target.checked)}
            />
            <span>Show OpenStreetMap basemap</span>
          </label>
        </div>

        <div className="panel selection">
          <div className="panel-title">Ward Detail</div>
          {selectedWard ? (
            <WardDetail ward={selectedWard} />
          ) : (
            <p className="muted">Select a ward from the map or the list.</p>
          )}
        </div>

        <div className="panel ward-list">
          <div className="panel-title">Ward Index</div>
          <div className="list-scroll">
            {filteredWards.slice(0, 80).map((ward) => (
              <button
                key={ward.wardId}
                className={`ward-row ${selectedWardId === ward.wardId ? 'selected' : ''}`}
                onClick={() => handleWardClick(ward.wardId)}
              >
                <div>
                  <strong>{ward.wardName}</strong>
                  <span>{ward.wardId}</span>
                </div>
                <span
                  className="risk-pill"
                  style={{ backgroundColor: getRiskColor(ward.floodRisk) }}
                >
                  {getRiskLabel(ward.floodRisk)}
                </span>
              </button>
            ))}
          </div>
        </div>
      </aside>

      <main className="map-stage">
        <div className="map-header">
          <div>
            <div className="eyebrow">Integrated GIS System</div>
            <h2>Ward-level flood risk map</h2>
          </div>
          <div className="legend">
            <span><i style={{ background: '#4ade80' }} />Low</span>
            <span><i style={{ background: '#facc15' }} />Moderate</span>
            <span><i style={{ background: '#ef4444' }} />Critical</span>
          </div>
        </div>

        <div className="map-frame">
          {loading && <div className="overlay">Loading GIS dataset...</div>}
          {error && <div className="overlay error">{error}</div>}
          <div ref={mapElementRef} className="map-canvas" />
        </div>
      </main>
    </div>
  );
}

function WardDetail({ ward }: { ward: WardMetrics }) {
  return (
    <div className="detail-grid">
      <div>
        <span>Name</span>
        <strong>{ward.wardName}</strong>
      </div>
      <div>
        <span>Ward ID</span>
        <strong>{ward.wardId}</strong>
      </div>
      <div>
        <span>Flood Risk</span>
        <strong>{(ward.floodRisk * 100).toFixed(1)}%</strong>
      </div>
      <div>
        <span>Severity</span>
        <strong>{getRiskLabel(ward.floodRisk)}</strong>
      </div>
      <div>
        <span>Readiness</span>
        <strong>{ward.readinessScore}%</strong>
      </div>
      <div>
        <span>Drainage Capacity</span>
        <strong>{ward.drainageCapacity}%</strong>
      </div>
      <div>
        <span>Elevation</span>
        <strong>{ward.elevationM} m</strong>
      </div>
      <div>
        <span>Population at Risk</span>
        <strong>{ward.affectedPopulation.toLocaleString()}</strong>
      </div>
      <div>
        <span>Trend</span>
        <strong className={`trend ${ward.trend}`}>{ward.trend}</strong>
      </div>
    </div>
  );
}

export default App;
