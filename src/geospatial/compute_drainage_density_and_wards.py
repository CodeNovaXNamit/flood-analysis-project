"""
compute_drainage_density_and_wards.py
------------------------------------
Attach ward membership and drainage density to the precipitation grid.

Outputs:
  1. A per-grid-cell CSV with ward attributes and drainage density.
  2. A per-ward CSV with drainage length, area, and drainage density.
  3. Optionally, a merged final CSV joined onto the precipitation/runoff table.

Important:
The existing precipitation CSV stores columns named `lon` and `lat`, but the
geographic values are swapped for spatial use in this project:

  true_x (longitude) = lat column
  true_y (latitude)  = lon column

This script preserves the original `lon` / `lat` columns for merge compatibility
while using corrected geometry internally.
"""

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point, box


PROJECTED_CRS = "EPSG:32643"  # UTM zone 43N, suitable for Delhi length/area


def build_precip_grid_cells(precip_csv: str) -> tuple[gpd.GeoDataFrame, float, float]:
    df = pd.read_csv(precip_csv, usecols=["lon", "lat"]).drop_duplicates().copy()
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce").round(6)
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce").round(6)
    df = df.dropna(subset=["lon", "lat"]).sort_values(["lon", "lat"]).reset_index(drop=True)

    unique_lon = np.sort(df["lon"].unique())
    unique_lat = np.sort(df["lat"].unique())
    lon_step = float(np.min(np.diff(unique_lon)))
    lat_step = float(np.min(np.diff(unique_lat)))
    half_lon = lon_step / 2.0
    half_lat = lat_step / 2.0

    # Correct geometry for spatial work.
    true_x = df["lat"].to_numpy(dtype=float)
    true_y = df["lon"].to_numpy(dtype=float)

    points = [Point(x, y) for x, y in zip(true_x, true_y)]
    cells = [box(x - half_lat, y - half_lon, x + half_lat, y + half_lon) for x, y in zip(true_x, true_y)]

    base = df.copy()
    base["cell_id"] = np.arange(len(base))
    grid_points = gpd.GeoDataFrame(base.copy(), geometry=points, crs="EPSG:4326")
    grid_cells = gpd.GeoDataFrame(base.copy(), geometry=cells, crs="EPSG:4326")
    return grid_points, grid_cells, lon_step, lat_step


def assign_wards(grid_points: gpd.GeoDataFrame, ward_path: str) -> pd.DataFrame:
    wards = gpd.read_file(ward_path)
    if wards.crs is None:
        raise ValueError("Ward layer has no CRS.")
    wards = wards.to_crs(grid_points.crs)

    joined = gpd.sjoin(
        grid_points,
        wards[["Ward_Name", "Ward_No", "geometry"]],
        how="left",
        predicate="within",
    ).drop(columns=["index_right"], errors="ignore")

    keep_cols = ["cell_id", "lon", "lat", "Ward_Name", "Ward_No"]
    return pd.DataFrame(joined[keep_cols])


def compute_grid_drainage_density(grid_cells: gpd.GeoDataFrame, drainage_path: str) -> pd.DataFrame:
    drainage = gpd.read_file(drainage_path)
    if drainage.crs is None:
        raise ValueError("Drainage layer has no CRS.")

    drainage = drainage.to_crs(PROJECTED_CRS)
    grid_proj = grid_cells.to_crs(PROJECTED_CRS)
    grid_proj["cell_area_km2"] = grid_proj.geometry.area / 1_000_000.0

    clipped = gpd.overlay(
        drainage[["geometry"]],
        grid_proj[["cell_id", "geometry"]],
        how="intersection",
        keep_geom_type=False,
    )

    if clipped.empty:
        lengths = pd.DataFrame({"cell_id": grid_proj["cell_id"], "drainage_length_km": 0.0})
    else:
        clipped["drainage_length_km"] = clipped.geometry.length / 1000.0
        lengths = clipped.groupby("cell_id", as_index=False)["drainage_length_km"].sum()

    out = pd.DataFrame(grid_proj.drop(columns="geometry"))
    out = out.merge(lengths, on="cell_id", how="left")
    out["drainage_length_km"] = out["drainage_length_km"].fillna(0.0)
    out["drainage_density_km_per_km2"] = out["drainage_length_km"] / out["cell_area_km2"]
    return out


