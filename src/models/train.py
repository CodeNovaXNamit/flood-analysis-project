"""
train_proxy_flood_risk_model.py
-------------------------------
Train a proxy flood-risk ensemble using only local libraries available in this
environment.

Ensemble components:
  - xgb_like: custom gradient-boosted stumps
  - random_forest: custom bagged random stumps
  - neural_net: PyTorch MLP

Requested weights were 0.6, 0.3, 0.2. These sum to 1.1, so the script
normalizes them before blending.
"""

from __future__ import annotations

import argparse
import json
import math
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from scipy.stats import rankdata
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


def minmax(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    s_min = s.min()
    s_max = s.max()
    if pd.isna(s_min) or pd.isna(s_max) or s_max == s_min:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - s_min) / (s_max - s_min)


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


def roc_auc_manual(y_true: np.ndarray, y_score: np.ndarray) -> float:
    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score).astype(float)
    pos = y_true == 1
    neg = y_true == 0
    n_pos = pos.sum()
    n_neg = neg.sum()
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    ranks = rankdata(y_score)
    auc = (ranks[pos].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
    return float(auc)


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


def classification_report_manual(y_true: np.ndarray, y_pred: np.ndarray) -> str:
    lines = []
    for cls in [0, 1]:
        tp = np.sum((y_true == cls) & (y_pred == cls))
        fp = np.sum((y_true != cls) & (y_pred == cls))
        fn = np.sum((y_true == cls) & (y_pred != cls))
        support = np.sum(y_true == cls)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        lines.append(
            f"class {cls}: precision={precision:.4f} recall={recall:.4f} f1={f1:.4f} support={support}"
        )
    lines.append(f"accuracy: {accuracy_manual(y_true, y_pred):.4f}")
    return "\n".join(lines)


def build_proxy_target(df: pd.DataFrame) -> pd.DataFrame:
    rain_now = minmax(df["precipitation_mm"])
    rain_3d = minmax(df["rain_3d"])
    rain_7d = minmax(df["rain_7d"])
    runoff = minmax(df["runoff_value"])
    runoff_poor = minmax(1.0 - df["runoff_coefficient"])
    low_elev = 1.0 - minmax(df["elevation_m"])
    low_drainage = 1.0 - minmax(df["drainage_density_km_per_km2"])
    low_slope = 1.0 - minmax(df["slope"])
    population = minmax(df["total_population"])

    score = (
        0.10 * rain_now +
        0.20 * rain_3d +
        0.25 * rain_7d +
        0.15 * runoff +
        0.10 * runoff_poor +
        0.07 * low_elev +
        0.05 * low_drainage +
        0.03 * low_slope +
        0.05 * population
    )

    threshold = float(score.quantile(0.95))
    df = df.copy()
    df["proxy_flood_risk_score"] = score
    df["proxy_flood_label"] = (score >= threshold).astype(int)
    return df


def get_feature_columns() -> list[str]:
    return [
        "grid_latitude",
        "grid_longitude",
        "precipitation_mm",
        "lag1",
        "lag2",
        "lag3",
        "rain_3d",
        "rain_5d",
        "rain_7d",
        "cumulative_rainfall",
        "average_intensity",
        "trend",
        "runoff_value",
        "runoff_coefficient",
        "elevation_m",
        "drainage_density_km_per_km2",
        "total_population",
        "slope",
        "month_sin",
        "month_cos",
        "seasonal_encoder",
    ]


def temporal_split(df: pd.DataFrame, test_fraction: float = 0.2) -> tuple[pd.DataFrame, pd.DataFrame]:
    dates = np.array(sorted(pd.to_datetime(df["date"]).unique()))
    split_idx = max(1, int(len(dates) * (1.0 - test_fraction)))
    split_date = dates[split_idx]
    train_df = df[pd.to_datetime(df["date"]) < split_date].copy()
    test_df = df[pd.to_datetime(df["date"]) >= split_date].copy()
    return train_df, test_df


def prepare_arrays(df: pd.DataFrame, feature_cols: list[str], means=None, stds=None):
    X = df[feature_cols].copy()
    X = X.fillna(0.0).to_numpy(dtype=np.float32)
    if means is None:
        means = X.mean(axis=0)
    if stds is None:
        stds = X.std(axis=0)
        stds[stds == 0] = 1.0
    Xs = (X - means) / stds
    return X, Xs, means, stds


def fit_best_stump(X, target, feature_indices=None):
    n_samples, n_features = X.shape
    if feature_indices is None:
        feature_indices = range(n_features)

    best = None
    best_loss = float("inf")

    for j in feature_indices:
        col = X[:, j]
        quantiles = np.unique(np.quantile(col, [0.15, 0.3, 0.5, 0.7, 0.85]))
        for thr in quantiles:
            left = col <= thr
            right = ~left
            if left.sum() < 5 or right.sum() < 5:
                continue
            left_val = float(target[left].mean())
            right_val = float(target[right].mean())
            pred = np.where(left, left_val, right_val)
            loss = float(np.mean((target - pred) ** 2))
            if loss < best_loss:
                best_loss = loss
                best = {
                    "feature": int(j),
                    "threshold": float(thr),
                    "left_val": left_val,
                    "right_val": right_val,
                }

    if best is None:
        mean_val = float(np.mean(target))
        best = {"feature": 0, "threshold": 0.0, "left_val": mean_val, "right_val": mean_val}
    return best


def stump_predict(stump, X):
    col = X[:, stump["feature"]]
    return np.where(col <= stump["threshold"], stump["left_val"], stump["right_val"])


class GradientBoostedStumps:
    def __init__(self, n_estimators=30, learning_rate=0.2):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.base_score = 0.0
        self.stumps = []

    def fit(self, X, y):
        p = np.clip(y.mean(), 1e-5, 1 - 1e-5)
        self.base_score = float(math.log(p / (1 - p)))
        raw = np.full(len(y), self.base_score, dtype=np.float32)

        for _ in range(self.n_estimators):
            prob = sigmoid(raw)
            residual = y - prob
            stump = fit_best_stump(X, residual)
            update = stump_predict(stump, X)
            raw += self.learning_rate * update
            self.stumps.append(stump)

    def predict_proba(self, X):
        raw = np.full(X.shape[0], self.base_score, dtype=np.float32)
        for stump in self.stumps:
            raw += self.learning_rate * stump_predict(stump, X)
        prob = sigmoid(raw)
        return np.column_stack([1 - prob, prob])


class RandomStumpForest:
    def __init__(self, n_estimators=200, max_features=5, random_state=42):
        self.n_estimators = n_estimators
        self.max_features = max_features
        self.random_state = random_state
        self.stumps = []

    def fit(self, X, y):
        rng = np.random.default_rng(self.random_state)
        n_samples, n_features = X.shape
        self.stumps = []

        for _ in range(self.n_estimators):
            sample_idx = rng.integers(0, n_samples, size=n_samples)
            feat_idx = rng.choice(n_features, size=min(self.max_features, n_features), replace=False)
            stump = fit_best_stump(X[sample_idx], y[sample_idx], feature_indices=feat_idx)
            self.stumps.append(stump)

    def predict_proba(self, X):
        preds = np.array([sigmoid(stump_predict(stump, X)) for stump in self.stumps], dtype=np.float32)
        prob = preds.mean(axis=0)
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


def train_torch_mlp(X_train, y_train, X_val, epochs=8, batch_size=4096):
    device = torch.device("cpu")
    model = TorchMLP(X_train.shape[1]).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.BCEWithLogitsLoss()

    ds = TensorDataset(torch.tensor(X_train), torch.tensor(y_train.astype(np.float32)))
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True)

    model.train()
    for _ in range(epochs):
        for xb, yb in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            optimizer.zero_grad()
            logits = model(xb)
            loss = loss_fn(logits, yb)
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        logits = model(torch.tensor(X_val, dtype=torch.float32, device=device)).cpu().numpy()
    prob = sigmoid(logits)
    return model, prob


