"""
add_model_features.py
---------------------
Add modeling features to the final dataset:
  - lag1, lag2, lag3
  - rain_3d, rain_5d, rain_7d
  - cumulative_rainfall
  - trend
  - average_intensity
  - seasonal encoder
  - month_sin, month_cos
  - slope

Assumptions:
  - Temporal features are computed from precipitation_mm for each grid cell.
  - trend is the change between current precipitation and the 3-step rolling mean.
  - average_intensity is the 3-step rolling mean of precipitation.
  - seasonal_encoder uses meteorological seasons:
      winter=0, pre_monsoon=1, monsoon=2, post_monsoon=3
  - slope is derived from neighboring elevation cells on the grid.
"""

import argparse

import numpy as np
import pandas as pd


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["grid_latitude", "grid_longitude", "date"]).copy()
    grp = df.groupby(["grid_latitude", "grid_longitude"], sort=False)

    df["lag1"] = grp["precipitation_mm"].shift(1)
    df["lag2"] = grp["precipitation_mm"].shift(2)
    df["lag3"] = grp["precipitation_mm"].shift(3)

    rolling_3 = grp["precipitation_mm"].rolling(3, min_periods=1)
    rolling_5 = grp["precipitation_mm"].rolling(5, min_periods=1)
    rolling_7 = grp["precipitation_mm"].rolling(7, min_periods=1)

    rolling_mean = rolling_3.mean().reset_index(level=[0, 1], drop=True)
    df["rain_3d"] = rolling_3.sum().reset_index(level=[0, 1], drop=True)
    df["rain_5d"] = rolling_5.sum().reset_index(level=[0, 1], drop=True)
    df["rain_7d"] = rolling_7.sum().reset_index(level=[0, 1], drop=True)
    df["cumulative_rainfall"] = grp["precipitation_mm"].cumsum()
    df["average_intensity"] = rolling_mean
    df["trend"] = df["precipitation_mm"] - df["average_intensity"]
    return df


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    dt = pd.to_datetime(df["date"])
    month = dt.dt.month

    df["month"] = month
    df["month_sin"] = np.sin(2 * np.pi * month / 12.0)
    df["month_cos"] = np.cos(2 * np.pi * month / 12.0)

    season_map = {
        12: 0, 1: 0, 2: 0,   # winter
        3: 1, 4: 1, 5: 1,    # pre-monsoon
        6: 2, 7: 2, 8: 2, 9: 2,  # monsoon
        10: 3, 11: 3,        # post-monsoon
    }
    df["seasonal_encoder"] = month.map(season_map).astype(int)
    return df


def compute_slope_from_grid(grid: pd.DataFrame) -> pd.DataFrame:
    grid = grid.drop_duplicates().sort_values(["grid_latitude", "grid_longitude"]).copy()

    lat_vals = np.sort(grid["grid_latitude"].unique())
    lon_vals = np.sort(grid["grid_longitude"].unique())
    lat_index = {v: i for i, v in enumerate(lat_vals)}
    lon_index = {v: i for i, v in enumerate(lon_vals)}

    elev = np.full((len(lat_vals), len(lon_vals)), np.nan, dtype=float)
    for row in grid.itertuples(index=False):
        elev[lat_index[row.grid_latitude], lon_index[row.grid_longitude]] = row.elevation_m

    # Grid spacing in degrees converted approximately to meters.
    lat_step_deg = float(np.min(np.diff(lat_vals))) if len(lat_vals) > 1 else 0.0
    lon_step_deg = float(np.min(np.diff(lon_vals))) if len(lon_vals) > 1 else 0.0
    mean_lat_rad = np.deg2rad(np.mean(lat_vals))
    dy = lat_step_deg * 111_320.0
    dx = lon_step_deg * 111_320.0 * np.cos(mean_lat_rad)

    grad_y, grad_x = np.gradient(elev, dy, dx)
    slope = np.sqrt(grad_x ** 2 + grad_y ** 2)

    slope_records = []
    for lat in lat_vals:
        for lon in lon_vals:
            slope_records.append(
                {
                    "grid_latitude": lat,
                    "grid_longitude": lon,
                    "slope": slope[lat_index[lat], lon_index[lon]],
                }
            )

    return pd.DataFrame(slope_records)


def main():
    parser = argparse.ArgumentParser(description="Add time-series and terrain features to the final dataset.")
    parser.add_argument("--input", required=True, help="Input modeling-ready CSV.")
    parser.add_argument("--elevation-grid", required=True, help="Full elevation CSV used to derive slope.")
    parser.add_argument("--output", required=True, help="Output CSV with added features.")
    args = parser.parse_args()

    print("=" * 60)
    print("  Add Model Features")
    print("=" * 60)

    df = pd.read_csv(args.input)
    print(f"\nInput rows : {len(df):,}")

    df = add_temporal_features(df)
    df = add_calendar_features(df)

    elev_grid = pd.read_csv(args.elevation_grid, usecols=["lon", "lat", "elevation"]).rename(
        columns={"lon": "grid_latitude", "lat": "grid_longitude", "elevation": "elevation_m"}
    )
    elev_grid["grid_latitude"] = pd.to_numeric(elev_grid["grid_latitude"], errors="coerce").round(6)
    elev_grid["grid_longitude"] = pd.to_numeric(elev_grid["grid_longitude"], errors="coerce").round(6)
    elev_grid["elevation_m"] = pd.to_numeric(elev_grid["elevation_m"], errors="coerce")

    slope_df = compute_slope_from_grid(elev_grid)
    df = df.merge(slope_df, on=["grid_latitude", "grid_longitude"], how="left")

    df.to_csv(args.output, index=False)

    print(f"Output rows: {len(df):,}")
    print(f"Saved -> {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()
