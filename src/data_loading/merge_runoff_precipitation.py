"""
merge_runoff_precipitation.py
-----------------------------
Merges a large runoff CSV (16M+ rows) with the interpolated precipitation CSV.

Strategy
--------
Runoff resolution  : ~0.0001 deg  (very fine, e.g. DEM-derived)
Precip grid spacing: ~0.0125 deg  (33x33 = 1089 unique coords)

Since many runoff pixels fall inside one precip cell, we:
  1. Snap every runoff (lat, lon) to its nearest precip grid point
     using fast binary search - O(log n), no KD-tree needed.
  2. Aggregate runoff values per snapped cell (mean across all pixels).
  3. Compute runoff_coefficient on the aggregated values.
  4. Merge the 1089-row runoff table into the precip CSV on (lon, lat).

Usage
-----
    python merge_runoff_precipitation.py \
        --runoff    /path/to/runoff.csv \
        --precip    combined_precipitation_interpolated.csv \
        --output    combined_final.csv \
        --nodata    -9999 \
        --agg       mean \
        --chunksize 500000

Arguments
---------
  --runoff      Path to runoff CSV  (columns: lat, lon, runoff)
  --precip      Path to interpolated precipitation CSV
  --output      Output file path
  --nodata      Nodata sentinel in runoff (default: -9999)
  --agg         How to aggregate multiple runoff pixels per cell:
                  mean  -> average (default, recommended for rainfall-runoff)
                  max   -> worst-case / peak runoff
                  sum   -> total runoff volume per cell
  --fill-missing How to populate precip cells with no direct runoff match:
                  nearest -> copy the nearest populated runoff cell (default)
                  idw     -> inverse-distance weighted interpolation
                  none    -> leave unmatched cells as NaN
  --chunksize   Rows per chunk when reading runoff (default: 500000)
"""

import argparse
import numpy as np
import pandas as pd
import sys
from pathlib import Path


# ---------------------------------------------
# Helpers
# ---------------------------------------------

