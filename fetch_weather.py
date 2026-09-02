import requests
from datetime import datetime, timezone

API_URL = "https://api.open-meteo.com/v1/forecast"

def fetch_current_weather(city):
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "current": "temperature_2m,precipitation_sum,windspeed_10m,weathercode",
        "timezone": "Europe/London",
    }
    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def clean_row(city, raw):
    current = raw["current"]

    return {
        "location_name": city["name"],
        "forecast_time": current["time"],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "temperature_c": current["temperature_2m"],
        "precipitation_mm": current["precipitation_sum"],
        "wind_speed_kmh": current["windspeed_10m"],
        "weather_code": current["weathercode"]
    }

if __name__ == "__main__":
    city = {"name": "London", "lat": 51.5074, "lon": -0.1278}
    raw = fetch_current_weather(city)
    cleaned = clean_row(city, raw)
    print(cleaned)