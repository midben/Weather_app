import os
import psycopg2
 
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "weather_db",
    "user": "postgres",
    "password": os.environ.get("WEATHER_DB_PASSWORD"),
}
 
 
def get_connection():
    if not DB_CONFIG["password"]:
        raise RuntimeError(
            "WEATHER_DB_PASSWORD environment variable is not set. "
            "Run: setx WEATHER_DB_PASSWORD \"your_postgres_password\" "
            "then open a new terminal."
        )
    return psycopg2.connect(**DB_CONFIG)