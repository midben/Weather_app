"""
Builds the GeoJSON the dashboard reads. Iterates the pre-filtered city
boundary GeoPackage directly (data/LAD_major_city_boundary_data.gpkg) —
since this file already only contains the cities we want, no name-matching
against a full national LAD dataset is needed anymore.
"""

import json
import geopandas as gpd

from weather_codes import get_weather_info

LAD_BOUNDARY_PATH = "data/LAD_major_city_boundary_data.gpkg"
LAD_NAME_FIELD = "LAD25NM"


def load_lad_layer_wgs84():
    """
    Loads the boundary GeoPackage and reprojects to EPSG:4326 (WGS84
    lat/lon degrees) if it isn't already. The source file is typically in
    EPSG:27700 (British National Grid) — fine for area/distance math, but
    both Open-Meteo and Leaflet/GeoJSON require plain lat/lon degrees, not
    projected coordinates.
    """
    layer = gpd.read_file(LAD_BOUNDARY_PATH)
    if layer.crs is not None and layer.crs.to_epsg() != 4326:
        layer = layer.to_crs(epsg=4326)
    return layer


def build_city_geojson(latest_forecasts):
    """
    latest_forecasts: dict of {city_name: forecast_row}, where forecast_row
    is the cleaned dict shape from fetch_weather.py's clean_row().

    Returns a GeoJSON FeatureCollection: one polygon feature per city.
    Each feature carries its centroid lat/lon as properties too — not for
    the API call (that already happened before this function runs), but
    so the dashboard can place a weather icon at a sensible point without
    needing its own polygon-centroid library just to re-derive it.
    """
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


if __name__ == "__main__":
    from fetch_weather import fetch_current_weather, clean_row

    lad_layer = load_lad_layer_wgs84()

    latest = {}
    for _, row in lad_layer.iterrows():
        name = row[LAD_NAME_FIELD]
        # Use each polygon's centroid as the point to query Open-Meteo for —
        # a forecast API needs a single lat/lon, not a whole shape.
        centroid = row.geometry.centroid
        city = {"name": name, "lat": centroid.y, "lon": centroid.x}

        raw = fetch_current_weather(city)
        latest[name] = clean_row(city, raw)

    geojson = build_city_geojson(latest)

    with open("data/city_weather.geojson", "w") as f:
        json.dump(geojson, f, indent=2)

    print(f"Wrote {len(geojson['features'])} city features to data/city_weather.geojson")
