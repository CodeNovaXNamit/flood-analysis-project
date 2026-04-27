"""
build_modeling_ready_dataset.py
-------------------------------
Build the final modeling-ready CSV by:
  1. Merging elevation onto the current final dataset.
  2. Cleaning and renaming columns.
  3. Writing a compact, consistent output table.

Important coordinate note:
The project stores the spatial columns as:
  lon -> actual latitude
  lat -> actual longitude

To make the final dataset easier to use, this script renames them to:
  grid_latitude  = lon
  grid_longitude = lat
"""

import argparse

import pandas as pd


def main():
    parser = argparse.ArgumentParser(description="Build a final modeling-ready dataset.")
    parser.add_argument("--input", required=True, help="Input final CSV.")
    parser.add_argument("--elevation", required=True, help="Elevation CSV with lon, lat, elevation.")
    parser.add_argument("--output", required=True, help="Output modeling-ready CSV.")
    args = parser.parse_args()

    print("=" * 60)
    print("  Build Modeling Ready Dataset")
    print("=" * 60)

    final_df = pd.read_csv(args.input)
    elev_df = pd.read_csv(args.elevation, usecols=["lon", "lat", "elevation", "elevation_imputed"])

    final_df["lon"] = pd.to_numeric(final_df["lon"], errors="coerce").round(6)
    final_df["lat"] = pd.to_numeric(final_df["lat"], errors="coerce").round(6)
    elev_df["lon"] = pd.to_numeric(elev_df["lon"], errors="coerce").round(6)
    elev_df["lat"] = pd.to_numeric(elev_df["lat"], errors="coerce").round(6)

    merged = final_df.merge(elev_df, on=["lon", "lat"], how="left")

    renamed = merged.rename(
        columns={
            "time": "date",
            "lon": "grid_latitude",
            "lat": "grid_longitude",
            "precipitation": "precipitation_mm",
            "runoff_raw": "runoff_value",
            "runoff_norm": "runoff_normalized",
            "Ward_Name": "ward_name",
            "Ward_No": "ward_code",
            "TOT_P": "total_population",
            "TOT_P_imputed": "population_imputed",
            "elevation": "elevation_m",
        }
    )

    column_order = [
        "date",
        "grid_latitude",
        "grid_longitude",
        "ward_name",
        "ward_code",
        "precipitation_mm",
        "runoff_value",
        "runoff_normalized",
        "runoff_coefficient",
        "runoff_imputed",
        "elevation_m",
        "elevation_imputed",
        "cell_area_km2",
        "drainage_length_km",
        "drainage_density_km_per_km2",
        "total_population",
        "population_imputed",
    ]

    modeling_df = renamed[column_order].copy()
    modeling_df["date"] = modeling_df["date"].astype(str)
    modeling_df["ward_name"] = modeling_df["ward_name"].astype(str).str.strip()
    modeling_df["ward_code"] = modeling_df["ward_code"].astype(str).str.strip()

    modeling_df.to_csv(args.output, index=False)

    print(f"\nInput rows              : {len(final_df):,}")
    print(f"Output rows             : {len(modeling_df):,}")
    print(f"Rows with elevation     : {int(modeling_df['elevation_m'].notna().sum()):,}")
    print(f"Rows with population    : {int(modeling_df['total_population'].notna().sum()):,}")
    print(f"\nSaved -> {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()
