# Weather_app
Webpage displaying weather conditions in major cities across the UK

## Architecture
 
```
Scheduler (Task Scheduler / cron)
    → insert_forecasts.py   — fetches from Open-Meteo, writes to Postgres
    → PostgreSQL database    — forecasts (history) + hourly_outlook (forecast)
    → build_outlook_geojson.py — reads from Postgres, writes GeoJSON
    → dashboard.html          — Leaflet map, reads the GeoJSON
```
 
Two tables serve different purposes:
- **`forecasts`** — append-only historical record. Every scheduled run adds
  one row per city; nothing is ever deleted.
- **`hourly_outlook`** — a refreshed 24-hour forecast cache. Every run
  replaces each city's rows entirely, since an outdated prediction has no
  value once a newer one exists.
## Requirements
 
### Software
- Python 3.10+
- PostgreSQL (no PostGIS extension needed — geometry lives only in the
  boundary file, not the database)
### Python packages
```bash
pip install requests geopandas psycopg2-binary
```
 
`geopandas` depends on GDAL under the hood. On Windows, if `pip install
geopandas` fails with a GDAL DLL error, this is a known Windows issue —
using a conda environment instead is the more reliable route:
```bash
conda create -n weather_app python=3.12
conda activate weather_app
conda install -c conda-forge geopandas requests psycopg2
```
 
### Data file
`data/LAD_major_city_boundary_data.gpkg` — a GeoPackage containing the
boundary polygons for the cities you want to track, sourced from the ONS
Open Geography Portal (Local Authority Districts). This isn't included in
the repo by default; you'll need to download and filter it to your chosen
cities yourself, or add it via Git LFS if the file is large.
 
## Setup
 
### 1. Create the database
```bash
psql -U postgres -c "CREATE DATABASE weather_db;"
psql -U postgres -d weather_db -f schema.sql
```
 
### 2. Set your database password as an environment variable
```bash
setx WEATHER_DB_PASSWORD "your_postgres_password"
```
Close and reopen your terminal after running this — `setx` only applies to
new sessions. For scheduled/unattended runs (Task Scheduler, cron), set it
as a **system-level** environment variable instead, since scheduled tasks
often don't inherit interactive user session variables.
 
### 3. Confirm the database connection works
```bash
python -c "from db import get_connection; get_connection(); print('Connected OK')"
```
 
### 4. Run the pipeline once, manually
```bash
python insert_forecasts.py
```
This fetches current weather + a 24-hour outlook for every city in the
boundary file and writes both to the database. Check for `Inserted
current: ...` and `Refreshed outlook: ...` lines with no `FAILED` entries.
 
### 5. Build the dashboard's data file
 
**Required before the dashboard will open successfully** — it never
generates its own data, it only reads a file this script produces:
```bash
python build_outlook_geojson.py
```
Produces `data/city_outlook.geojson`. Skipping this step, or running the
dashboard before `insert_forecasts.py` has ever populated `hourly_outlook`,
is the single most common reason the dashboard fails to load.
 
### 6. Serve and view the dashboard
```bash
python -m http.server 8000
```
Then open **http://localhost:8000/dashboard.html** in a browser. Opening
the HTML file directly (`file://...`) will not work — browsers block
`fetch()` requests from local files, so it must be served over HTTP.
 
## Scheduling recurring runs
 
Set up `insert_forecasts.py` to run on a timer (e.g. hourly) via Windows
Task Scheduler or cron, so `forecasts` accumulates real history and
`hourly_outlook` stays current. See the project notes for exact Task
Scheduler configuration (trigger: daily, repeat every 1 hour).
 
Re-run `build_outlook_geojson.py` (or schedule it too) whenever you want
the dashboard to reflect the latest data — it's decoupled from the fetch
step on purpose, so you can rebuild the dashboard file independently of
how often the underlying data refreshes.