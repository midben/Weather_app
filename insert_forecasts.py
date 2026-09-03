from fetch_weather import fetch_current_weather, clean_row
from build_geojson import load_lad_layer_wgs84, LAD_NAME_FIELD
from db import get_connection

def insert_row(conn, row):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO forecasts (
                location_name, forecast_time, fetched_at,
                temperature_c, precipitation_mm, wind_speed_kmh, weather_code
            )
            VALUES (
                %(location_name)s, %(forecast_time)s, %(fetched_at)s,
                %(temperature_c)s, %(precipitation_mm)s,
                %(wind_speed_kmh)s, %(weather_code)s
            )
        """, row)
    conn.commit()

def run():
    lad_layer = load_lad_layer_wgs84()
    conn = get_connection()

    try:
        for _, boundary_row in lad_layer.iterrows():
            name = boundary_row[LAD_NAME_FIELD]
            centroid = boundary_row['geometry'].centroid
            city = {"name": name, "lat": centroid.y, "lon": centroid.x}

            try:
                raw_data = fetch_current_weather(city)
                cleaned_data = clean_row(city, raw_data)
                insert_row(conn, cleaned_data)
                print(f"Inserted forecast for {name}")
            except Exception as e:
                print(f"Error processing {name}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run()