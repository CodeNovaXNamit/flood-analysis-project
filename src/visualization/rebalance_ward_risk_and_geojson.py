import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT_CSV = ROOT / "sample_week_unique_ward_risk.csv"
INPUT_GEOJSON = ROOT / "Delhi_Wards.geojson"
OUTPUT_CSV = ROOT / "sample_week_unique_ward_risk_rebalanced.csv"
OUTPUT_GEOJSON = ROOT / "Delhi_Wards_with_rebalanced_risk.geojson"

RANDOM_SEED = 20260328
LOW_RANGE = (0.0, 0.3)
MID_RANGE = (0.3, 0.7)
HIGH_RANGE = (0.7, 1.0)


def bounded_random(rng: random.Random, value_range: tuple[float, float], *, upper_open: bool) -> float:
    low, high = value_range
    value = rng.uniform(low, high)
    if upper_open and value >= high:
        value = high - 1e-6
    return round(value, 6)


def rebalance_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rng = random.Random(RANDOM_SEED)
    indexed_rows = list(enumerate(rows))
    indexed_rows.sort(key=lambda item: float(item[1]["risk"]), reverse=True)

    total = len(indexed_rows)
    high_count = round(total * 0.30)
    mid_count = round(total * 0.40)

    rebalanced: list[dict[str, str] | None] = [None] * total

    for position, (original_index, row) in enumerate(indexed_rows):
        updated = dict(row)
        if position < high_count:
            risk = bounded_random(rng, HIGH_RANGE, upper_open=True)
        elif position < high_count + mid_count:
            risk = bounded_random(rng, MID_RANGE, upper_open=True)
        else:
            risk = bounded_random(rng, LOW_RANGE, upper_open=True)
        updated["risk"] = f"{risk:.6f}"
        rebalanced[original_index] = updated

    return [row for row in rebalanced if row is not None]


def write_csv(rows: list[dict[str, str]]) -> None:
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=["ward_name", "ward_code", "risk"])
        writer.writeheader()
        writer.writerows(rows)


def build_risk_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str], float]:
    lookup: dict[tuple[str, str], float] = {}
    for row in rows:
        lookup[(row["ward_code"].strip(), row["ward_name"].strip().upper())] = float(row["risk"])
    return lookup


def write_geojson(rows: list[dict[str, str]]) -> tuple[int, int]:
    rng = random.Random(RANDOM_SEED + 1)
    risk_lookup = build_risk_lookup(rows)

    with INPUT_GEOJSON.open("r", encoding="utf-8") as input_file:
        geojson = json.load(input_file)

    matched = 0
    unmatched = 0

    for feature in geojson.get("features", []):
        properties = feature.setdefault("properties", {})
        ward_no = str(properties.get("Ward_No", "")).strip()
        ward_name = str(properties.get("Ward_Name", "")).strip().upper()

        risk = risk_lookup.get((ward_no, ward_name))
        if risk is None:
            risk = bounded_random(rng, LOW_RANGE, upper_open=True)
            unmatched += 1
        else:
            matched += 1

        properties["risk"] = risk

    with OUTPUT_GEOJSON.open("w", encoding="utf-8") as output_file:
        json.dump(geojson, output_file, ensure_ascii=False)

    return matched, unmatched


def main() -> None:
    with INPUT_CSV.open("r", newline="", encoding="utf-8-sig") as input_file:
        rows = list(csv.DictReader(input_file))

    rebalanced_rows = rebalance_rows(rows)
    write_csv(rebalanced_rows)
    matched, unmatched = write_geojson(rebalanced_rows)

    print(f"created_csv={OUTPUT_CSV.name}")
    print(f"created_geojson={OUTPUT_GEOJSON.name}")
    print(f"csv_rows={len(rebalanced_rows)}")
    print(f"geojson_matched={matched}")
    print(f"geojson_unmatched={unmatched}")


if __name__ == "__main__":
    main()
