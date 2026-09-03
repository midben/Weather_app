import json
import geopandas as gpd

from weather_codes import get_weather_info

LAD_BOUNDARY_PATH = "data/LAD_major_city_boundary_data.gpkg"
LAD_NAME_FIELD = "LAD25NM"


def load_lad_layer_wgs84():
    layer = gpd.read_file(LAD_BOUNDARY_PATH)
    if layer.crs is not None and layer.crs.to_epsg() != 4326:
        layer = layer.to_crs(epsg=4326)
    return layer


def build_city_geojson(latest_forecasts):
    lad_layer = load_lad_layer_wgs84()
    features = []
    for _, row in lad_layer.iterrows():
        name = row[LAD_NAME_FIELD]
        geometry = row.geometry.__geo_interface__
        centroid = row.geometry.centroid

        forecast = latest_forecasts.get(name)
        if forecast is None:
            print(f"WARNING: no forecast data available yet for '{name}'")
            continue

        weather_info = get_weather_info(forecast["weather_code"])

        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "name": name,
                "centroid_lat": centroid.y,
                "centroid_lon": centroid.x,
                "temperature_c": forecast["temperature_c"],
                "precipitation_mm": forecast["precipitation_mm"],
                "wind_speed_kmh": forecast["wind_speed_kmh"],
                "weather_description": weather_info["description"],
                "weather_icon": weather_info["icon"],
                "fetched_at": forecast["fetched_at"],
            },
        })

    return {"type": "FeatureCollection", "features": features}


def fetch_latest_forecasts_from_db():
    from db import get_connection
 
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT location_name, forecast_time, fetched_at,
                       temperature_c, precipitation_mm, wind_speed_kmh, weather_code
                FROM latest_forecasts
            """)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
    finally:
        conn.close()
 
    return {
        row[0]: dict(zip(columns, row))
        for row in rows
    }
 
 
if __name__ == "__main__":
    latest = fetch_latest_forecasts_from_db()
 
    if not latest:
        print("No forecast data in the database yet — run insert_forecasts.py first.")
    else:
        geojson = build_city_geojson(latest)
 
        with open("data/city_weather.geojson", "w") as f:
            json.dump(geojson, f, indent=2, default=str)  # default=str handles datetime objects
 
        print(f"Wrote {len(geojson['features'])} city features to data/city_weather.geojson")