def main():
    parser = argparse.ArgumentParser(description="Train a proxy flood-risk ensemble model.")
    parser.add_argument("--input", required=True, help="Engineered feature CSV.")
    parser.add_argument("--output-dir", required=True, help="Folder for model artifacts and predictions.")
    parser.add_argument("--train-sample", type=int, default=200000, help="Maximum sampled training rows.")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  Train Proxy Flood Risk Model")
    print("=" * 60)

    df = pd.read_csv(args.input)
    df = build_proxy_target(df)
    feature_cols = get_feature_columns()

    train_df, test_df = temporal_split(df)
    rng = np.random.default_rng(42)
    if len(train_df) > args.train_sample:
        pos = train_df[train_df["proxy_flood_label"] == 1]
        neg = train_df[train_df["proxy_flood_label"] == 0]
        pos_n = min(len(pos), args.train_sample // 2)
        neg_n = args.train_sample - pos_n
        train_df = pd.concat(
            [
                pos.sample(pos_n, random_state=42),
                neg.sample(min(len(neg), neg_n), random_state=42),
            ],
            ignore_index=True,
        ).sample(frac=1.0, random_state=42).reset_index(drop=True)

    print(f"\nTrain rows used: {len(train_df):,}")
    print(f"Test rows      : {len(test_df):,}")

    X_train_raw, X_train_scaled, means, stds = prepare_arrays(train_df, feature_cols)
    X_test_raw, X_test_scaled, _, _ = prepare_arrays(test_df, feature_cols, means=means, stds=stds)
    y_train = train_df["proxy_flood_label"].to_numpy(dtype=np.float32)
    y_test = test_df["proxy_flood_label"].to_numpy(dtype=np.int32)

    print("\nTraining xgb-like boosted stumps...")
    xgb_like = GradientBoostedStumps(n_estimators=35, learning_rate=0.25)
    xgb_like.fit(X_train_raw, y_train)
    p_xgb = xgb_like.predict_proba(X_test_raw)[:, 1]

    print("Training random-forest-like stump ensemble...")
    rf = RandomStumpForest(n_estimators=220, max_features=5, random_state=42)
    rf.fit(X_train_raw, y_train)
    p_rf = rf.predict_proba(X_test_raw)[:, 1]

    print("Training neural net...")
    nn_model, p_nn = train_torch_mlp(X_train_scaled, y_train, X_test_scaled)

    raw_weights = np.array([0.6, 0.3, 0.2], dtype=float)
    weights = raw_weights / raw_weights.sum()
    ensemble_prob = weights[0] * p_xgb + weights[1] * p_rf + weights[2] * p_nn
    ensemble_pred = (ensemble_prob >= 0.5).astype(int)

    metrics = {
        "blend_weights_normalized": {
            "xgb_like": float(weights[0]),
            "random_forest": float(weights[1]),
            "neural_net": float(weights[2]),
        },
        "roc_auc": roc_auc_manual(y_test, ensemble_prob),
        "f1": f1_manual(y_test, ensemble_pred),
        "accuracy": accuracy_manual(y_test, ensemble_pred),
    }

    print("\nMetrics:")
    print(json.dumps(metrics, indent=2))

    pred_cols = [
        "date",
        "grid_latitude",
        "grid_longitude",
        "ward_name",
        "ward_code",
        "proxy_flood_risk_score",
        "proxy_flood_label",
    ]
    predictions = test_df[pred_cols].copy()
    predictions["pred_xgb_like"] = p_xgb
    predictions["pred_random_forest"] = p_rf
    predictions["pred_neural_net"] = p_nn
    predictions["pred_ensemble"] = ensemble_prob
    predictions["predicted_flood_label"] = ensemble_pred
    predictions.to_csv(out_dir / "proxy_flood_predictions.csv", index=False)

    df.to_csv(out_dir / "proxy_flood_training_dataset.csv", index=False)
    with open(out_dir / "proxy_flood_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    with open(out_dir / "proxy_flood_classification_report.txt", "w", encoding="utf-8") as f:
        f.write(classification_report_manual(y_test, ensemble_pred))

    with open(out_dir / "xgb_like_model.pkl", "wb") as f:
        pickle.dump(xgb_like, f)
    with open(out_dir / "random_forest_model.pkl", "wb") as f:
        pickle.dump(rf, f)
    torch.save(
        {
            "state_dict": nn_model.state_dict(),
            "means": means,
            "stds": stds,
            "feature_cols": feature_cols,
        },
        out_dir / "neural_net_model.pt",
    )

    meta = {
        "features": feature_cols,
        "target": "proxy_flood_label",
        "note": "Proxy target derived heuristically from rainfall, runoff, elevation, drainage, slope, and population.",
        "model_note": "xgboost, sklearn forests, and xgboost package were unavailable; local custom ensemble components were used instead.",
    }
    with open(out_dir / "proxy_flood_model_info.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    static_cols = [
        "grid_latitude",
        "grid_longitude",
        "runoff_value",
        "runoff_coefficient",
        "elevation_m",
        "drainage_density_km_per_km2",
        "total_population",
        "slope",
    ]
    df[static_cols].drop_duplicates().to_csv(out_dir / "coordinate_static_features.csv", index=False)

    print(f"\nSaved artifacts in -> {out_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
