import requests

def get_weather_index_data(latitude, longitude, start_date, end_date):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "start_date": start_date,  # e.g. "2025-08-01"
        "end_date": end_date,      # e.g. "2025-08-10"
        "timezone": "UTC"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching weather data:", response.status_code)
        return None

# Example usage
# data = get_weather_index_data(12.9716, 77.5946, "2025-08-01", "2025-08-10")
# print(data)
