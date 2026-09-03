import requests
from datetime import datetime, timezone

API_URL = "https://api.open-meteo.com/v1/forecast"

def fetch_current_weather(city):
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "current": "temperature_2m,precipitation,windspeed_10m,weather_code",
        "timezone": "Europe/London",
    }
    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    print(response.json())
    return response.json()

def clean_row(city, raw):
    current = raw["current"]

    return {
        "location_name": city["name"],
        "forecast_time": current["time"],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "temperature_c": current["temperature_2m"],
        "precipitation_mm": current["precipitation"],
        "wind_speed_kmh": current["windspeed_10m"],
        "weather_code": current["weather_code"]
    }

def fetch_hourly_forecast(city, hours=24):
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "hourly": "temperature_2m,precipitation,windspeed_10m,weather_code",
        "forecast_hours": hours,
        "timezone": "Europe/London",
    }
    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def clean_hourly_rows(city, raw_response):
    hourly = raw_response["hourly"]
    generated_at = datetime.now(timezone.utc).isoformat()

    rows = []
    for i, valid_time in enumerate(hourly["time"]):
        rows.append({
            "location_name": city["name"],
            "valid_time": valid_time,
            "generated_at": generated_at,
            "temperature_c": hourly["temperature_2m"][i],
            "precipitation_mm": hourly["precipitation"][i],
            "wind_speed_kmh": hourly["windspeed_10m"][i],
            "weather_code": hourly["weather_code"][i]
        })
    return rows

if __name__ == "__main__":
    city = {"name": "London", "lat": 51.5074, "lon": -0.1278}
    raw = fetch_current_weather(city)
    cleaned = clean_row(city, raw)
    print(cleaned)