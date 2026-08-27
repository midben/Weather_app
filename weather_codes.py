WMO_CODES = {
    0:  {"description": "Clear sky", "icon": "sun"},
    1:  {"description": "Mainly clear", "icon": "sun"},
    2:  {"description": "Partly cloudy", "icon": "cloud-sun"},
    3:  {"description": "Overcast", "icon": "cloud"},
    45: {"description": "Fog", "icon": "fog"},
    48: {"description": "Depositing rime fog", "icon": "fog"},
    51: {"description": "Light drizzle", "icon": "drizzle"},
    53: {"description": "Moderate drizzle", "icon": "drizzle"},
    55: {"description": "Dense drizzle", "icon": "drizzle"},
    61: {"description": "Slight rain", "icon": "rain"},
    63: {"description": "Moderate rain", "icon": "rain"},
    65: {"description": "Heavy rain", "icon": "rain-heavy"},
    71: {"description": "Slight snow", "icon": "snow"},
    73: {"description": "Moderate snow", "icon": "snow"},
    75: {"description": "Heavy snow", "icon": "snow-heavy"},
    80: {"description": "Slight rain showers", "icon": "rain"},
    81: {"description": "Moderate rain showers", "icon": "rain"},
    82: {"description": "Violent rain showers", "icon": "rain-heavy"},
    95: {"description": "Thunderstorm", "icon": "storm"},
    96: {"description": "Thunderstorm, slight hail", "icon": "storm"},
    99: {"description": "Thunderstorm, heavy hail", "icon": "storm"},
}


def get_weather_info(weather_code):
    return WMO_CODES.get(weather_code, {"description": "Unknown", "icon": "cloud"})
