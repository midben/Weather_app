CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE forecasts (
    id SERIAL PRIMARY KEY,
    location_name TEXT NOT NULL,
    forecast_time TIMESTAMP NOT NULL,
    fetched_at TIMESTAMP NOT NULL DEFAULT NOW(),
    temperature_c FLOAT,
    precipitation_mm FLOAT,
    wind_speed_kmh FLOAT,
    weather_code INT
);

CREATE INDEX idx_forecasts_geom ON forecasts USING GIST (geom);

CREATE INDEX idx_forecasts_location_time ON forecasts (location_name, fetched_at DESC);
 
CREATE VIEW latest_forecasts AS
SELECT DISTINCT ON (location_name)
    location_name, forecast_time, fetched_at,
    temperature_c, precipitation_mm, wind_speed_kmh, weather_code
FROM forecasts
ORDER BY location_name, fetched_at DESC;

CREATE TABLE hourly_outlook (
    id               SERIAL PRIMARY KEY,
    location_name    TEXT NOT NULL,
    valid_time       TIMESTAMP NOT NULL,   -- the future hour this prediction is FOR
    generated_at     TIMESTAMP NOT NULL DEFAULT NOW(),  -- when this prediction was fetched
    temperature_c    FLOAT,
    precipitation_mm FLOAT,
    wind_speed_kmh   FLOAT,
    weather_code     INT
);