from __future__ import annotations

import json
import pickle
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch

from src.models.predict import (
    GradientBoostedStumps,
    RandomStumpForest,
    TorchMLP,
    add_inference_features,
    add_static_features,
    sigmoid,
    standardize_columns,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = PROJECT_ROOT / "data" / "processed" / "models"
REFERENCE_GRID_PATH = PROJECT_ROOT / "data" / "processed" / "references" / "delhi_unique_model_grid_coordinates.csv"
PIPELINE_ROOT = PROJECT_ROOT / "outputs" / "pipeline"
UPLOADS_DIR = PIPELINE_ROOT / "uploads"
RUNS_DIR = PIPELINE_ROOT / "runs"


@dataclass(frozen=True)
class RunArtifacts:
    upload_path: Path
    interpolated_path: Path
    enriched_path: Path
    predictions_path: Path
    final_output_path: Path


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or "scenario"


def ensure_dirs() -> None:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)


def build_artifact_paths(run_id: str, scenario_name: str, filename: str) -> RunArtifacts:
    ensure_dirs()
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(filename).suffix or ".csv"
    scenario_slug = slugify(scenario_name)
    upload_path = UPLOADS_DIR / f"{run_id}_{scenario_slug}{suffix}"
    return RunArtifacts(
        upload_path=upload_path,
        interpolated_path=run_dir / f"{scenario_slug}_interpolated_grid.csv",
        enriched_path=run_dir / f"{scenario_slug}_engineered_features.csv",
        predictions_path=run_dir / f"{scenario_slug}_predictions.csv",
        final_output_path=run_dir / f"{scenario_slug}_coordinate_risk.csv",
    )


@lru_cache(maxsize=1)
def load_reference_grid() -> pd.DataFrame:
    grid = pd.read_csv(REFERENCE_GRID_PATH)
    grid["grid_latitude"] = pd.to_numeric(grid["grid_latitude"], errors="coerce").round(6)
    grid["grid_longitude"] = pd.to_numeric(grid["grid_longitude"], errors="coerce").round(6)
    return grid.dropna().drop_duplicates().reset_index(drop=True)


@lru_cache(maxsize=1)
def load_model_bundle() -> dict[str, Any]:
    with open(MODEL_DIR / "proxy_flood_model_info.json", "r", encoding="utf-8") as handle:
        metadata = json.load(handle)
    with open(MODEL_DIR / "xgb_like_model.pkl", "rb") as handle:
        xgb_like: GradientBoostedStumps = _load_legacy_pickle(handle)
    with open(MODEL_DIR / "random_forest_model.pkl", "rb") as handle:
        random_forest: RandomStumpForest = _load_legacy_pickle(handle)

    neural_net_bundle = torch.load(MODEL_DIR / "neural_net_model.pt", map_location="cpu", weights_only=False)
    feature_cols = metadata["features"]
    neural_net = TorchMLP(len(feature_cols))
    neural_net.load_state_dict(neural_net_bundle["state_dict"])
    neural_net.eval()

    return {
        "metadata": metadata,
        "feature_cols": feature_cols,
        "xgb_like": xgb_like,
        "random_forest": random_forest,
        "neural_net": neural_net,
        "means": np.array(neural_net_bundle["means"], dtype=np.float32),
        "stds": np.array(neural_net_bundle["stds"], dtype=np.float32),
    }


class _LegacyModelUnpickler(pickle.Unpickler):
    LEGACY_CLASS_MAP = {
        ("__main__", "GradientBoostedStumps"): GradientBoostedStumps,
        ("__main__", "RandomStumpForest"): RandomStumpForest,
    }

    def find_class(self, module: str, name: str):  # type: ignore[override]
        resolved = self.LEGACY_CLASS_MAP.get((module, name))
        if resolved is not None:
            return resolved
        return super().find_class(module, name)


def _load_legacy_pickle(handle) -> Any:
    return _LegacyModelUnpickler(handle).load()


