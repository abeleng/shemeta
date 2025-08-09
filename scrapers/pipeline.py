import json
import sys
import os
import pandas as pd
import glob
import numpy as np
from scipy.stats import skew
# Import the main scrape functions from gee.py
from gee import (
    scrape_precipitation_data,
    scrape_temperature_data,
    scrape_soil_moisture_data,
    scrape_ndvi_data,
    # scrape_drought_indices
)


def get_combined_crop_calendar():
    # Load the combined crop calendar JSON
    with open('data/combined_crop_calendar.json', encoding='utf-8') as f:
        combined_crop_calendar = json.load(f)

    # Store as a dictionary for further processing
    # If you want to index by (crop name, region), you can do:
    crop_region_dict = {}
    for entry in combined_crop_calendar:
        crop_name = entry['crop']['name']
        region = entry['region']
        crop_region_dict[(crop_name, region)] = entry

    return crop_region_dict

def load_gee_data(max_kebeles=10):
    """
    Runs all main GEE scraping functions in sequence.
    """
    print("▶ Running precipitation scraper...")
    scrape_precipitation_data(max_kebeles=max_kebeles)
    print("▶ Running temperature scraper...")
    scrape_temperature_data(max_kebeles=max_kebeles)
    print("▶ Running soil moisture scraper...")
    scrape_soil_moisture_data(max_kebales=max_kebeles)
    print("▶ Running NDVI scraper...")
    scrape_ndvi_data(max_kebales=max_kebeles)
    # print("▶ Running drought indices calculation...")
    # scrape_drought_indices()
    print("✅ All GEE data scraping completed.")

# Region normalization mapping
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




def load_precipitation_timeseries():
    precip_dir = os.path.join("scraped_data", "precipitation")
    csv_files = glob.glob(os.path.join(precip_dir, "*_precipitation_timeseries.csv"))
    data = {}
    for csv_path in csv_files:
        df = pd.read_csv(csv_path)
        # Normalize region if present
        if "REGION" in df.columns:
            df["REGION"] = df["REGION"].map(REGION_MAP).fillna(df["REGION"])
        elif "Region" in df.columns:
            df["Region"] = df["Region"].map(REGION_MAP).fillna(df["Region"])
        # Extract GlobalID from filename
        unique_id = os.path.basename(csv_path).replace("_precipitation_timeseries.csv", "")
        data[unique_id] = df
    return data

def load_temperature_timeseries():
    temp_dir = os.path.join("scraped_data", "temperature")
    csv_files = glob.glob(os.path.join(temp_dir, "*_temperature_timeseries.csv"))
    data = {}
    for csv_path in csv_files:
        df = pd.read_csv(csv_path)
        if "REGION" in df.columns:
            df["REGION"] = df["REGION"].map(REGION_MAP).fillna(df["REGION"])
        elif "Region" in df.columns:
            df["Region"] = df["Region"].map(REGION_MAP).fillna(df["Region"])
        elif "R_NAME" in df.columns:
            df["R_NAME"] = df["R_NAME"].map(REGION_MAP).fillna(df["R_NAME"])
        unique_id = os.path.basename(csv_path).replace("_temperature_timeseries.csv", "")
        data[unique_id] = df
    return data

def load_soil_moisture_timeseries():
    soil_dir = os.path.join("scraped_data", "soil_moisture")
    csv_files = glob.glob(os.path.join(soil_dir, "*_soil_moisture_timeseries.csv"))
    data = {}
    for csv_path in csv_files:
        df = pd.read_csv(csv_path)
        if "REGION" in df.columns:
            df["REGION"] = df["REGION"].map(REGION_MAP).fillna(df["REGION"])
        elif "Region" in df.columns:
            df["Region"] = df["Region"].map(REGION_MAP).fillna(df["Region"])
        elif "R_NAME" in df.columns:
            df["R_NAME"] = df["R_NAME"].map(REGION_MAP).fillna(df["R_NAME"])
        unique_id = os.path.basename(csv_path).replace("_soil_moisture_timeseries.csv", "")
        data[unique_id] = df
    return data

