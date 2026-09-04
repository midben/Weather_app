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
    valid_time       TIMESTAMP NOT NULL,  
    generated_at     TIMESTAMP NOT NULL DEFAULT NOW(),  
    temperature_c    FLOAT,
    precipitation_mm FLOAT,
    wind_speed_kmh   FLOAT,
    weather_code     INT
);

CREATE INDEX idx_outlook_location_time ON hourly_outlook (location_name, valid_time);