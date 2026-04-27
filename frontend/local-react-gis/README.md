# Local React GIS Copy

This is a separate local React frontend copy of the Delhi flood dashboard.

## Features

- React + Vite local app
- Integrated GIS map using Leaflet
- Ward choropleth from `Delhi_Wards_with_rebalanced_risk.geojson`
- Ward search, selection, popup details, and city summary metrics
- Optional OpenStreetMap basemap toggle

## Run Locally

1. Open a terminal in this folder:

```bash
cd local-react-gis
```

2. Install dependencies:

```bash
npm install
```

3. Start the local dev server:

```bash
npm run dev
```

4. Open:

```text
http://localhost:5174
```

## Build

```bash
npm run build
```

## GIS Data

The app reads the local GeoJSON file from:

`public/data/Delhi_Wards_with_rebalanced_risk.geojson`
