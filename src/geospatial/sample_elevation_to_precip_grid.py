"""
sample_elevation_to_precip_grid.py
---------------------------------
Sample elevation values from a raster onto the precipitation grid.

Important:
The existing precipitation CSV uses column names `lon` and `lat`, but the
stored values appear geographically swapped. This script keeps the original
column names for merge compatibility while using corrected x/y geometry for
raster sampling:

  x = precip_df["lat"]   # true longitude
  y = precip_df["lon"]   # true latitude

Usage
-----
    python sample_elevation_to_precip_grid.py ^
        --precip precip_grid_points.csv ^
        --elevation elevation\\elevation.tif ^
        --output elevation\\elevation_on_precip_grid.csv
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio


def fill_missing_elevation(grid_df: pd.DataFrame, method: str) -> pd.DataFrame:
    if method == "none":
        grid_df["elevation_imputed"] = grid_df["elevation"].isna()
        return grid_df

    known_mask = grid_df["elevation"].notna()
    missing_mask = ~known_mask

    grid_df["elevation_imputed"] = False
    if not missing_mask.any():
        return grid_df

    known = grid_df.loc[known_mask, ["lon", "lat", "elevation"]].reset_index(drop=True)
    if known.empty:
        raise ValueError("No valid elevation values were sampled from the raster.")

    target_idx = grid_df.index[missing_mask]
    target = grid_df.loc[missing_mask, ["lon", "lat"]].reset_index(drop=True)

    # Use corrected geometry for distance calculations.
    known_xy = np.column_stack([known["lat"].to_numpy(dtype=float), known["lon"].to_numpy(dtype=float)])
    target_xy = np.column_stack([target["lat"].to_numpy(dtype=float), target["lon"].to_numpy(dtype=float)])
    values = known["elevation"].to_numpy(dtype=float)

    deltas = target_xy[:, None, :] - known_xy[None, :, :]
    dist2 = np.sum(deltas * deltas, axis=2)

    if method == "nearest":
        nearest_idx = np.argmin(dist2, axis=1)
        filled = values[nearest_idx]
    elif method == "idw":
        k = min(8, len(known))
        nearest_idx = np.argpartition(dist2, kth=k - 1, axis=1)[:, :k]
        nearest_dist2 = np.take_along_axis(dist2, nearest_idx, axis=1)
        nearest_vals = values[nearest_idx]

        filled = np.empty(len(target), dtype=float)
        exact_match = nearest_dist2 == 0
        has_exact_match = exact_match.any(axis=1)
        if has_exact_match.any():
            exact_rows = np.where(has_exact_match)[0]
            first_exact = exact_match[exact_rows].argmax(axis=1)
            filled[exact_rows] = nearest_vals[exact_rows, first_exact]

        non_exact_rows = np.where(~has_exact_match)[0]
        if len(non_exact_rows):
            d = np.sqrt(nearest_dist2[non_exact_rows])
            weights = 1.0 / np.power(d, 2)
            weights = weights / weights.sum(axis=1, keepdims=True)
            filled[non_exact_rows] = np.sum(nearest_vals[non_exact_rows] * weights, axis=1)
    else:
        raise ValueError(f"Unknown fill method: {method}")

    grid_df.loc[target_idx, "elevation"] = filled
    grid_df.loc[target_idx, "elevation_imputed"] = True
    return grid_df


def main():
    parser = argparse.ArgumentParser(
        description="Sample elevation raster values onto the precipitation grid."
    )
    parser.add_argument(
        "--precip",
        required=True,
        help="CSV with precipitation grid columns lon and lat.",
    )
    parser.add_argument(
        "--elevation",
        required=True,
        help="Path to elevation raster (.tif).",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path with lon, lat, elevation.",
    )
    parser.add_argument(
        "--band",
        type=int,
        default=1,
        help="Raster band to sample (default: 1).",
    )
    parser.add_argument(
        "--fill-missing",
        choices=["nearest", "idw", "none"],
        default="nearest",
        help="How to populate precip cells not covered by the raster (default: nearest).",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  Sample Elevation To Precipitation Grid")
    print("=" * 60)

    precip_df = pd.read_csv(args.precip, usecols=["lon", "lat"]).copy()
    precip_df["lon"] = pd.to_numeric(precip_df["lon"], errors="coerce")
    precip_df["lat"] = pd.to_numeric(precip_df["lat"], errors="coerce")
    precip_df = precip_df.dropna(subset=["lon", "lat"]).drop_duplicates().reset_index(drop=True)

    with rasterio.open(args.elevation) as src:
        print(f"\nRaster CRS    : {src.crs}")
        print(f"Raster bounds : {src.bounds}")
        print(f"Raster nodata : {src.nodata}")
        print(f"Raster res    : {src.res}")

        # Correct geometry for sampling while preserving original columns.
        x = precip_df["lat"].to_numpy(dtype=float)
        y = precip_df["lon"].to_numpy(dtype=float)
        coords = list(zip(x, y))

        samples = np.array([val[0] for val in src.sample(coords, indexes=args.band)], dtype=float)

        nodata = src.nodata
        if nodata is not None:
            samples = np.where(samples == nodata, np.nan, samples)

    precip_df["elevation"] = samples
    matched = int(precip_df["elevation"].notna().sum())
    missing = int(precip_df["elevation"].isna().sum())

    print(f"\nDirect matches    : {matched:,}")
    print(f"Direct missing    : {missing:,}")

    precip_df = fill_missing_elevation(precip_df, args.fill_missing)
    final_missing = int(precip_df["elevation"].isna().sum())
    imputed = int(precip_df["elevation_imputed"].sum())

    out_path = Path(args.output)
    precip_df.to_csv(out_path, index=False)

    print(f"\nGrid points       : {len(precip_df):,}")
    print(f"Imputed elevation : {imputed:,}")
    print(f"Missing elevation : {final_missing:,}")
    if precip_df["elevation"].notna().any():
        print(
            f"Elevation range   : {precip_df['elevation'].min():.2f} -> "
            f"{precip_df['elevation'].max():.2f}"
        )
    print(f"\nSaved -> {out_path}")
    print("\nSample output:")
    print(precip_df.head(5).to_string(index=False))
    print("=" * 60)


if __name__ == "__main__":
    main()
