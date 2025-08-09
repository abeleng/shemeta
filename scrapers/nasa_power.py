import requests
import numpy as np
import time
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
import json

# Load Ethiopia boundary shapefile
ethiopia_shape = gpd.read_file(r"C:\Users\HP\Downloads\ethiopia-zone\Eth_Zone_2013.shp")  # <-- update path if needed
# Reproject to WGS84 if necessary
if ethiopia_shape.crs != "EPSG:4326":
    ethiopia_shape = ethiopia_shape.to_crs("EPSG:4326")
# Ethiopia bounding box and grid resolution
lat_min, lat_max = 3.4, 15.0
lon_min, lon_max = 33.0, 48.0
grid_step = 0.5  # smaller step means more points

# Date range
start_date = "20230101"
end_date = "20231231"

# Parameters to fetch
parameters = [
    "PRECTOT",   # Precipitation (mm)
    "T2M_MAX",   # Max temperature (C)
    "T2M_MIN",   # Min temperature (C)
    "WS2M",      # Wind speed (m/s)
    "ALLSKY_SFC_SW_DWN"  # Solar radiation (MJ/m2)
]

lat_points = np.arange(lat_min, lat_max + grid_step, grid_step)
lon_points = np.arange(lon_min, lon_max + grid_step, grid_step)

def is_inside_ethiopia(lat, lon):
    point = Point(lon, lat)
    return ethiopia_shape.contains(point).any()

json_path = "ethiopia_weather_data_2023.json"
if not os.path.exists(json_path):
    with open(json_path, "w") as f:
        json.dump([], f)  # initialize with empty list

total_points = len(lat_points) * len(lon_points)
print(f"Total grid points in bounding box: {total_points}")

count_inside = 0

for lat in lat_points:
    for lon in lon_points:
        if not is_inside_ethiopia(lat, lon):
            continue

        count_inside += 1
        print(f"Requesting data for lat={lat:.2f}, lon={lon:.2f} (inside Ethiopia)")

        param_str = ",".join(parameters)
        url = (
            f"https://power.larc.nasa.gov/api/temporal/daily/point?"
            f"parameters={param_str}&community=AG&longitude={lon}&latitude={lat}"
            f"&start={start_date}&end={end_date}&format=JSON"
        )
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            daily_data = data.get("properties", {}).get("parameter", {})
            dates = list(daily_data.get(parameters[0], {}).keys())

            rows = []
            for date in dates:
                row = {
                    "date": date,
                    "latitude": lat,
                    "longitude": lon,
                }
                for p in parameters:
                    row[p] = daily_data.get(p, {}).get(date, None)
                rows.append(row)

            # Append rows to JSON file
            with open(json_path, "r+") as f:
                existing = json.load(f)
                existing.extend(rows)
                f.seek(0)
                json.dump(existing, f, indent=2)
                f.truncate()
            print(f"Data for {lat},{lon} written to JSON.")

            time.sleep(2)
        except Exception as e:
            print(f"Failed to get data for {lat},{lon}: {e}")

print(f"Total points inside Ethiopia: {count_inside}")
print("JSON data collection complete!")