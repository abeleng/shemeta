# train_regression_per_cluster.py
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
import joblib

# ---------------------------
# 1. Load per-year dataset
# ---------------------------
per_year_file = "myclusters_per_year_with_cluster.csv"
print(f"Loading: {per_year_file}")
df = pd.read_csv(per_year_file)
print(f"Rows: {len(df)} Columns: {len(df.columns)}")

# ---------------------------
# 2. Choose target variable
# ---------------------------
target_var = "ndvi_integral"  # could be yield later
if target_var not in df.columns:
    raise ValueError(f"Target {target_var} not found in CSV")

# ---------------------------
# 3. Features selection
# ---------------------------
# Identify crop one-hot columns (same as in clustering code)
crop_cols = [c for c in df.columns if c.startswith("crop_")]

ndvi_cols = [
    "ndvi_peak", "ndvi_scale", "ndvi_seasonal_avg", "ndvi_start_of_season",
    "ndvi_end_of_season", "ndvi_threshold", "ndvi_anomaly_avg"
]
# Exclude IDs, categorical flags, and target
exclude_cols = ["kebele", "crop", "year", "data_quality_flag", "cluster"] + crop_cols + [target_var] + ndvi_cols
feature_cols = [c for c in df.columns if c not in exclude_cols]

print(f"Feature columns ({len(feature_cols)}): {feature_cols}")

# ---------------------------
# 4. Output dirs
# ---------------------------
models_dir = Path("models_regression")
models_dir.mkdir(exist_ok=True)

results = []

# ---------------------------
# 5. Train model per cluster
# ---------------------------
clusters = sorted(df["cluster"].unique())
for cl in clusters:
    cluster_df = df[df["cluster"] == cl].copy()
    print(f"\n=== Training cluster {cl} ({len(cluster_df)} rows) ===")

    X = cluster_df[feature_cols]
    y = cluster_df[target_var]

    if len(cluster_df) < 10:
        print(f"⚠️ Skipping cluster {cl} — not enough samples.")
        continue

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Pipeline: scale + RF regressor
    model = Pipeline(steps=[
        ("scaler", StandardScaler()),
        ("regressor", RandomForestRegressor(
            n_estimators=200,
            random_state=42
        ))
    ])

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print(f"Cluster {cl} → R²={r2:.3f} RMSE={rmse:.8f}")

    # Save model
    model_path = models_dir / f"regression_cluster_{cl}.joblib"
    joblib.dump(model, model_path)
    print(f"Saved model to {model_path}")

    # Save metrics
    results.append({
        "cluster": cl,
        "n_samples": len(cluster_df),
        "r2": r2,
        "rmse": rmse,
        "model_path": str(model_path)
    })

# ---------------------------
# 6. Save summary
# ---------------------------
results_df = pd.DataFrame(results)
results_df.to_csv("regression_per_cluster_summary.csv", index=False)
print("\n✅ All done. Results saved to regression_per_cluster_summary.csv")

print("\nTarget variable stats per cluster:")
print(df.groupby("cluster")[target_var].describe())