def interpolate_to_grid(input_df: pd.DataFrame, target_grid: pd.DataFrame) -> pd.DataFrame:
    target_coords = target_grid[["grid_latitude", "grid_longitude"]].to_numpy(dtype=np.float64)
    all_frames: list[pd.DataFrame] = []

    for date_value, frame in input_df.groupby("date", sort=True):
        observed = (
            frame.groupby(["grid_latitude", "grid_longitude"], as_index=False)["precipitation_mm"]
            .mean()
            .sort_values(["grid_latitude", "grid_longitude"])
        )
        observed_coords = observed[["grid_latitude", "grid_longitude"]].to_numpy(dtype=np.float64)
        observed_rain = observed["precipitation_mm"].to_numpy(dtype=np.float64)

        if observed_coords.shape[0] == 0:
            raise ValueError(f"No valid coordinates found for date {date_value}.")

        distances = np.sqrt(((target_coords[:, None, :] - observed_coords[None, :, :]) ** 2).sum(axis=2))
        zero_mask = distances <= 1e-12

        weighted = np.empty(len(target_grid), dtype=np.float64)
        if zero_mask.any():
            exact_rows = zero_mask.any(axis=1)
            weighted[exact_rows] = observed_rain[zero_mask[exact_rows].argmax(axis=1)]
            remaining = ~exact_rows
        else:
            remaining = np.ones(len(target_grid), dtype=bool)

        if remaining.any():
            safe_dist = np.clip(distances[remaining], 1e-6, None)
            inverse = 1.0 / np.square(safe_dist)
            weights = inverse / inverse.sum(axis=1, keepdims=True)
            weighted[remaining] = weights @ observed_rain

        interpolated = target_grid.copy()
        interpolated["date"] = date_value
        interpolated["precipitation_mm"] = weighted.astype(np.float32)
        all_frames.append(interpolated)

    result = pd.concat(all_frames, ignore_index=True)
    return result[["date", "grid_latitude", "grid_longitude", "precipitation_mm"]]


def predict_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    bundle = load_model_bundle()
    feature_cols = bundle["feature_cols"]
    X_raw = df[feature_cols].fillna(0.0).to_numpy(dtype=np.float32)

    means = bundle["means"]
    stds = bundle["stds"].copy()
    stds[stds == 0] = 1.0
    X_scaled = (X_raw - means) / stds

    p_xgb = bundle["xgb_like"].predict_proba(X_raw)[:, 1]
    p_rf = bundle["random_forest"].predict_proba(X_raw)[:, 1]
    with torch.no_grad():
        logits = bundle["neural_net"](torch.tensor(X_scaled, dtype=torch.float32)).numpy()
    p_nn = sigmoid(logits)

    raw_weights = np.array([0.6, 0.3, 0.2], dtype=float)
    weights = raw_weights / raw_weights.sum()
    p_ensemble = weights[0] * p_xgb + weights[1] * p_rf + weights[2] * p_nn

    predictions = df.copy()
    predictions["pred_xgb_like"] = p_xgb
    predictions["pred_random_forest"] = p_rf
    predictions["pred_neural_net"] = p_nn
    predictions["risk"] = p_ensemble
    predictions["predicted_flood_label"] = (p_ensemble >= 0.5).astype(int)
    return predictions


def build_final_output(predictions: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    latest_date = str(pd.to_datetime(predictions["date"]).max().date())
    latest = (
        predictions[pd.to_datetime(predictions["date"]) == pd.to_datetime(latest_date)]
        .sort_values("risk", ascending=False)
        .reset_index(drop=True)
    )
    final_output = latest.rename(
        columns={"grid_latitude": "lat", "grid_longitude": "lon"}
    )[["lat", "lon", "risk"]]
    return final_output, latest_date


def summarize(final_output: pd.DataFrame, latest_date: str) -> dict[str, Any]:
    if final_output.empty:
        return {
            "latest_prediction_date": latest_date,
            "max_risk": 0.0,
            "mean_risk": 0.0,
            "high_risk_points": 0,
            "medium_risk_points": 0,
            "low_risk_points": 0,
            "top_points": [],
        }

    high = int((final_output["risk"] >= 0.66).sum())
    medium = int(((final_output["risk"] >= 0.33) & (final_output["risk"] < 0.66)).sum())
    low = int((final_output["risk"] < 0.33).sum())
    top_points = final_output.head(25).round(6).to_dict(orient="records")
    return {
        "latest_prediction_date": latest_date,
        "max_risk": float(final_output["risk"].max()),
        "mean_risk": float(final_output["risk"].mean()),
        "high_risk_points": high,
        "medium_risk_points": medium,
        "low_risk_points": low,
        "top_points": top_points,
    }


def run_pipeline(upload_path: Path, artifacts: RunArtifacts) -> dict[str, Any]:
    raw_input = pd.read_csv(upload_path)
    standardized = standardize_columns(raw_input)
    interpolated = interpolate_to_grid(standardized, load_reference_grid())
    enriched = add_static_features(add_inference_features(interpolated), MODEL_DIR)
    predictions = predict_dataframe(enriched)
    final_output, latest_date = build_final_output(predictions)
    summary = summarize(final_output, latest_date)

    interpolated.to_csv(artifacts.interpolated_path, index=False)
    enriched.to_csv(artifacts.enriched_path, index=False)
    predictions.to_csv(artifacts.predictions_path, index=False)
    final_output.to_csv(artifacts.final_output_path, index=False)

    return {
        "input_rows": int(len(standardized)),
        "interpolated_rows": int(len(interpolated)),
        "output_rows": int(len(final_output)),
        "latest_prediction_date": latest_date,
        "summary": summary,
        "final_output": final_output.round(6).to_dict(orient="records"),
    }
