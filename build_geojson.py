import json
import geopandas as gpd

from weather_codes import get_weather_info

LAD_BOUNDARY_PATH = "data/LAD_major_city_boundary_data.gpkg"
LAD_NAME_FIELD = "LAD25NM"

def build_city_geojson(latest_forecasts):
    lad_layer = gpd.read_file(LAD_BOUNDARY_PATH)
    features=[]
    for _, row in lad_layer.iterrows():
        name = row[LAD_NAME_FIELD]
        geometry = row.geometry.__geo_interface__

        forecast = latest_forecasts.get(name)
        if forecast is None:
            print(f"Warning: no forecast data for {name}")
            continue

        weather_info = get_weather_info(forecast["weather_code"])

        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "name": name,
                "temperature_c": forecast["temperature_c"],
                "precipitation_mm": forecast["precipitation_mm"],
                "wind_speed_kmh": forecast["wind_speed_kmh"],
                "weather_description": weather_info["description"],
                "weather_icon": weather_info["icon"],
                "fetched_at": forecast["fetched_at"],
            },
        })

        return {"type": "FeatureCollection", "features": features}

if __name__ == "__main__":
    from fetch_weather import fetch_current_weather, clean_row

    lad_layer = gpd.read_file(LAD_BOUNDARY_PATH)
    latest = {}
    for _, row in lad_layer.iterrows():
        name = row[LAD_NAME_FIELD]
        centroid = row.geometry.centroid
        city = {"name": name, "lat": centroid.y, "lon": centroid.x}

        raw = fetch_current_weather(city)
        latest[name] = clean_row(city, raw)

    geojson = build_city_geojson(latest)

    with open("data/city_weather.geojson", "w") as f:
        json.dump(geojson, f, indent=2)

    print(f"Wrote {len(geojson['features'])} city features to data/city_weather.geojson")