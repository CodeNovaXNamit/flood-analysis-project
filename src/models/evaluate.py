"""Evaluation helpers for saved flood-risk predictions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def accuracy_manual(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float((y_true == y_pred).mean())


def f1_manual(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    if tp == 0:
        return 0.0
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    if precision + recall == 0:
        return 0.0
    return float(2 * precision * recall / (precision + recall))


def evaluate_predictions(df: pd.DataFrame) -> dict[str, float]:
    required = {"proxy_flood_label", "predicted_flood_label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    y_true = df["proxy_flood_label"].to_numpy(dtype=int)
    y_pred = df["predicted_flood_label"].to_numpy(dtype=int)
    return {
        "accuracy": accuracy_manual(y_true, y_pred),
        "f1": f1_manual(y_true, y_pred),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a saved prediction CSV.")
    parser.add_argument("--input", required=True, help="Prediction CSV with labels.")
    parser.add_argument("--output", help="Optional JSON file for metrics.")
    args = parser.parse_args()

    metrics = evaluate_predictions(pd.read_csv(args.input))
    print(json.dumps(metrics, indent=2))

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
