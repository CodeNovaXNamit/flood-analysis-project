"""
merge_population_tot_p.py
-------------------------
Merge ward-level population (TOT_P) from multiple zone workbooks into the final
grid dataset using ward number.

The source workbooks contain multiple hierarchy levels. This script keeps only
rows where Level == WARD and then joins TOT_P onto the final CSV by Ward_No.
"""

import argparse
from pathlib import Path

import pandas as pd


def load_population_table(pop_dir: str) -> pd.DataFrame:
    files = ["east.xlsx", "North.xlsx", "south.xlsx", "west.xlsx"]
    frames = []

    for name in files:
        path = Path(pop_dir) / name
        df = pd.read_excel(path)
        if "Level" not in df.columns or "TOT_P" not in df.columns or "Ward" not in df.columns:
            raise ValueError(f"Missing required columns in {path}")

        ward_df = df[df["Level"].astype(str).str.upper() == "WARD"].copy()
        if ward_df.empty:
            continue

        ward_df["Ward_No"] = pd.to_numeric(ward_df["Ward"], errors="coerce").astype("Int64")
        ward_df["TOT_P"] = pd.to_numeric(ward_df["TOT_P"], errors="coerce")
        ward_df = ward_df.dropna(subset=["Ward_No", "TOT_P"])
        ward_df = ward_df[["Ward_No", "TOT_P"]].drop_duplicates()
        frames.append(ward_df)

    if not frames:
        raise ValueError("No ward-level population rows were found in the population workbooks.")

    population = pd.concat(frames, ignore_index=True)
    population = population.groupby("Ward_No", as_index=False)["TOT_P"].sum()
    return population


def main():
    parser = argparse.ArgumentParser(description="Merge TOT_P population into the final ward-level dataset.")
    parser.add_argument("--population-dir", required=True, help="Folder containing east/North/south/west Excel files.")
    parser.add_argument("--input", required=True, help="Input final CSV with Ward_No.")
    parser.add_argument("--output", required=True, help="Output CSV path.")
    args = parser.parse_args()

    print("=" * 60)
    print("  Merge Population TOT_P")
    print("=" * 60)

    population = load_population_table(args.population_dir)
    print(f"\nPopulation ward rows : {len(population):,}")

    final_df = pd.read_csv(args.input)
    final_df["Ward_No_num"] = pd.to_numeric(final_df["Ward_No"], errors="coerce").astype("Int64")

    merged = final_df.merge(population, left_on="Ward_No_num", right_on="Ward_No", how="left")
    merged = merged.drop(columns=["Ward_No_num", "Ward_No_y"], errors="ignore").rename(columns={"Ward_No_x": "Ward_No"})

    matched = int(merged["TOT_P"].notna().sum())
    print(f"Final rows           : {len(merged):,}")
    print(f"Rows with TOT_P      : {matched:,}")
    print(f"Rows without TOT_P   : {len(merged) - matched:,}")

    merged.to_csv(args.output, index=False)
    print(f"\nSaved -> {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()
