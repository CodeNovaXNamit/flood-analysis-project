"""Extract a small rainfall sample from local NC4 files for testing."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import xarray as xr


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract a test rainfall CSV from NC4 files.")
    parser.add_argument("--input-dir", default="data/external/test_rainfall/nc4", help="Directory containing NC4 files.")
    parser.add_argument("--output", default="data/interim/flood_modeling/rainfall_spatial_full.csv", help="Output CSV path.")
    parser.add_argument("--limit", type=int, default=50, help="Number of NC4 files to process.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    files = sorted(input_dir.glob("*.nc4"))[: args.limit]
    if not files:
        raise FileNotFoundError(f"No NC4 files found in {input_dir}")

    all_data = []
    for file_path in files:
        ds = xr.open_dataset(file_path)
        rain_delhi = ds["precipitation"].squeeze()
        df = rain_delhi.to_dataframe().reset_index()[["lat", "lon", "precipitation"]]
        df.columns = ["lat", "lon", "rainfall"]
        df["time"] = str(ds["time"].values[0])
        all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)
    print(f"Saved {len(final_df):,} rows to {output_path}")


if __name__ == "__main__":
    main()