def snap_to_nearest(vals: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """
    Snap each value in `vals` to the closest value in sorted `grid`.
    Uses binary search - fast even for 16M rows.
    """
    idx = np.searchsorted(grid, vals)                  # insertion index
    idx = np.clip(idx, 0, len(grid) - 1)
    idx_left = np.maximum(idx - 1, 0)
    closer_left = np.abs(vals - grid[idx_left]) < np.abs(vals - grid[idx])
    return grid[np.where(closer_left, idx_left, idx)]


def compute_runoff_coefficient(series: pd.Series, nodata) -> pd.DataFrame:
    """
    Given a series of raw runoff values:
      1. Replace nodata with NaN
      2. Normalize to [0, 1]
      3. runoff_coefficient = 1 - normalized   (higher runoff -> lower coefficient)
    Returns a DataFrame with runoff_raw, runoff_norm, runoff_coefficient.
    """
    df = pd.DataFrame({'runoff_raw': series})
    df['runoff_raw'] = pd.to_numeric(df['runoff_raw'], errors='coerce')
    df.loc[df['runoff_raw'] == nodata, 'runoff_raw'] = np.nan

    min_val = df['runoff_raw'].min()
    max_val = df['runoff_raw'].max()

    if max_val == min_val:
        # All values identical -> coefficient is undefined, set to 0.5
        print("  WARNING: all runoff values are identical - runoff_coefficient set to 0.5")
        df['runoff_norm']        = 0.5
        df['runoff_coefficient'] = 0.5
    else:
        df['runoff_norm']        = (df['runoff_raw'] - min_val) / (max_val - min_val)
        df['runoff_coefficient'] = 1.0 - df['runoff_norm']

    return df


def fill_missing_runoff_cells(runoff_grid: pd.DataFrame, method: str) -> pd.DataFrame:
    """
    Fill missing runoff cells on the precipitation grid.

    The precipitation grid is small (1089 cells), so a dense distance matrix is
    both simple and fast here.
    """
    if method == "none":
        runoff_grid["runoff_imputed"] = runoff_grid["runoff_raw"].isna()
        return runoff_grid

    known_mask = runoff_grid["runoff_raw"].notna()
    missing_mask = ~known_mask

    runoff_grid["runoff_imputed"] = False
    if not missing_mask.any():
        return runoff_grid

    known = runoff_grid.loc[known_mask, ["lon", "lat", "runoff_raw"]].reset_index(drop=True)
    if known.empty:
        raise ValueError("Cannot fill missing runoff cells because no runoff values were aggregated.")

    target_idx = runoff_grid.index[missing_mask]
    target = runoff_grid.loc[missing_mask, ["lon", "lat"]].reset_index(drop=True)

    known_xy = known[["lon", "lat"]].to_numpy(dtype=float)
    target_xy = target[["lon", "lat"]].to_numpy(dtype=float)
    values = known["runoff_raw"].to_numpy(dtype=float)

    deltas = target_xy[:, None, :] - known_xy[None, :, :]
    dist2 = np.sum(deltas * deltas, axis=2)

    if method == "nearest":
        nearest_idx = np.argmin(dist2, axis=1)
        filled_values = values[nearest_idx]
    elif method == "idw":
        k = min(8, len(known))
        nearest_idx = np.argpartition(dist2, kth=k - 1, axis=1)[:, :k]
        nearest_dist2 = np.take_along_axis(dist2, nearest_idx, axis=1)
        nearest_vals = values[nearest_idx]

        filled_values = np.empty(len(target), dtype=float)
        exact_match = nearest_dist2 == 0
        has_exact_match = exact_match.any(axis=1)
        if has_exact_match.any():
            exact_rows = np.where(has_exact_match)[0]
            first_exact = exact_match[exact_rows].argmax(axis=1)
            filled_values[exact_rows] = nearest_vals[exact_rows, first_exact]

        non_exact_rows = np.where(~has_exact_match)[0]
        if len(non_exact_rows):
            d = np.sqrt(nearest_dist2[non_exact_rows])
            weights = 1.0 / np.power(d, 2)
            weights = weights / weights.sum(axis=1, keepdims=True)
            filled_values[non_exact_rows] = np.sum(nearest_vals[non_exact_rows] * weights, axis=1)
    else:
        raise ValueError(f"Unknown fill method: {method}")

    runoff_grid.loc[target_idx, "runoff_raw"] = filled_values
    runoff_grid.loc[target_idx, "runoff_imputed"] = True
    return runoff_grid


# ---------------------------------------------
# Main
# ---------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Merge runoff -> precipitation CSV")
    parser.add_argument("--runoff",     required=True,  help="Path to runoff CSV")
    parser.add_argument("--precip",     required=True,  help="Path to interpolated precipitation CSV")
    parser.add_argument("--output",     required=True,  help="Output CSV path")
    parser.add_argument("--nodata",     type=float, default=-9999, help="Nodata value in runoff")
    parser.add_argument("--agg",        choices=["mean", "max", "sum"], default="mean")
    parser.add_argument("--fill-missing", choices=["nearest", "idw", "none"], default="nearest")
    parser.add_argument("--chunksize",  type=int, default=500_000)
    args = parser.parse_args()

    print("=" * 60)
    print("  Runoff x Precipitation Merge Pipeline")
    print("=" * 60)

    # Step 1: Load precip unique grid coords
    print("\n[1/5] Loading precipitation grid coordinates...")
    precip_df = pd.read_csv(args.precip)
    unique_lons = np.array(sorted(precip_df['lon'].unique()))
    unique_lats = np.array(sorted(precip_df['lat'].unique()))
    print(f"      Precip grid: {len(unique_lons)} lons x {len(unique_lats)} lats "
          f"= {len(unique_lons)*len(unique_lats)} cells")
    print(f"      Lon range  : {unique_lons[0]:.6f} -> {unique_lons[-1]:.6f}")
    print(f"      Lat range  : {unique_lats[0]:.6f} -> {unique_lats[-1]:.6f}")
    print(f"      Dates      : {precip_df['time'].nunique()}, Rows: {len(precip_df):,}")

    # Step 2: Stream runoff, snap, accumulate
    print(f"\n[2/5] Reading runoff in chunks of {args.chunksize:,} rows & snapping coords...")

    agg_dict = {}   # key: (lon_snap, lat_snap) -> list of runoff values
    total_rows = 0
    out_of_bounds = 0

    for chunk_num, chunk in enumerate(
        pd.read_csv(args.runoff, chunksize=args.chunksize, dtype={'lat': float, 'lon': float, 'runoff': float})
    ):
        total_rows += len(chunk)

        # Replace nodata before aggregating
        chunk['runoff'] = pd.to_numeric(chunk['runoff'], errors='coerce')
        chunk.loc[chunk['runoff'] == args.nodata, 'runoff'] = np.nan
        chunk = chunk.dropna(subset=['runoff'])

        # Snap to precip grid
        chunk['lon_snap'] = snap_to_nearest(chunk['lon'].values, unique_lons)
        chunk['lat_snap'] = snap_to_nearest(chunk['lat'].values, unique_lats)

        # Track points that fall outside the precip bounding box
        lon_tol = (unique_lons[1] - unique_lons[0]) / 2
        lat_tol = (unique_lats[1] - unique_lats[0]) / 2
        oob = (
            (chunk['lon'] < unique_lons[0]  - lon_tol) |
            (chunk['lon'] > unique_lons[-1] + lon_tol) |
            (chunk['lat'] < unique_lats[0]  - lat_tol) |
            (chunk['lat'] > unique_lats[-1] + lat_tol)
        )
        out_of_bounds += oob.sum()

        # Accumulate values per cell
        grouped = chunk.groupby(['lon_snap', 'lat_snap'])['runoff']
        if args.agg == 'mean':
            cell_vals = grouped.mean()
        elif args.agg == 'max':
            cell_vals = grouped.max()
        else:
            cell_vals = grouped.sum()

        for (lon_s, lat_s), val in cell_vals.items():
            key = (lon_s, lat_s)
            if key not in agg_dict:
                agg_dict[key] = []
            agg_dict[key].append(val)

        if (chunk_num + 1) % 10 == 0:
            print(f"      Chunk {chunk_num+1} done - {total_rows:,} rows processed, "
                  f"{len(agg_dict)} cells populated")

    print(f"\n      Total runoff rows processed : {total_rows:,}")
    print(f"      Rows outside precip bbox   : {out_of_bounds:,}")
    print(f"      Precip cells with runoff   : {len(agg_dict)} / {len(unique_lons)*len(unique_lats)}")

    # Step 3: Final aggregation across chunks
    print("\n[3/5] Finalising per-cell runoff aggregation...")
    records = []
    for (lon_s, lat_s), vals in agg_dict.items():
        arr = np.array(vals)
        if args.agg == 'mean':
            final = arr.mean()
        elif args.agg == 'max':
            final = arr.max()
        else:
            final = arr.sum()
        records.append({'lon': lon_s, 'lat': lat_s, 'runoff_raw': final})

    runoff_agg = pd.DataFrame(records)
    print(f"      Aggregated runoff table shape: {runoff_agg.shape}")

    # Step 4: Compute runoff coefficient
    print(f"\n[4/5] Building full runoff grid and filling gaps ({args.fill_missing})...")

    # Round coords to avoid float64 key mismatches during grid merge.
    DECIMALS = 6
    precip_df['lon'] = precip_df['lon'].round(DECIMALS)
    precip_df['lat'] = precip_df['lat'].round(DECIMALS)
    runoff_agg['lon'] = runoff_agg['lon'].round(DECIMALS)
    runoff_agg['lat'] = runoff_agg['lat'].round(DECIMALS)

    full_grid = (
        precip_df[['lon', 'lat']]
        .drop_duplicates()
        .merge(runoff_agg[['lon', 'lat', 'runoff_raw']], on=['lon', 'lat'], how='left')
        .sort_values(['lon', 'lat'])
        .reset_index(drop=True)
    )

    observed_cells = full_grid['runoff_raw'].notna().sum()
    missing_cells = full_grid['runoff_raw'].isna().sum()
    print(f"      Direct runoff cells : {observed_cells} / {len(full_grid)}")
    print(f"      Missing cells       : {missing_cells}")

    full_grid = fill_missing_runoff_cells(full_grid, args.fill_missing)

    coeff_df = compute_runoff_coefficient(full_grid['runoff_raw'], nodata=args.nodata)
    full_grid['runoff_raw'] = coeff_df['runoff_raw']
    full_grid['runoff_norm'] = coeff_df['runoff_norm']
    full_grid['runoff_coefficient'] = coeff_df['runoff_coefficient']

    imputed_cells = int(full_grid['runoff_imputed'].sum())
    print(f"      Imputed runoff cells: {imputed_cells}")
    print(f"      runoff_raw         : {full_grid['runoff_raw'].min():.4f} -> {full_grid['runoff_raw'].max():.4f}")
    print(f"      runoff_coefficient : {full_grid['runoff_coefficient'].min():.4f} -> {full_grid['runoff_coefficient'].max():.4f}")

    # Step 5: Merge with precip (left join - keeps all dates)
    print("\n[5/5] Merging with precipitation data...")

    merged = precip_df.merge(
        full_grid[['lon', 'lat', 'runoff_raw', 'runoff_norm', 'runoff_coefficient', 'runoff_imputed']],
        on=['lon', 'lat'],
        how='left'    # keep every (date x coord) row in precip, fill NaN where no runoff
    )

    matched_cells = merged['runoff_coefficient'].notna().sum()
    print(f"      Precip rows        : {len(precip_df):,}")
    print(f"      Merged rows        : {len(merged):,}")
    print(f"      Rows with runoff   : {matched_cells:,}  "
          f"({100*matched_cells/len(merged):.1f}%)")

    # Save
    out_path = Path(args.output)
    merged.to_csv(out_path, index=False)
    size_mb = out_path.stat().st_size / 1e6
    print(f"\nSaved -> {out_path}  ({size_mb:.1f} MB)")
    print("\nColumn summary:")
    print(merged.dtypes.to_string())
    print("\nSample output:")
    print(merged.head(5).to_string())
    print("=" * 60)


if __name__ == "__main__":
    main()
