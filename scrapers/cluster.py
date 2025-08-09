#!/usr/bin/env python3
"""
cluster_kebele_crop.py

Aggregates per-(kebele,crop,year) seasonal features into per-(kebele,crop) profiles,
scales features, searches for a good K with silhouette score, fits KMeans, and saves outputs.

Outputs:
- {out_prefix}_kebele_crop_clusters.csv      : aggregated rows with cluster labels
- {out_prefix}_cluster_summary.csv           : cluster medians & counts for interpretation
- {out_prefix}_per_year_with_cluster.csv     : original per-year rows annotated with cluster
- models/{out_prefix}_scaler.joblib
- models/{out_prefix}_kmeans.joblib
"""

import argparse
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import joblib

def detect_crop_column(df):
    """Return (df, crop_col_name).  If crop one-hot columns exist, create single 'crop' column."""
    # If a plain 'crop' column exists, use it
    if 'crop' in df.columns:
        return df, 'crop'

    # Find one-hot crop columns starting with 'crop_'
    crop_cols = [c for c in df.columns if c.startswith('crop_')]
    if not crop_cols:
        # Nothing found
        raise ValueError("No 'crop' column found and no columns starting with 'crop_'. "
                         "Please include a crop column or crop one-hot columns.")
    # Convert crop_cols to numeric if possible (True/False, 1/0, 'True'/'False')
    # Create 'crop' by taking the one-hot column with the highest value per row.
    # We'll coerce to numeric (True->1, False->0, 'False'->NaN->0)
    crop_df = df[crop_cols].copy()

    # Coerce booleans/strings to numeric 0/1
    for col in crop_cols:
        crop_df[col] = pd.to_numeric(crop_df[col].replace({True:1, False:0, 'True':1, 'False':0}), errors='coerce').fillna(0)

    # If row has all zeros (no one-hot flagged), leave crop as 'unknown'
    def row_to_crop(row):
        if row.sum() == 0:
            return 'unknown'
        # idxmax returns first max if ties
        return crop_cols[int(row.values.argmax())].replace('crop_', '')

    df['crop'] = crop_df.apply(row_to_crop, axis=1)
    return df, 'crop'

def ensure_ndvi_scale(df):
    """If any NDVI column has max > 1.5, divide those columns by 10000."""
    ndvi_cols = [c for c in df.columns if c.lower().startswith('ndvi_')]
    for col in ndvi_cols:
        try:
            if df[col].max(skipna=True) > 1.5:
                df[col] = df[col] / 10000.0
                print(f"Normalized NDVI column {col} by dividing by 10000.")
        except Exception:
            # If non-numeric, skip
            continue
    return df

def unify_soil_moisture(df):
    """If either 'ssm' or 'sm_rootzone' exist, create unified 'soil_moisture_value' (mean of both)."""
    cols = []
    if 'ssm' in df.columns:
        cols.append('ssm')
    if 'sm_rootzone' in df.columns:
        cols.append('sm_rootzone')
    # also some pipeline/gee variants may use 'soil_moisture_value'
    if 'soil_moisture_value' in df.columns:
        cols.append('soil_moisture_value')

    cols = list(dict.fromkeys(cols))  # unique
    if cols:
        if len(cols) == 1:
            df['soil_moisture_value'] = pd.to_numeric(df[cols[0]], errors='coerce')
        else:
            df['soil_moisture_value'] = pd.to_numeric(df[cols], errors='coerce').mean(axis=1)
        print(f"Unified soil moisture columns {cols} -> 'soil_moisture_value'")
    return df

