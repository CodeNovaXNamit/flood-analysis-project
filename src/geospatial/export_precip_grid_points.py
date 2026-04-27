"""
export_precip_grid_points.py
----------------------------
Export unique precipitation grid coordinates from the full precipitation CSV.

This creates a compact CSV you can load into QGIS as point features and use
for raster sampling, such as attaching elevation values from a DEM GeoTIFF.

Usage
-----
    python export_precip_grid_points.py ^
        --precip combined_precipitation_interpolated.csv ^
        --output precip_grid_points.csv
"""

import argparse
from pathlib import Path

import pandas as pd


def main():
    parser = argparse.ArgumentParser(
        description="Export unique precipitation grid points for QGIS."
    )
    parser.add_argument(
        "--precip",
        required=True,
        help="Path to precipitation CSV containing lon and lat columns.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV containing one row per unique grid point.",
    )
    parser.add_argument(
        "--decimals",
        type=int,
        default=6,
        help="Decimal places used before deduplicating coordinates (default: 6).",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  Export Precipitation Grid Points")
    print("=" * 60)
    print(f"\nReading precipitation CSV: {args.precip}")

    precip_df = pd.read_csv(args.precip, usecols=["lon", "lat"])
    total_rows = len(precip_df)

    precip_df["lon"] = pd.to_numeric(precip_df["lon"], errors="coerce").round(args.decimals)
    precip_df["lat"] = pd.to_numeric(precip_df["lat"], errors="coerce").round(args.decimals)
    precip_df = precip_df.dropna(subset=["lon", "lat"])

    grid_points = (
        precip_df[["lon", "lat"]]
        .drop_duplicates()
        .sort_values(["lon", "lat"])
        .reset_index(drop=True)
    )

    out_path = Path(args.output)
    grid_points.to_csv(out_path, index=False)

    print(f"Input rows         : {total_rows:,}")
    print(f"Unique grid points : {len(grid_points):,}")
    print(f"Lon range          : {grid_points['lon'].min():.6f} -> {grid_points['lon'].max():.6f}")
    print(f"Lat range          : {grid_points['lat'].min():.6f} -> {grid_points['lat'].max():.6f}")
    print(f"\nSaved -> {out_path}")
    print("\nSample output:")
    print(grid_points.head(5).to_string(index=False))
    print("=" * 60)


if __name__ == "__main__":
    main()
