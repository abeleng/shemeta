import os
import pandas as pd
import numpy as np
from datetime import datetime
from scipy.stats import zscore
from climate_indices import compute, indices, utils
from climate_indices import climdex_input

# ---------- Paths ---------- #
base_output = "scraped_data"
precip_path = os.path.join(base_output, "precipitation", "precipitation-temporary")
temp_path = os.path.join(base_output, "temperature")
output_path = os.path.join(base_output, "drought_indices")
os.makedirs(output_path, exist_ok=True)

# ---------- Helper: Group to Monthly ---------- #
def daily_to_monthly(df, value_col):
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    return df.groupby(['year', 'month'])[value_col].sum().reset_index()

def daily_temp_to_monthly(df, min_col, max_col):
    df['date'] = pd.to_datetime(df['date'])
    df['tavg'] = (df[min_col] + df[max_col]) / 2
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    return df.groupby(['year', 'month'])['tavg'].mean().reset_index()

# ---------- SPI Calculation ---------- #
def compute_spi(monthly_precip, scale=3):
    values = monthly_precip['precip'].values
    # Fill missing or invalid values with NaN
    values = np.where((values < 0) | (np.isnan(values)), np.nan, values)
    spi_vals = indices.spi(values, scale=scale, data_start_year=int(monthly_precip['year'].iloc[0]))
    return spi_vals

# ---------- PDSI Calculation (simplified) ---------- #
def compute_pdsi(monthly_precip, monthly_temp, lat=10.0):
    # PDSI computation is complex; here we use Thornthwaite PET as a proxy input
    # Merge precip + temp
    df = pd.merge(monthly_precip, monthly_temp, on=['year', 'month'], how='inner')
    df = df.sort_values(['year', 'month'])

    # Compute PET using Thornthwaite method
    pet_vals = utils.pet.thornthwaite(df['tavg'].values, lat)
    df['pet'] = pet_vals
    df['deficit'] = df['pet'] - df['precip']

    # Placeholder for full PDSI; here we return the deficit as proxy
    return df[['year', 'month', 'precip', 'tavg', 'pet', 'deficit']]

# ---------- Main ---------- #
def process_kebeles():
    kebele_df = pd.read_csv(os.path.join(base_output, "kebeles_used.csv"))
    kebele_ids = kebele_df['unique_id'].unique()

    for unique_id in kebele_ids:
        print(f"📍 Processing {unique_id}...")

        # -------------------- Load Precip -------------------- #
        precip_files = [f for f in os.listdir(precip_path) if f.startswith(unique_id)]
        precip_df = pd.concat([pd.read_csv(os.path.join(precip_path, f)) for f in precip_files])
        precip_df = precip_df.rename(columns={unique_id: "precip"})
        monthly_precip = daily_to_monthly(precip_df, "precip")

        # -------------------- Load Temperature -------------------- #
        temp_files = [f for f in os.listdir(temp_path) if f.startswith(unique_id)]
        temp_df = pd.concat([pd.read_csv(os.path.join(temp_path, f)) for f in temp_files])
        monthly_temp = daily_temp_to_monthly(temp_df, "minimum_2m_air_temperature", "maximum_2m_air_temperature")

        # -------------------- SPI -------------------- #
        try:
            spi_vals = compute_spi(monthly_precip, scale=3)
            spi_df = monthly_precip.copy()
            spi_df['spi_3'] = spi_vals
            spi_df.to_csv(os.path.join(output_path, f"{unique_id}_spi.csv"), index=False)
            print(f"✅ SPI saved for {unique_id}")
        except Exception as e:
            print(f"❌ SPI failed for {unique_id}: {e}")

        # -------------------- PDSI -------------------- #
        try:
            pdsi_df = compute_pdsi(monthly_precip, monthly_temp, lat=9.0)  # Approx latitude for Ethiopia
            pdsi_df.to_csv(os.path.join(output_path, f"{unique_id}_pdsi.csv"), index=False)
            print(f"✅ PDSI saved for {unique_id}")
        except Exception as e:
            print(f"❌ PDSI failed for {unique_id}: {e}")

if __name__ == "__main__":
    process_kebeles()
