"""
predict_new_data.py
-------------------
Run proxy flood-risk inference on new data using the saved ensemble.

Expected input columns:
  - date
  - lat or grid_latitude
  - lon or grid_longitude
  - rainfall or precipitation_mm

The script computes the required rainfall/time features per grid cell, loads the
saved ensemble, and writes prediction probabilities plus the final label.
"""

from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


class GradientBoostedStumps:
    def predict_proba(self, X):
        raw = np.full(X.shape[0], self.base_score, dtype=np.float32)
        for stump in self.stumps:
            col = X[:, stump["feature"]]
            update = np.where(col <= stump["threshold"], stump["left_val"], stump["right_val"])
            raw += self.learning_rate * update
        prob = sigmoid(raw)
        return np.column_stack([1 - prob, prob])


class RandomStumpForest:
    def predict_proba(self, X):
        preds = []
        for stump in self.stumps:
            col = X[:, stump["feature"]]
            raw = np.where(col <= stump["threshold"], stump["left_val"], stump["right_val"])
            preds.append(sigmoid(raw))
        prob = np.mean(np.array(preds, dtype=np.float32), axis=0)
        return np.column_stack([1 - prob, prob])


class TorchMLP(nn.Module):
    def __init__(self, in_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(1)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    if "lat" in df.columns:
        rename_map["lat"] = "grid_latitude"
    if "lon" in df.columns:
        rename_map["lon"] = "grid_longitude"
    if "rainfall" in df.columns:
        rename_map["rainfall"] = "precipitation_mm"
    df = df.rename(columns=rename_map).copy()

    required = {"date", "grid_latitude", "grid_longitude", "precipitation_mm"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df["grid_latitude"] = pd.to_numeric(df["grid_latitude"], errors="coerce").round(6)
    df["grid_longitude"] = pd.to_numeric(df["grid_longitude"], errors="coerce").round(6)
    df["precipitation_mm"] = pd.to_numeric(df["precipitation_mm"], errors="coerce").fillna(0.0)
    df = df.dropna(subset=["grid_latitude", "grid_longitude"]).copy()
    return df


def add_inference_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["grid_latitude", "grid_longitude", "date"]).copy()
    grp = df.groupby(["grid_latitude", "grid_longitude"], sort=False)

    df["lag1"] = grp["precipitation_mm"].shift(1)
    df["lag2"] = grp["precipitation_mm"].shift(2)
    df["lag3"] = grp["precipitation_mm"].shift(3)

    roll3 = grp["precipitation_mm"].rolling(3, min_periods=1)
    roll5 = grp["precipitation_mm"].rolling(5, min_periods=1)
    roll7 = grp["precipitation_mm"].rolling(7, min_periods=1)
    df["rain_3d"] = roll3.sum().reset_index(level=[0, 1], drop=True)
    df["rain_5d"] = roll5.sum().reset_index(level=[0, 1], drop=True)
    df["rain_7d"] = roll7.sum().reset_index(level=[0, 1], drop=True)
    df["cumulative_rainfall"] = grp["precipitation_mm"].cumsum()
    df["average_intensity"] = roll3.mean().reset_index(level=[0, 1], drop=True)
    df["trend"] = df["precipitation_mm"] - df["average_intensity"]

    dt = pd.to_datetime(df["date"])
    month = dt.dt.month
    df["month"] = month
    df["month_sin"] = np.sin(2 * np.pi * month / 12.0)
    df["month_cos"] = np.cos(2 * np.pi * month / 12.0)
    season_map = {12: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2, 9: 2, 10: 3, 11: 3}
    df["seasonal_encoder"] = month.map(season_map).astype(int)
    return df


def add_static_features(df: pd.DataFrame, model_dir: Path) -> pd.DataFrame:
    static_df = pd.read_csv(model_dir / "coordinate_static_features.csv")
    static_df["grid_latitude"] = pd.to_numeric(static_df["grid_latitude"], errors="coerce").round(6)
    static_df["grid_longitude"] = pd.to_numeric(static_df["grid_longitude"], errors="coerce").round(6)
    return df.merge(static_df, on=["grid_latitude", "grid_longitude"], how="left")


def main():
    parser = argparse.ArgumentParser(description="Predict proxy flood risk on new rainfall data.")
    parser.add_argument("--input", required=True, help="CSV with date, lat/lon, rainfall.")
    parser.add_argument("--model-dir", default="proxy_flood_model", help="Folder containing saved model artifacts.")
    parser.add_argument("--output", required=True, help="Output CSV path for predictions.")
    args = parser.parse_args()

    model_dir = Path(args.model_dir)
    df = pd.read_csv(args.input)
    df = standardize_columns(df)
    df = add_inference_features(df)
    df = add_static_features(df, model_dir)

    with open(model_dir / "proxy_flood_model_info.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    feature_cols = meta["features"]

    X_raw = df[feature_cols].fillna(0.0).to_numpy(dtype=np.float32)

    with open(model_dir / "xgb_like_model.pkl", "rb") as f:
        xgb_like = pickle.load(f)
    with open(model_dir / "random_forest_model.pkl", "rb") as f:
        rf = pickle.load(f)

    nn_bundle = torch.load(model_dir / "neural_net_model.pt", map_location="cpu", weights_only=False)
    means = np.array(nn_bundle["means"], dtype=np.float32)
    stds = np.array(nn_bundle["stds"], dtype=np.float32)
    X_scaled = (X_raw - means) / stds

    nn_model = TorchMLP(len(feature_cols))
    nn_model.load_state_dict(nn_bundle["state_dict"])
    nn_model.eval()

    p_xgb = xgb_like.predict_proba(X_raw)[:, 1]
    p_rf = rf.predict_proba(X_raw)[:, 1]
    with torch.no_grad():
        logits = nn_model(torch.tensor(X_scaled, dtype=torch.float32)).numpy()
    p_nn = sigmoid(logits)

    raw_weights = np.array([0.6, 0.3, 0.2], dtype=float)
    weights = raw_weights / raw_weights.sum()
    p_ens = weights[0] * p_xgb + weights[1] * p_rf + weights[2] * p_nn
    pred = (p_ens >= 0.5).astype(int)

    out = df[["date", "grid_latitude", "grid_longitude", "precipitation_mm"]].copy()
    out["pred_xgb_like"] = p_xgb
    out["pred_random_forest"] = p_rf
    out["pred_neural_net"] = p_nn
    out["pred_ensemble"] = p_ens
    out["predicted_flood_label"] = pred
    out.to_csv(args.output, index=False)

    print("=" * 60)
    print("Prediction complete")
    print(f"Input rows : {len(df):,}")
    print(f"Saved -> {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()