def convert_date_like_to_doy(df, date_cols):
    """For each column in date_cols present in df, convert to day-of-year numeric.
       If already numeric, coerces to numeric."""
    for col in date_cols:
        if col in df.columns:
            # Try parse then convert to dayofyear; if values already numeric (1..365) then keep numeric
            try:
                parsed = pd.to_datetime(df[col], errors='coerce')
                if parsed.notna().any():
                    df[col] = parsed.dt.dayofyear
                else:
                    # Coerce numeric strings to numeric
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            except Exception:
                df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def select_feature_columns(df, exclude_prefixes=None, exclude_exact=None):
    exclude_prefixes = exclude_prefixes or []
    exclude_exact = exclude_exact or []
    cols = []
    for c in df.columns:
        if c in exclude_exact:
            continue
        if any([c.startswith(p) for p in exclude_prefixes]):
            continue
        cols.append(c)
    return cols

def aggregate_per_kebele_crop(df, features, min_years=3):
    group = df.groupby(['kebele', 'crop'])
    n_years = group.size().rename('n_years').reset_index()
    # Filter kebele-crop pairs with at least min_years rows
    qualified = n_years[n_years['n_years'] >= min_years][['kebele','crop']]
    if qualified.empty:
        raise ValueError(f"No kebele-crop groups found with min_years >= {min_years}. Reduce min_years.")

    # Restrict df to qualified groups
    merged = pd.merge(df, qualified, on=['kebele','crop'], how='inner')

    # Compute mean & std per feature
    agg_mean = merged.groupby(['kebele','crop'])[features].mean().add_suffix('_mean')
    agg_std  = merged.groupby(['kebele','crop'])[features].std().add_suffix('_std').fillna(0.0)
    agg_n = merged.groupby(['kebele','crop']).size().rename('n_years')

    agg = pd.concat([agg_mean, agg_std, agg_n], axis=1).reset_index()
    return agg

def scale_features(agg_df, feature_cols):
    scaler = StandardScaler()
    X = agg_df[feature_cols].values
    X_scaled = scaler.fit_transform(X)
    return X_scaled, scaler

def find_best_k(X_scaled, k_min=2, k_max=12, random_state=42):
    n_samples = X_scaled.shape[0]
    if n_samples < 2:
        raise ValueError("Not enough samples to cluster (need >=2).")
    k_max = min(k_max, n_samples - 1)
    best_k = None
    best_score = -1.0
    best_labels = None
    for k in range(k_min, max(k_min, k_max) + 1):
        try:
            km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
            labels = km.fit_predict(X_scaled)
            score = silhouette_score(X_scaled, labels)
            print(f"k={k} silhouette={score:.4f}")
            if score > best_score:
                best_score = score
                best_k = k
                best_labels = labels
        except Exception as e:
            print(f"skipping k={k} because error: {e}")
            continue
    if best_k is None:
        raise RuntimeError("Failed to find a valid k. Try different range or settings.")
    print(f"Selected best_k={best_k} with silhouette={best_score:.4f}")
    return best_k

def fit_kmeans_and_assign(X_scaled, agg_df, feature_cols_scaled, k, random_state=42):
    kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    agg_df['cluster'] = labels
    return kmeans, agg_df

def save_models(scaler, kmeans, out_prefix):
    os.makedirs('models', exist_ok=True)
    joblib.dump(scaler, os.path.join('models', f'{out_prefix}_scaler.joblib'))
    joblib.dump(kmeans, os.path.join('models', f'{out_prefix}_kmeans.joblib'))
    print(f"Saved models to models/{out_prefix}_*.joblib")