def compute_ward_drainage_density(ward_path: str, drainage_path: str) -> pd.DataFrame:
    wards = gpd.read_file(ward_path)
    drainage = gpd.read_file(drainage_path)
    if wards.crs is None or drainage.crs is None:
        raise ValueError("Ward or drainage layer has no CRS.")

    wards_proj = wards.to_crs(PROJECTED_CRS).copy()
    drainage_proj = drainage.to_crs(PROJECTED_CRS)
    wards_proj["ward_area_km2"] = wards_proj.geometry.area / 1_000_000.0

    clipped = gpd.overlay(
        drainage_proj[["geometry"]],
        wards_proj[["Ward_Name", "Ward_No", "geometry"]],
        how="intersection",
        keep_geom_type=False,
    )

    if clipped.empty:
        lengths = pd.DataFrame(
            {"Ward_Name": wards_proj["Ward_Name"], "Ward_No": wards_proj["Ward_No"], "ward_drainage_length_km": 0.0}
        )
    else:
        clipped["ward_drainage_length_km"] = clipped.geometry.length / 1000.0
        lengths = (
            clipped.groupby(["Ward_Name", "Ward_No"], as_index=False)["ward_drainage_length_km"]
            .sum()
        )

    ward_df = pd.DataFrame(wards_proj.drop(columns="geometry"))
    ward_df = ward_df.merge(lengths, on=["Ward_Name", "Ward_No"], how="left")
    ward_df["ward_drainage_length_km"] = ward_df["ward_drainage_length_km"].fillna(0.0)
    ward_df["ward_drainage_density_km_per_km2"] = ward_df["ward_drainage_length_km"] / ward_df["ward_area_km2"]
    return ward_df


def main():
    parser = argparse.ArgumentParser(
        description="Compute drainage density for the precipitation grid and wards."
    )
    parser.add_argument("--precip-grid", required=True, help="Path to precip grid CSV with lon and lat columns.")
    parser.add_argument("--drainage", required=True, help="Path to drainage network vector file.")
    parser.add_argument("--ward", required=True, help="Path to ward polygon vector file.")
    parser.add_argument("--grid-output", required=True, help="Output CSV path for per-grid drainage + ward data.")
    parser.add_argument("--ward-output", required=True, help="Output CSV path for per-ward drainage summary.")
    parser.add_argument("--merge-input", help="Optional merged precip/runoff CSV to enrich.")
    parser.add_argument("--merge-output", help="Optional output path for enriched merged CSV.")
    args = parser.parse_args()

    print("=" * 60)
    print("  Compute Drainage Density And Ward Mapping")
    print("=" * 60)

    print("\n[1/4] Building precipitation grid cells...")
    grid_points, grid_cells, lon_step, lat_step = build_precip_grid_cells(args.precip_grid)
    print(f"      Grid points : {len(grid_points):,}")
    print(f"      Cell size   : lon step {lon_step:.6f}, lat step {lat_step:.6f}")

    print("\n[2/4] Assigning wards to grid points...")
    ward_map = assign_wards(grid_points, args.ward)
    ward_hits = int(ward_map["Ward_No"].notna().sum())
    print(f"      Ward matches: {ward_hits:,} / {len(ward_map):,}")

    print("\n[3/4] Computing drainage density per grid cell...")
    grid_density = compute_grid_drainage_density(grid_cells, args.drainage)
    grid_out = ward_map.merge(
        grid_density[["cell_id", "cell_area_km2", "drainage_length_km", "drainage_density_km_per_km2"]],
        on="cell_id",
        how="left",
    )
    grid_out.to_csv(args.grid_output, index=False)
    print(f"      Saved grid data -> {args.grid_output}")
    print(
        f"      Grid density  : {grid_out['drainage_density_km_per_km2'].min():.4f} -> "
        f"{grid_out['drainage_density_km_per_km2'].max():.4f}"
    )

    print("\n[4/4] Computing drainage density per ward...")
    ward_density = compute_ward_drainage_density(args.ward, args.drainage)
    ward_density.to_csv(args.ward_output, index=False)
    print(f"      Saved ward data -> {args.ward_output}")
    print(
        f"      Ward density  : {ward_density['ward_drainage_density_km_per_km2'].min():.4f} -> "
        f"{ward_density['ward_drainage_density_km_per_km2'].max():.4f}"
    )

    if args.merge_input and args.merge_output:
        print("\n[extra] Merging drainage + ward data into the final table...")
        merged = pd.read_csv(args.merge_input)
        enriched = merged.merge(
            grid_out[
                [
                    "lon",
                    "lat",
                    "Ward_Name",
                    "Ward_No",
                    "cell_area_km2",
                    "drainage_length_km",
                    "drainage_density_km_per_km2",
                ]
            ],
            on=["lon", "lat"],
            how="left",
        )
        enriched.to_csv(args.merge_output, index=False)
        print(f"      Saved enriched final -> {args.merge_output}")

    print("=" * 60)


if __name__ == "__main__":
    main()
