import ee
import pandas as pd
import os
from datetime import datetime

# Initialize Earth Engine
ee.Initialize(project="")

# Global Parameters
start_year = 2010
end_year = datetime.now().year
scale = 5000  # For precip/temp/soil
ndvi_scale = 250  # MODIS NDVI resolution

# Paths
base_output = "scraped_data"
precip_folder = os.path.join(base_output, "precipitation")
temp_folder = os.path.join(base_output, "temperature")
soil_folder = os.path.join(base_output, "soil_moisture")
ndvi_folder = os.path.join(base_output, "ndvi")

# Ensure directories exist
os.makedirs(os.path.join(precip_folder, "precipitation-temporary"), exist_ok=True)
os.makedirs(temp_folder, exist_ok=True)
os.makedirs(os.path.join(soil_folder, "soil_moisture-temporary"), exist_ok=True)
os.makedirs(soil_folder, exist_ok=True)
os.makedirs(os.path.join(ndvi_folder, "ndvi-temporary"), exist_ok=True)
os.makedirs(ndvi_folder, exist_ok=True)

# Load kebele boundaries
admin_boundaries = ee.FeatureCollection('projects/medacolleges/assets/Ethiopia_AdminBoundaries-shp')


# ----------------------- UTILS ------------------------

def get_feature_metadata(feature):
    metadata = feature.toDictionary().getInfo()
    metadata.pop('geometry', None)
    return metadata

def get_unique_id(feature):
    # Only use GlobalID as unique_id
    return feature.get('GlobalID').getInfo()

def load_used_kebeles(csv_path=os.path.join(base_output, "kebeles_used.csv")):
    return pd.read_csv(csv_path) if os.path.exists(csv_path) else None


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

def normalize_region_column(df):
    region_col = None
    for col in ["R_NAME", "REGION"]:
        if col in df.columns:
            region_col = col
            break
    if region_col:
        df[region_col] = df[region_col].map(REGION_MAP).fillna(df[region_col])
    return df


# ----------------------- SCRAPER HELPERS ------------------------

def reduce_image(image, geometry, scale, band_name, convert_kelvin=False):
    img = ee.Image(image)
    if convert_kelvin:
        img = img.subtract(273.15)
    date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd')
    mean = img.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=scale,
        bestEffort=True
    ).get(band_name)
    return ee.Feature(None, {'date': date, band_name: mean})


# ----------------------- PRECIPITATION SCRAPER ------------------------

def scrape_precipitation_data(max_kebeles=10):
    print("▶ Starting CHIRPS precipitation scrape...")
    collection_name = 'UCSB-CHG/CHIRPS/DAILY'
    band_name = 'precipitation'
    kebele_metadata_records = []

    features = admin_boundaries.toList(admin_boundaries.size())
    num_features = admin_boundaries.size().getInfo()

    for i in range(min(max_kebeles, num_features)):
        feature = ee.Feature(features.get(i))
        unique_id = get_unique_id(feature)
        geometry = feature.geometry()
        metadata = get_feature_metadata(feature)
        metadata["unique_id"] = unique_id
        kebele_metadata_records.append(metadata)

        df = pd.DataFrame()

        for year in range(start_year, end_year + 1):
            print(f"Fetching rainfall for {unique_id} in {year}")
            image_collection = ee.ImageCollection(collection_name).filterDate(f"{year}-01-01", f"{year}-12-31").select(band_name)
            time_series = image_collection.map(lambda img: reduce_image(img, geometry, scale, band_name))
            features_list = time_series.getInfo()['features']
            temp_df = pd.json_normalize([f['properties'] for f in features_list])
            for k, v in metadata.items():
                temp_df[k] = v
            temp_df = normalize_region_column(temp_df)
            temp_df["date"] = pd.to_datetime(temp_df["date"]).dt.strftime("%Y-%m-%d")
            temp_df.to_csv(os.path.join(precip_folder, "precipitation-temporary", f"{unique_id}_{year}.csv"), index=False)
            df = pd.concat([df, temp_df], ignore_index=True)

        if not df.empty:
            df['date'] = pd.to_datetime(df['date']).dt.strftime("%Y-%m-%d")
            df = normalize_region_column(df)
            df.to_csv(os.path.join(precip_folder, f"{unique_id}_precipitation_timeseries.csv"), index=False)

    pd.DataFrame(kebele_metadata_records).to_csv(os.path.join(base_output, "kebeles_used.csv"), index=False)
    print("✅ Precipitation data for each kebele saved separately.\n")