def load_ndvi_timeseries():
    ndvi_dir = os.path.join("scraped_data", "ndvi")
    csv_files = glob.glob(os.path.join(ndvi_dir, "*_ndvi_timeseries.csv"))
    data = {}
    for csv_path in csv_files:
        df = pd.read_csv(csv_path)
        if "REGION" in df.columns:
            df["REGION"] = df["REGION"].map(REGION_MAP).fillna(df["REGION"])
        elif "Region" in df.columns:
            df["Region"] = df["Region"].map(REGION_MAP).fillna(df["Region"])
        elif "R_NAME" in df.columns:
            df["R_NAME"] = df["R_NAME"].map(REGION_MAP).fillna(df["R_NAME"])
        if "NDVI" in df.columns and df["NDVI"].max() > 1.5:
            df["NDVI"] = df["NDVI"] / 10000
        unique_id = os.path.basename(csv_path).replace("_ndvi_timeseries.csv", "")
        data[unique_id] = df
    return data

def compute_rainfall_features(crop_calendar, rainfall_data):
    """
    For each crop-region and kebele, compute rainfall features for each season.
    Uses data-driven thresholds for onset, rainy day, and dry spell.
    """
    results = []
    for (crop_name, region), entry in crop_calendar.items():
        region = REGION_MAP.get(region, region)
        sessions = entry.get("sessions", [])
        for session in sessions:
            sow_month = int(session["early_sowing"]["month"])
            sow_day = int(session["early_sowing"]["day"])
            harv_month = int(session["late_harvest"]["month"])
            harv_day = int(session["late_harvest"]["day"])
            for unique_id, df in rainfall_data.items():
                kebele_region = df["R_NAME"].iloc[0] if "R_NAME" in df.columns else None
                kebele_region = REGION_MAP.get(kebele_region, kebele_region)
                if kebele_region != region:
                    continue
                df["date"] = pd.to_datetime(df["date"])
                df["precipitation"] = df["precipitation"].fillna(0)
                years = df["date"].dt.year.unique()
                seasonal_totals = []
                year_to_result_idx = {}
                for year in years:
                    start = pd.Timestamp(year=year, month=sow_month, day=sow_day)
                    end = pd.Timestamp(year=year, month=harv_month, day=harv_day)
                    mask = (df["date"] >= start) & (df["date"] <= end)
                    season_df = df.loc[mask].copy()
                    if season_df.empty:
                        continue
                    season_df = season_df.reset_index(drop=True)
                    # --- Data-driven thresholds ---
                    # Rainfall onset threshold: 75th percentile of 3-day rolling sum during sowing window (first 30 days)
                    rolling_3day_sums = season_df["precipitation"].rolling(3).sum().iloc[:30].dropna()
                    onset_threshold = np.percentile(rolling_3day_sums, 75) if not rolling_3day_sums.empty else 20
                    # Rainy day threshold: 50th percentile of non-zero rainfall during growing season
                    non_zero_rainfall = season_df["precipitation"][season_df["precipitation"] > 0]
                    rainy_day_threshold = np.percentile(non_zero_rainfall, 50) if not non_zero_rainfall.empty else 1
                    # Dry spell threshold: same as rainy day threshold (or 10th percentile)
                    dry_spell_threshold = rainy_day_threshold
                    # Feature 1: seasonal_rainfall_total
                    total = season_df["precipitation"].sum(skipna=True)
                    seasonal_totals.append(total)
                    # Feature 2: onset_date (use onset_threshold)
                    onset = None
                    for i in range(len(season_df) - 2):
                        window = season_df.iloc[i:i+3]
                        if window["precipitation"].sum(skipna=True) >= onset_threshold:
                            prev = season_df.iloc[max(0, i-10):i]
                            if (prev["precipitation"] < dry_spell_threshold).all():
                                onset = window.iloc[0]["date"]
                                break
                    # Feature 3: cessation_date
                    cessation = None
                    for i in range(len(season_df)-1, -1, -1):
                        if season_df.iloc[i]["precipitation"] > rainy_day_threshold:
                            next_days = season_df.iloc[i+1:i+8]
                            if (next_days["precipitation"] < dry_spell_threshold).all():
                                cessation = season_df.iloc[i]["date"]
                                break
                    # Feature 4: rainy_days_count (use rainy_day_threshold)
                    rainy_days = (season_df["precipitation"] > rainy_day_threshold).sum()
                    # Feature 5: dry_spell_days (use dry_spell_threshold)
                    dry = (season_df["precipitation"] < dry_spell_threshold).astype(int)
                    dry_spell_lengths = (dry.groupby((dry != dry.shift()).cumsum()).cumsum() * dry)
                    max_dry_spell = dry_spell_lengths.max() if not dry_spell_lengths.empty else 0
                    # Optional: data quality flag
                    missing_days = season_df["precipitation"].isna().sum()
                    data_quality_flag = "OK" if missing_days == 0 else f"missing_{missing_days}"
                    # Optional: onset delay in days
                    onset_delay_days = (onset - start).days if onset is not None else None
                    result = {
                        "crop": crop_name,
                        "region": region,
                        "kebele": unique_id,
                        "year": year,
                        "seasonal_rainfall_total": total,
                        "onset_date": onset,
                        "cessation_date": cessation,
                        "rainy_days_count": rainy_days,
                        "dry_spell_days": max_dry_spell,
                        "data_quality_flag": data_quality_flag,
                        "onset_delay_days": onset_delay_days,
                        "onset_threshold": onset_threshold,
                        "rainy_day_threshold": rainy_day_threshold,
                        "dry_spell_threshold": dry_spell_threshold
                    }
                    results.append(result)
                    year_to_result_idx[year] = len(results) - 1
                # Feature 6: rainfall_std_dev, rainfall_skewness (across years)
                if seasonal_totals:
                    std = np.std(seasonal_totals, ddof=1) if len(seasonal_totals) > 1 else 0
                    skewness = skew(seasonal_totals) if len(seasonal_totals) > 2 else 0
                    for year in years:
                        idx = year_to_result_idx.get(year)
                        if idx is not None:
                            results[idx]["rainfall_std_dev"] = std
                            results[idx]["rainfall_skewness"] = skewness
    df = pd.DataFrame(results)
    for col in ["onset_date", "cessation_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.dayofyear
    return df.to_dict(orient="records")

def compute_temperature_features(crop_calendar, temperature_data):
    """
    For each crop-region and kebele, compute temperature features for each season.
    Uses data-driven thresholds for GDD base and heatwave.
    """
    results = []
    for (crop_name, region), entry in crop_calendar.items():
        region = REGION_MAP.get(region, region)
        sessions = entry.get("sessions", [])
        for session in sessions:
            sow_month = int(session["early_sowing"]["month"])
            sow_day = int(session["early_sowing"]["day"])
            harv_month = int(session["late_harvest"]["month"])
            harv_day = int(session["late_harvest"]["day"])
            for unique_id, df in temperature_data.items():
                kebele_region = df["R_NAME"].iloc[0] if "R_NAME" in df.columns else None
                kebele_region = REGION_MAP.get(kebele_region, kebele_region)
                if kebele_region != region:
                    continue
                df["date"] = pd.to_datetime(df["date"])
                years = df["date"].dt.year.unique()
                for year in years:
                    start = pd.Timestamp(year=year, month=sow_month, day=sow_day)
                    end = pd.Timestamp(year=year, month=harv_month, day=harv_day)
                    mask = (df["date"] >= start) & (df["date"] <= end)
                    season_df = df.loc[mask].copy()
                    if season_df.empty:
                        continue
                    season_df = season_df.reset_index(drop=True)
                    # --- Dynamic thresholds ---
                    # GDD base temp: 10th percentile of mean temp in first 30 days
                    early_season = season_df.iloc[:30]
                    mean_temps_early = ((early_season["maximum_2m_air_temperature"] + early_season["minimum_2m_air_temperature"]) / 2)
                    gdd_base_temp = np.percentile(mean_temps_early, 10) if not mean_temps_early.empty else 10
                    # Heatwave threshold: 95th percentile of max temps in season
                    max_temps = season_df["maximum_2m_air_temperature"]
                    heatwave_threshold = np.percentile(max_temps, 95) if not max_temps.empty else 35
                    # --- Features ---
                    mean_temp = ((season_df["maximum_2m_air_temperature"] + season_df["minimum_2m_air_temperature"]) / 2).mean()
                    max_temp_avg = season_df["maximum_2m_air_temperature"].mean()
                    min_temp_avg = season_df["minimum_2m_air_temperature"].mean()
                    gdd = ((season_df["maximum_2m_air_temperature"] + season_df["minimum_2m_air_temperature"]) / 2 - gdd_base_temp).clip(lower=0).sum()
                    heatwave_days = (season_df["maximum_2m_air_temperature"] > heatwave_threshold).sum()
                    result = {
                        "crop": crop_name,
                        "region": region,
                        "kebele": unique_id,
                        "year": year,
                        "mean_temp_season": mean_temp,
                        "max_temp_avg": max_temp_avg,
                        "min_temp_avg": min_temp_avg,
                        "gdd_total": gdd,
                        "gdd_base_temp": gdd_base_temp,
                        "heatwave_days": heatwave_days,
                        "heatwave_threshold": heatwave_threshold
                    }
                    results.append(result)
    df = pd.DataFrame(results)
    # No date columns to convert here, but keep for future extensibility
    return df.to_dict(orient="records")

def compute_soil_moisture_features(crop_calendar, soil_data):
    """
    For each crop-region and kebele, compute soil moisture features for each season.
    Uses data-driven dry threshold.
    """
    results = []
    for (crop_name, region), entry in crop_calendar.items():
        region = REGION_MAP.get(region, region)
        sessions = entry.get("sessions", [])
        for session in sessions:
            sow_month = int(session["early_sowing"]["month"])
            sow_day = int(session["early_sowing"]["day"])
            harv_month = int(session["late_harvest"]["month"])
            harv_day = int(session["late_harvest"]["day"])
            for unique_id, df in soil_data.items():
                kebele_region = df["R_NAME"].iloc[0] if "R_NAME" in df.columns else None
                kebele_region = REGION_MAP.get(kebele_region, kebele_region)
                if kebele_region != region:
                    continue
                df["date"] = pd.to_datetime(df["date"])
                years = df["date"].dt.year.unique()
                year_means = []
                year_to_idx = {}
                for year in years:
                    start = pd.Timestamp(year=year, month=sow_month, day=sow_day)
                    end = pd.Timestamp(year=year, month=harv_month, day=harv_day)
                    mask = (df["date"] >= start) & (df["date"] <= end)
                    season_df = df.loc[mask].copy()
                    if season_df.empty:
                        continue
                    season_df = season_df.reset_index(drop=True)
                    # Use unified soil moisture column
                    soil_moisture_values = season_df["soil_moisture_value"].dropna()
                    dry_threshold = np.percentile(soil_moisture_values, 10) if not soil_moisture_values.empty else 1.5
                    mean_soil_moisture = soil_moisture_values.mean()
                    dry_soil_days = (soil_moisture_values < dry_threshold).sum()
                    year_means.append(mean_soil_moisture)
                    result = {
                        "crop": crop_name,
                        "region": region,
                        "kebele": unique_id,
                        "year": year,
                        "mean_soil_moisture": mean_soil_moisture,
                        "dry_soil_days": dry_soil_days,
                        "dry_threshold": dry_threshold
                    }
                    results.append(result)
                    year_to_idx[year] = len(results) - 1
                # Compute std across years
                if year_means:
                    std = np.std(year_means, ddof=1) if len(year_means) > 1 else 0
                    for year in years:
                        idx = year_to_idx.get(year)
                        if idx is not None:
                            results[idx]["soil_moisture_std"] = std
    df = pd.DataFrame(results)
    # No date columns to convert here, but keep for future extensibility
    return df.to_dict(orient="records")

def compute_ndvi_features(crop_calendar, ndvi_data):
    """
    For each crop-region and kebele, compute NDVI features for each season.
    Uses data-driven NDVI threshold and NDVI scale.
    """
    results = []
    for (crop_name, region), entry in crop_calendar.items():
        region = REGION_MAP.get(region, region)
        sessions = entry.get("sessions", [])
        for session in sessions:
            sow_month = int(session["early_sowing"]["month"])
            sow_day = int(session["early_sowing"]["day"])
            harv_month = int(session["late_harvest"]["month"])
            harv_day = int(session["late_harvest"]["day"])
            for unique_id, df in ndvi_data.items():
                kebele_region = df["R_NAME"].iloc[0] if "R_NAME" in df.columns else None
                kebele_region = REGION_MAP.get(kebele_region, kebele_region)
                if kebele_region != region:
                    continue
                df["date"] = pd.to_datetime(df["date"])
                # Normalize NDVI if needed
                if df["NDVI"].max() > 1.5:
                    df["NDVI"] = df["NDVI"] / 10000
                years = df["date"].dt.year.unique()
                all_seasonal_means = []
                year_to_idx = {}
                for year in years:
                    start = pd.Timestamp(year=year, month=sow_month, day=sow_day)
                    end = pd.Timestamp(year=year, month=harv_month, day=harv_day)
                    mask = (df["date"] >= start) & (df["date"] <= end)
                    season_df = df.loc[mask].copy()
                    if season_df.empty:
                        continue
                    season_df = season_df.reset_index(drop=True)
                    ndvi_vals = season_df["NDVI"].dropna()
                    ndvi_peak = ndvi_vals.max()
                    ndvi_scale = ndvi_peak  # NDVI scale: max NDVI in dataset for region/season
                    ndvi_seasonal_avg = ndvi_vals.mean()
                    all_seasonal_means.append(ndvi_seasonal_avg)
                    # --- Dynamic NDVI threshold: max(25% of peak, 20th percentile) ---
                    ndvi_threshold = max(0.25 * ndvi_peak, np.percentile(ndvi_vals, 20)) if not ndvi_vals.empty else 0.2
                    # Start of season: first date NDVI crosses threshold upwards
                    sos = None
                    for i in range(len(season_df)):
                        if season_df["NDVI"].iloc[i] >= ndvi_threshold:
                            sos = season_df["date"].iloc[i]
                            break
                    # End of season: first date after peak NDVI drops below threshold
                    eos = None
                    after_peak = season_df[season_df["NDVI"] == ndvi_peak].index.max()
                    if after_peak is not None:
                        for i in range(after_peak + 1, len(season_df)):
                            if season_df["NDVI"].iloc[i] < ndvi_threshold:
                                eos = season_df["date"].iloc[i]
                                break
                    ndvi_integral = ndvi_vals.sum() * 1  # 1 day interval
                    result = {
                        "crop": crop_name,
                        "region": region,
                        "kebele": unique_id,
                        "year": year,
                        "ndvi_peak": ndvi_peak,
                        "ndvi_scale": ndvi_scale,
                        "ndvi_seasonal_avg": ndvi_seasonal_avg,
                        "ndvi_start_of_season": sos,
                        "ndvi_end_of_season": eos,
                        "ndvi_integral": ndvi_integral,
                        "ndvi_threshold": ndvi_threshold
                    }
                    results.append(result)
                    year_to_idx[year] = len(results) - 1
                # NDVI anomaly avg (z-score) across years
                if all_seasonal_means:
                    mu = np.mean(all_seasonal_means)
                    sigma = np.std(all_seasonal_means, ddof=1) if len(all_seasonal_means) > 1 else 1
                    for year in years:
                        idx = year_to_idx.get(year)
                        if idx is not None:
                            z = (results[idx]["ndvi_seasonal_avg"] - mu) / sigma if sigma > 0 else 0
                            results[idx]["ndvi_anomaly_avg"] = z
    df = pd.DataFrame(results)
    for col in ["ndvi_start_of_season", "ndvi_end_of_season"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.dayofyear
    return df.to_dict(orient="records")



if __name__ == "__main__":
    # Load crop calendar
    crop_calendar = get_combined_crop_calendar()

    # --- Precipitation ---
    rainfall_data = load_precipitation_timeseries()
    rainfall_features = compute_rainfall_features(crop_calendar, rainfall_data)
    pd.DataFrame(rainfall_features).to_csv("rainfall_features_per_crop_kebele_season.csv", index=False)
    print("Rainfall features saved to rainfall_features_per_crop_kebele_season.csv")

    # --- Temperature ---
    temperature_data = load_temperature_timeseries()
    temperature_features = compute_temperature_features(crop_calendar, temperature_data)
    pd.DataFrame(temperature_features).to_csv("temperature_features_per_crop_kebele_season.csv", index=False)
    print("Temperature features saved to temperature_features_per_crop_kebele_season.csv")

    # --- Soil Moisture ---
    soil_data = load_soil_moisture_timeseries()
    soil_features = compute_soil_moisture_features(crop_calendar, soil_data)
    pd.DataFrame(soil_features).to_csv("soil_moisture_features_per_crop_kebele_season.csv", index=False)
    print("Soil moisture features saved to soil_moisture_features_per_crop_kebele_season.csv")

    # --- NDVI ---
    ndvi_data = load_ndvi_timeseries()
    ndvi_features = compute_ndvi_features(crop_calendar, ndvi_data)
    pd.DataFrame(ndvi_features).to_csv("ndvi_features_per_crop_kebele_season.csv", index=False)
    print("NDVI features saved to ndvi_features_per_crop_kebele_season.csv")