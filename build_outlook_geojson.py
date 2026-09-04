import json

from build_geojson import load_lad_layer_wgs84, LAD_NAME_FIELD
from weather_codes import get_weather_info
from db import get_connection


def fetch_hourly_outlook_from_db():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT location_name, valid_time,
                       temperature_c, precipitation_mm, wind_speed_kmh, weather_code
                FROM hourly_outlook
                ORDER BY location_name, valid_time
            """)
            rows = cur.fetchall()
    finally:
        conn.close()

    outlook = {}
    for location_name, valid_time, temp, precip, wind, code in rows:
        weather_info = get_weather_info(code)
        outlook.setdefault(location_name, []).append({
            "valid_time": valid_time.isoformat(),
            "temperature_c": temp,
            "precipitation_mm": precip,
            "wind_speed_kmh": wind,
            "weather_description": weather_info["description"],
            "weather_icon": weather_info["icon"],
        })
    return outlook


def build_outlook_geojson(outlook_by_city):
    lad_layer = load_lad_layer_wgs84()

    features = []
    for _, row in lad_layer.iterrows():
        name = row[LAD_NAME_FIELD]
        geometry = row.geometry.__geo_interface__
        centroid = row.geometry.centroid

        hourly = outlook_by_city.get(name)
        if not hourly:
            print(f"WARNING: no outlook data available yet for '{name}'")
            continue

        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "name": name,
                "centroid_lat": centroid.y,
                "centroid_lon": centroid.x,
                "hourly": hourly,
            },
        })

    return {"type": "FeatureCollection", "features": features}


if __name__ == "__main__":
    outlook = fetch_hourly_outlook_from_db()

    if not outlook:
        print("No outlook data in the database yet — run insert_forecasts.py first.")
    else:
        geojson = build_outlook_geojson(outlook)

        with open("data/city_outlook.geojson", "w") as f:
            json.dump(geojson, f, indent=2, default=str)

        print(f"Wrote {len(geojson['features'])} city features to data/city_outlook.geojson")
