import csv
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SAMPLE_FILE = ROOT / "sample_week_coordinate_hotspot_risk.csv"
REFERENCE_FILE = ROOT / "final_modeling_ready_features.csv"
OUTPUT_FILE = ROOT / "sample_week_unique_ward_risk.csv"


def coord_key(lat: str, lon: str) -> tuple[float, float]:
    return (round(float(lat), 4), round(float(lon), 4))


def load_reference() -> dict[tuple[float, float], tuple[str, str]]:
    mapping: dict[tuple[float, float], tuple[str, str]] = {}
    with REFERENCE_FILE.open("r", newline="", encoding="utf-8-sig") as ref_file:
        reader = csv.DictReader(ref_file)
        for row in reader:
            key = coord_key(row["grid_latitude"], row["grid_longitude"])
            mapping.setdefault(key, (row["ward_name"], row["ward_code"]))
    return mapping


def build_output(reference_map: dict[tuple[float, float], tuple[str, str]]) -> tuple[int, int]:
    unique_wards: "OrderedDict[tuple[str, str], float]" = OrderedDict()
    unmatched = 0

    with SAMPLE_FILE.open("r", newline="", encoding="utf-8-sig") as sample_file:
        reader = csv.DictReader(sample_file)
        for row in reader:
            key = coord_key(row["lat"], row["lon"])
            ward_info = reference_map.get(key)
            if ward_info is None:
                unmatched += 1
                continue

            ward_key = (ward_info[0], ward_info[1])
            risk_value = float(row["hotspot_risk"])

            if ward_key not in unique_wards or risk_value > unique_wards[ward_key]:
                unique_wards[ward_key] = risk_value

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=["ward_name", "ward_code", "risk"])
        writer.writeheader()
        for (ward_name, ward_code), risk in unique_wards.items():
            writer.writerow({"ward_name": ward_name, "ward_code": ward_code, "risk": risk})

    return len(unique_wards), unmatched


def main() -> None:
    reference_map = load_reference()
    unique_count, unmatched_count = build_output(reference_map)
    print(f"created={OUTPUT_FILE.name}")
    print(f"unique_wards={unique_count}")
    print(f"unmatched_coordinates={unmatched_count}")


if __name__ == "__main__":
    main()