# ----------------------- TEMPERATURE SCRAPER ------------------------

def scrape_temperature_data(max_kebeles=10):
    print("▶ Starting ERA5 temperature scrape...")
    kebeles_df = load_used_kebeles()
    if kebeles_df is None:
        print("❌ kebeles_used.csv not found. Run rainfall scraper first.")
        return

    for _, row in kebeles_df.iterrows():
        unique_id = row['GlobalID']
        feature = admin_boundaries.filter(ee.Filter.eq('GlobalID', row['GlobalID'])).first()
        if feature is None:
            print(f"Skipping {unique_id} - not found.")
            continue
        geometry = ee.Feature(feature).geometry()
        metadata = row.to_dict()

        df = pd.DataFrame()
        for year in range(start_year, end_year + 1):
            print(f"Fetching temperature for {unique_id} in {year}")
            max_col = ee.ImageCollection('ECMWF/ERA5/DAILY').filterDate(f'{year}-01-01', f'{year}-12-31').select('maximum_2m_air_temperature')
            min_col = ee.ImageCollection('ECMWF/ERA5/DAILY').filterDate(f'{year}-01-01', f'{year}-12-31').select('minimum_2m_air_temperature')
            max_series = max_col.map(lambda img: reduce_image(img, geometry, scale, 'maximum_2m_air_temperature', True))
            min_series = min_col.map(lambda img: reduce_image(img, geometry, scale, 'minimum_2m_air_temperature', True))

            max_df = pd.json_normalize([f['properties'] for f in max_series.getInfo()['features']])
            min_df = pd.json_normalize([f['properties'] for f in min_series.getInfo()['features']])

            if 'date' not in max_df.columns or max_df.empty:
                print(f"⚠️  No max temperature data for {unique_id} in {year}")
                continue
            if 'date' not in min_df.columns or min_df.empty:
                print(f"⚠️  No min temperature data for {unique_id} in {year}")
                continue

            temp_df = pd.merge(max_df, min_df, on='date', how='outer')
            for k, v in metadata.items():
                temp_df[k] = v
            temp_df = normalize_region_column(temp_df)
            temp_df["date"] = pd.to_datetime(temp_df["date"]).dt.strftime("%Y-%m-%d")
            # Optionally save per-year CSVs here if you want
            # temp_df.to_csv(os.path.join(temp_folder, f"{unique_id}_{year}_temp.csv"), index=False)
            df = pd.concat([df, temp_df], ignore_index=True)

        if not df.empty:
            df['date'] = pd.to_datetime(df['date']).dt.strftime("%Y-%m-%d")
            df = normalize_region_column(df)
            df.to_csv(os.path.join(temp_folder, f"{unique_id}_temperature_timeseries.csv"), index=False)

    print("✅ Temperature data for each kebele saved separately.\n")


# ----------------------- SOIL MOISTURE SCRAPER ------------------------

