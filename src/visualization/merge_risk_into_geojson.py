import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RISK_FILE = ROOT / "sample_week_unique_ward_risk.csv"
GEOJSON_FILE = ROOT / "Delhi_Wards.geojson"
OUTPUT_FILE = ROOT / "Delhi_Wards_with_risk.geojson"


def load_risk_map() -> dict[str, dict[str, str]]:
    risk_map: dict[str, dict[str, str]] = {}
    with RISK_FILE.open("r", newline="", encoding="utf-8-sig") as risk_file:
        reader = csv.DictReader(risk_file)
        for row in reader:
            ward_code = str(row["ward_code"]).strip()
            risk_map[ward_code] = {
                "ward_name": row["ward_name"],
                "risk": row["risk"],
            }
    return risk_map


def main() -> None:
    risk_map = load_risk_map()

    with GEOJSON_FILE.open("r", encoding="utf-8-sig") as geojson_file:
        data = json.load(geojson_file)

    matched = 0
    unmatched = 0

    for feature in data.get("features", []):
        properties = feature.setdefault("properties", {})
        ward_no = str(properties.get("Ward_No", "")).strip()
        risk_info = risk_map.get(ward_no)

        if risk_info is None:
            properties["risk"] = None
            unmatched += 1
            continue

        properties["risk"] = float(risk_info["risk"])
        matched += 1

    with OUTPUT_FILE.open("w", encoding="utf-8") as output_file:
        json.dump(data, output_file, ensure_ascii=False)

    print(f"created={OUTPUT_FILE.name}")
    print(f"matched_features={matched}")
    print(f"unmatched_features={unmatched}")


if __name__ == "__main__":
    main()
