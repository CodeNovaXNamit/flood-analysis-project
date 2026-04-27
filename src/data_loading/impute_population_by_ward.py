"""
impute_population_by_ward.py
---------------------------
Fill missing ward population (TOT_P) using nearby ward polygons.

Method:
  1. Read ward polygons and compute ward area in km^2.
  2. Join known TOT_P values from the final dataset at ward level.
  3. Convert known TOT_P to population density.
  4. For wards with missing TOT_P, estimate density from nearby known wards
     using inverse-distance weighting on ward centroids.
  5. Convert estimated density back to TOT_P and write the filled value to all
     rows in the final dataset for that ward.
"""

import argparse

import geopandas as gpd
import numpy as np
import pandas as pd


PROJECTED_CRS = "EPSG:32643"


def normalize_ward_no(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype("Int64")


def build_ward_population_table(final_csv: str, ward_path: str) -> pd.DataFrame:
    final_df = pd.read_csv(final_csv, usecols=["Ward_Name", "Ward_No", "TOT_P"])
    ward_pop = final_df[["Ward_Name", "Ward_No", "TOT_P"]].drop_duplicates().copy()
    ward_pop["Ward_No_num"] = normalize_ward_no(ward_pop["Ward_No"])

    wards = gpd.read_file(ward_path)[["Ward_Name", "Ward_No", "geometry"]].copy()
    wards["Ward_No_num"] = normalize_ward_no(wards["Ward_No"])
    wards = wards.to_crs(PROJECTED_CRS)
    wards["ward_area_km2"] = wards.geometry.area / 1_000_000.0
    wards["centroid"] = wards.geometry.centroid

    table = wards.merge(
        ward_pop[["Ward_Name", "Ward_No_num", "TOT_P"]],
        on=["Ward_Name", "Ward_No_num"],
        how="left",
    )
    table["pop_density_per_km2"] = table["TOT_P"] / table["ward_area_km2"]
    return table


def impute_missing_tot_p(ward_table: pd.DataFrame, k: int = 5) -> pd.DataFrame:
    known = ward_table[ward_table["TOT_P"].notna()].copy()
    missing = ward_table[ward_table["TOT_P"].isna()].copy()

    ward_table["TOT_P_imputed"] = False
    if missing.empty or known.empty:
        return ward_table

    known_xy = np.array([(geom.x, geom.y) for geom in known["centroid"]], dtype=float)
    missing_xy = np.array([(geom.x, geom.y) for geom in missing["centroid"]], dtype=float)
    known_density = known["pop_density_per_km2"].to_numpy(dtype=float)

    deltas = missing_xy[:, None, :] - known_xy[None, :, :]
    dist2 = np.sum(deltas * deltas, axis=2)

    k = min(k, len(known))
    nearest_idx = np.argpartition(dist2, kth=k - 1, axis=1)[:, :k]
    nearest_dist2 = np.take_along_axis(dist2, nearest_idx, axis=1)
    nearest_density = known_density[nearest_idx]

    estimated_density = np.empty(len(missing), dtype=float)
    exact_match = nearest_dist2 == 0
    has_exact = exact_match.any(axis=1)

    if has_exact.any():
        rows = np.where(has_exact)[0]
        first_exact = exact_match[rows].argmax(axis=1)
        estimated_density[rows] = nearest_density[rows, first_exact]

    rows = np.where(~has_exact)[0]
    if len(rows):
        d = np.sqrt(nearest_dist2[rows])
        weights = 1.0 / np.power(d, 2)
        weights = weights / weights.sum(axis=1, keepdims=True)
        estimated_density[rows] = np.sum(nearest_density[rows] * weights, axis=1)

    filled_tot_p = np.rint(estimated_density * missing["ward_area_km2"].to_numpy(dtype=float))
    ward_table.loc[missing.index, "TOT_P"] = filled_tot_p
    ward_table.loc[missing.index, "pop_density_per_km2"] = estimated_density
    ward_table.loc[missing.index, "TOT_P_imputed"] = True
    return ward_table


def main():
    parser = argparse.ArgumentParser(description="Impute missing TOT_P using nearby ward polygons.")
    parser.add_argument("--input", required=True, help="Input CSV with Ward_Name, Ward_No, TOT_P.")
    parser.add_argument("--ward", required=True, help="Ward polygon file.")
    parser.add_argument("--output", required=True, help="Output CSV with filled TOT_P.")
    args = parser.parse_args()

    print("=" * 60)
    print("  Impute Population By Ward")
    print("=" * 60)

    ward_table = build_ward_population_table(args.input, args.ward)
    before_missing = int(ward_table["TOT_P"].isna().sum())
    print(f"\nWards with known TOT_P   : {int(ward_table['TOT_P'].notna().sum()):,}")
    print(f"Wards missing TOT_P     : {before_missing:,}")

    ward_table = impute_missing_tot_p(ward_table)
    print(f"Wards imputed           : {int(ward_table['TOT_P_imputed'].sum()):,}")
    print(f"Wards still missing     : {int(ward_table['TOT_P'].isna().sum()):,}")

    final_df = pd.read_csv(args.input)
    final_df["Ward_No_num"] = normalize_ward_no(final_df["Ward_No"])

    ward_fill = pd.DataFrame(
        ward_table[["Ward_Name", "Ward_No_num", "TOT_P", "TOT_P_imputed"]]
    )
    merged = final_df.drop(columns=["TOT_P"], errors="ignore").merge(
        ward_fill,
        on=["Ward_Name", "Ward_No_num"],
        how="left",
    )
    merged = merged.drop(columns=["Ward_No_num"])
    merged.to_csv(args.output, index=False)

    print(f"\nFinal rows               : {len(merged):,}")
    print(f"Rows with TOT_P          : {int(merged['TOT_P'].notna().sum()):,}")
    print(f"Rows with imputed TOT_P  : {int(merged['TOT_P_imputed'].fillna(False).sum()):,}")
    print(f"\nSaved -> {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()