def scrape_soil_moisture_data(max_kebeles=10):
    print("▶ Starting SMAP soil moisture scrape...")
    kebeles_df = load_used_kebeles()
    use_shapefile = kebeles_df is None

    features = admin_boundaries.toList(admin_boundaries.size()) if use_shapefile else None
    num_features = admin_boundaries.size().getInfo() if use_shapefile else len(kebeles_df)

    switch_date = datetime(2022, 8, 2)

    for i in range(min(max_kebeles, num_features)):
        if use_shapefile:
            feature = ee.Feature(features.get(i))
            kebele_name = feature.get('KK_NAME').getInfo()
            global_id = feature.get('GlobalID').getInfo()
            geometry = feature.geometry()
            metadata = get_feature_metadata(feature)
        else:
            row = kebeles_df.iloc[i]
            kebele_name, global_id = row['KK_NAME'], row['GlobalID']
            feature = admin_boundaries.filter(ee.Filter.eq('GlobalID', global_id)).first()
            geometry = feature.geometry()
            metadata = row.to_dict()

        unique_id = global_id
        df = pd.DataFrame()

        for year in range(start_year, end_year + 1):
            print(f"Fetching soil moisture for {unique_id} in {year}")

            # Determine date ranges for each dataset
            year_start = datetime(year, 1, 1)
            year_end = datetime(year, 12, 31)
            dfs = []

            # Use first dataset up to switch_date
            if year_start <= switch_date:
                end = min(year_end, switch_date)
                collection1 = ee.ImageCollection('NASA_USDA/HSL/SMAP10KM_soil_moisture') \
                    .filterDate(year_start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')) \
                    .select('ssm')
                series1 = collection1.map(lambda img: reduce_image(img, geometry, scale, 'ssm'))
                features_list1 = series1.getInfo()['features']
                temp_df1 = pd.json_normalize([f['properties'] for f in features_list1])
                for k, v in metadata.items():
                    temp_df1[k] = v
                temp_df1.rename(columns={"ssm": "soil_moisture_value"}, inplace=True)
                temp_df1 = normalize_region_column(temp_df1)
                if "date" in temp_df1.columns and not temp_df1.empty:
                    temp_df1["date"] = pd.to_datetime(temp_df1["date"]).dt.strftime("%Y-%m-%d")
                dfs.append(temp_df1)

            # Use second dataset after switch_date
            if year_end > switch_date:
                start = max(year_start, switch_date + pd.Timedelta(days=1))
                collection2 = ee.ImageCollection('NASA_USDA/HSL/SMAP10KM_soil_moisture') \
                    .filterDate(start.strftime('%Y-%m-%d'), year_end.strftime('%Y-%m-%d')) \
                    .select('sm_rootzone')
                series2 = collection2.map(lambda img: reduce_image(img, geometry, scale, 'sm_rootzone'))
                features_list2 = series2.getInfo()['features']
                temp_df2 = pd.json_normalize([f['properties'] for f in features_list2])
                for k, v in metadata.items():
                    temp_df2[k] = v
                temp_df2.rename(columns={"sm_rootzone": "soil_moisture_value"}, inplace=True)
                temp_df2 = normalize_region_column(temp_df2)
                if "date" in temp_df2.columns and not temp_df2.empty:
                    temp_df2["date"] = pd.to_datetime(temp_df2["date"]).dt.strftime("%Y-%m-%d")
                dfs.append(temp_df2)

            if dfs:
                temp_df = pd.concat(dfs, ignore_index=True)
                temp_df.to_csv(os.path.join(soil_folder, "soil_moisture-temporary", f"{unique_id}_{year}.csv"), index=False)
                df = pd.concat([df, temp_df], ignore_index=True)

        if not df.empty:
            df['date'] = pd.to_datetime(df['date']).dt.strftime("%Y-%m-%d")
            df = normalize_region_column(df)
            df.to_csv(os.path.join(soil_folder, f"{unique_id}_soil_moisture_timeseries.csv"), index=False)

    print("✅ Soil moisture data for each kebele saved separately.\n")


# ----------------------- NDVI SCRAPER ------------------------

def scrape_ndvi_data(max_kebeles=10):
    print("▶ Starting MODIS NDVI scrape...")
    kebeles_df = load_used_kebeles()
    use_shapefile = kebeles_df is None

    features = admin_boundaries.toList(admin_boundaries.size()) if use_shapefile else None
    num_features = admin_boundaries.size().getInfo() if use_shapefile else len(kebeles_df)

    switch_date = datetime(2023, 7, 31)

    for i in range(min(max_kebeles, num_features)):
        if use_shapefile:
            feature = ee.Feature(features.get(i))
            kebele_name = feature.get('KK_NAME').getInfo()
            global_id = feature.get('GlobalID').getInfo()
            geometry = feature.geometry()
            metadata = get_feature_metadata(feature)
        else:
            row = kebeles_df.iloc[i]
            kebele_name, global_id = row['KK_NAME'], row['GlobalID']
            feature = admin_boundaries.filter(ee.Filter.eq('GlobalID', global_id)).first()
            geometry = feature.geometry()
            metadata = row.to_dict()

        unique_id = global_id
        df = pd.DataFrame()

        for year in range(start_year, end_year + 1):
            print(f"Fetching NDVI for {unique_id} in {year}")

            year_start = datetime(year, 1, 1)
            year_end = datetime(year, 12, 31)
            dfs = []

            # Use MODIS/006/MOD13Q1 up to switch_date
            if year_start <= switch_date:
                end = min(year_end, switch_date)
                collection1 = ee.ImageCollection('MODIS/006/MOD13Q1') \
                    .filterDate(year_start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')) \
                    .select('NDVI')
                series1 = collection1.map(lambda img: reduce_image(img, geometry, ndvi_scale, 'NDVI'))
                features_list1 = series1.getInfo()['features']
                temp_df1 = pd.json_normalize([f['properties'] for f in features_list1])
                for k, v in metadata.items():
                    temp_df1[k] = v
                if not temp_df1.empty and temp_df1["NDVI"].max(skipna=True) > 1.5:
                    temp_df1["NDVI"] = temp_df1["NDVI"] / 10000
                temp_df1 = normalize_region_column(temp_df1)
                temp_df1["date"] = pd.to_datetime(temp_df1["date"]).dt.strftime("%Y-%m-%d")
                dfs.append(temp_df1)

            # Use MODIS/061/MOD13Q1 after switch_date
            if year_end > switch_date:
                start = max(year_start, switch_date + pd.Timedelta(days=1))
                collection2 = ee.ImageCollection('MODIS/061/MOD13Q1') \
                    .filterDate(start.strftime('%Y-%m-%d'), year_end.strftime('%Y-%m-%d')) \
                    .select('NDVI')
                series2 = collection2.map(lambda img: reduce_image(img, geometry, ndvi_scale, 'NDVI'))
                features_list2 = series2.getInfo()['features']
                temp_df2 = pd.json_normalize([f['properties'] for f in features_list2])
                for k, v in metadata.items():
                    temp_df2[k] = v
                if not temp_df2.empty and temp_df2["NDVI"].max(skipna=True) > 1.5:
                    temp_df2["NDVI"] = temp_df2["NDVI"] / 10000
                temp_df2 = normalize_region_column(temp_df2)
                temp_df2["date"] = pd.to_datetime(temp_df2["date"]).dt.strftime("%Y-%m-%d")
                dfs.append(temp_df2)

            if dfs:
                temp_df = pd.concat(dfs, ignore_index=True)
                temp_df.to_csv(os.path.join(ndvi_folder, "ndvi-temporary", f"{unique_id}_{year}.csv"), index=False)
                df = pd.concat([df, temp_df], ignore_index=True)

        if not df.empty:
            df['date'] = pd.to_datetime(df['date']).dt.strftime("%Y-%m-%d")
            df = normalize_region_column(df)
            df.to_csv(os.path.join(ndvi_folder, f"{unique_id}_ndvi_timeseries.csv"), index=False)

    print("✅ NDVI data for each kebele saved separately.\n")


# ----------------------- MAIN ------------------------

def print_unique_rk_names(save_to_file=True, filename="unique_r_names.txt"):
    # Get all unique RK_NAME values
    unique_rk_names = admin_boundaries.distinct(['RK_NAME']).aggregate_array('R_NAME').getInfo()
    print("Unique RK_NAME values:")
    for rk_name in unique_rk_names:
        print(rk_name)
    if save_to_file:
        with open(filename, "w", encoding="utf-8") as f:
            for rk_name in unique_rk_names:
                f.write(f"{rk_name}\n")
        print(f"✅ Saved unique RK_NAME values to {filename}")

if __name__ == "__main__":
    scrape_precipitation_data(max_kebeles=3)
    scrape_temperature_data(max_kebeles=3)
    scrape_soil_moisture_data(max_kebeles=3)
    scrape_ndvi_data(max_kebeles=3)
