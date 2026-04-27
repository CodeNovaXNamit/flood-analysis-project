import { FeatureCollection, Point, Feature } from 'geojson';
import hotspotData from './data_risk_frontend.json';

export interface HotspotProperties {
  lat: number;
  lon: number;
  hotspot_risk: number;
  deployment_priority?: 'CRITICAL' | 'HIGH' | 'MEDIUM';
}

type RawHotspotProperties = {
  lat?: number;
  lon?: number;
  risk?: number;
  hotspot_risk?: number;
};

type RawHotspotFeature = Feature<Point, RawHotspotProperties>;

const rawFeatureCollection = hotspotData as FeatureCollection<Point, RawHotspotProperties>;

const normalizeFeature = (feature: RawHotspotFeature): Feature<Point, HotspotProperties> => {
  const [lon = feature.properties?.lon ?? 0, lat = feature.properties?.lat ?? 0] = feature.geometry.coordinates;
  const hotspotRisk = feature.properties?.hotspot_risk ?? feature.properties?.risk ?? 0;

  return {
    type: 'Feature',
    geometry: {
      type: 'Point',
      coordinates: [lon, lat],
    },
    properties: {
      lat,
      lon,
      hotspot_risk: hotspotRisk,
    },
  };
};

export const microHotspotsData: FeatureCollection<Point, HotspotProperties> = {
  type: 'FeatureCollection',
  features: rawFeatureCollection.features.map((feature) => normalizeFeature(feature as RawHotspotFeature)),
};
