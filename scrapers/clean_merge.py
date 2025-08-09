import pandas as pd
from functools import reduce
import numpy as np
from sklearn.preprocessing import StandardScaler

REGION_MAP = {
    "Addis  Abeba": "Oromia",
    "Afar": "Afar",
    "Amahara": "Amhara",
    "Amhara": "Amhara",
    "Benishangul Gumuz": "SNNP",
    "Dredewa": "Dire Dawa",
    "Gambella": "Gambella",
    "Harari": "Harari",
    "OROMIYA": "Oromia",
    "Oromiya": "Oromia",
    "SNNP": "SNNP",
    "SOMALE KILLIL": "Somali",
    "Tigray": "Tigray"
}

files = [
    "rainfall_features_per_crop_kebele_season.csv",
    "temperature_features_per_crop_kebele_season.csv",
    "soil_moisture_features_per_crop_kebele_season.csv",
    "ndvi_features_per_crop_kebele_season.csv"
]

dfs = []
for f in files:
    d = pd.read_csv(f)
    if "region" in d.columns:
        d["region"] = d["region"].map(REGION_MAP).fillna(d["region"])
    dfs.append(d)

df = reduce(lambda left, right: pd.merge(
    left, right, on=["crop", "region", "kebele", "year"], how="outer"), dfs)

# 3. Drop rows with >50% missing values
threshold = df.shape[1] / 2
df = df.dropna(thresh=threshold)

# 5. Ensure NDVI scaling is consistent
ndvi_cols = [c for c in df.columns if c.startswith("ndvi_") and "date" not in c]
for col in ndvi_cols:
    if df[col].max(skipna=True) > 1.5:
        df[col] = df[col] / 10000

# 6. Convert date features to day-of-year
date_cols = ["onset_date", "cessation_date"]
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.dayofyear
# Do NOT convert ndvi_start_of_season or ndvi_end_of_season again—they are already day-of-year integers.

# 7. Merge soil moisture columns if present
if "ssm" in df.columns or "sm_rootzone" in df.columns:
    df["soil_moisture_value"] = df[["ssm", "sm_rootzone"]].mean(axis=1, skipna=True)

# 8. Impute missing numeric values per crop–region
num_cols = df.select_dtypes(include=[np.number]).columns
df[num_cols] = df.groupby(["crop", "region"])[num_cols].transform(lambda g: g.fillna(g.median()))

# 9. Standardize continuous features
continuous_cols = [
    "seasonal_rainfall_total", "rainfall_std_dev", "rainy_days_count", "dry_spell_days",
    "mean_temp_season", "gdd_total", "heatwave_days",
    "mean_soil_moisture", "dry_soil_days", "soil_moisture_std",
    "ndvi_peak", "ndvi_seasonal_avg", "ndvi_anomaly_avg"
]
for col in continuous_cols:
    if col not in df.columns:
        df[col] = np.nan  # Ensure all columns exist for scaler

scaler = StandardScaler()
df[continuous_cols] = scaler.fit_transform(df[continuous_cols])

# 10. Encode categorical features (optional)
df = pd.get_dummies(df, columns=["crop", "region"], drop_first=True)

# 11. Save the cleaned dataset
df.to_csv("cleaned_master_features.csv", index=False)
print("✅ Cleaned dataset saved to cleaned_master_features.csv")