def main(
    input_path,
    min_years=3,
    k_min=2,
    k_max=12,
    out_prefix='kebele_crop',
    random_state=42
):
    print("Loading:", input_path)
    df = pd.read_csv(input_path)
    print("Rows:", len(df), "Columns:", len(df.columns))

    # Derive crop if needed
    df, crop_col = detect_crop_column(df)

    # Basic sanity: require kebele, year, crop
    if 'kebele' not in df.columns:
        raise ValueError("Input CSV must include 'kebele' column.")
    if 'year' not in df.columns:
        print("Warning: 'year' not found. Proceeding; aggregation will use available rows.")

    # Normalize / clean NDVI and soil moisture
    df = ensure_ndvi_scale(df)
    df = unify_soil_moisture(df)

    # Convert some likely date columns to day-of-year numeric
    date_cols = ['onset_date', 'cessation_date', 'ndvi_start_of_season', 'ndvi_end_of_season']
    df = convert_date_like_to_doy(df, date_cols)

    # Exclude identifiers & crop one-hots & quality flags from clustering features
    crop_onehots = [c for c in df.columns if c.startswith('crop_')]
    exclude_cols = set(['kebele', 'year', 'data_quality_flag', crop_col] + crop_onehots)
    # Also exclude non-numeric columns automatically:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # but keep soil_moisture_value if numeric
    feature_candidates = [c for c in numeric_cols if c not in exclude_cols]

    if not feature_candidates:
        raise ValueError("No numeric feature columns found for clustering. Check the input CSV.")

    print("Feature candidates (numeric) for aggregation:", feature_candidates)

    # Aggregate per kebele-crop
    agg_df = aggregate_per_kebele_crop(df, feature_candidates, min_years=min_years)
    print("Aggregated rows (kebele,crop):", len(agg_df))

    # Feature columns after aggregation are feature_mean and feature_std. We'll use both.
    feature_cols = []
    for f in feature_candidates:
        feature_cols.append(f + '_mean')
        feature_cols.append(f + '_std')
    # Ensure these columns exist (std might be missing if very few rows -> it was filled as 0)
    feature_cols = [c for c in feature_cols if c in agg_df.columns]

    # Keep a copy of original aggregated (unscaled) columns for interpretation
    unscaled_features = feature_cols.copy()

    # Scale
    X_scaled, scaler = scale_features(agg_df, unscaled_features)

    # Determine best K
    n_samples = X_scaled.shape[0]
    if n_samples <= k_min:
        k_min = 2
    k_max = min(k_max, n_samples - 1)
    if k_min >= k_max:
        k_min = 2
        k_max = max(2, n_samples - 1)

    best_k = find_best_k(X_scaled, k_min=k_min, k_max=k_max, random_state=random_state)

    # Fit final KMeans and add cluster labels
    kmeans, agg_df_with_cluster = fit_kmeans_and_assign(X_scaled, agg_df, unscaled_features, best_k, random_state=random_state)
    print("Cluster counts:\n", agg_df_with_cluster['cluster'].value_counts())

    # Save aggregated clusters CSV
    out_clusters_fn = f"{out_prefix}_kebele_crop_clusters.csv"
    agg_df_with_cluster.to_csv(out_clusters_fn, index=False)
    print(f"Saved aggregated clusters to {out_clusters_fn}")

    # Save per-year rows annotated with cluster (join back)
    per_year_with_cluster = pd.merge(df, agg_df_with_cluster[['kebele','crop','cluster']], on=['kebele','crop'], how='left')
    out_per_year = f"{out_prefix}_per_year_with_cluster.csv"
    per_year_with_cluster.to_csv(out_per_year, index=False)
    print(f"Saved per-year annotated CSV to {out_per_year}")

    # Save model artifacts
    save_models(scaler, kmeans, out_prefix)

    # Save cluster summary for interpretation: median of original aggregated (unscaled) features per cluster
    cluster_summary = agg_df_with_cluster.groupby('cluster')[unscaled_features + ['n_years']].median()
    cluster_summary = cluster_summary.reset_index()
    out_summary = f"{out_prefix}_cluster_summary.csv"
    cluster_summary.to_csv(out_summary, index=False)
    print(f"Saved cluster summary to {out_summary}")

    print("Done.")

if __name__ == "__main__":
    # Example usage:
    # main("cleaned_master_features.csv", min_years=3, k_min=2, k_max=8, out_prefix="myclusters")
    main(
        "cleaned_master_features.csv",  # input_path
        3,                              # min_years
        2,                              # k_min
        8,                              # k_max
        "myclusters",                   # out_prefix
        42                              # random_state
    )
