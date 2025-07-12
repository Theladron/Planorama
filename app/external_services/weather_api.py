import requests
from typing import Optional, List, Dict

WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️❄️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    61: ("Slight rain", "🌧️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️🌧️"),
    66: ("Freezing rain", "🌧️❄️"),
    67: ("Heavy freezing rain", "🌧️❄️❄️"),
    71: ("Slight snow", "🌨️"),
    73: ("Moderate snow", "🌨️"),
    75: ("Heavy snow", "❄️❄️"),
    80: ("Rain showers", "🌦️"),
    81: ("Heavy rain showers", "🌧️🌧️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️❄️")
}


def get_weather_forecast(lat: float, lon: float) -> Optional[Dict]:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weathercode",
        "daily": "temperature_2m_max,temperature_2m_min,weathercode,sunrise,sunset",
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        current_time = current.get("time")
        current_temp = current.get("temperature_2m")
        current_code = current.get("weathercode")
        current_desc, current_icon = WEATHER_CODES.get(current_code, ("Unknown", "❓"))

        daily = data.get("daily", {})
        today = {
            "date": daily["time"][0],
            "temp_min": daily["temperature_2m_min"][0],
            "temp_max": daily["temperature_2m_max"][0],
            "weathercode": daily["weathercode"][0],
            "sunrise": daily["sunrise"][0],
            "sunset": daily["sunset"][0],
        }
        today_desc, today_icon = WEATHER_CODES.get(today["weathercode"], ("Unknown", "❓"))

        # Create full forecast for the next 7 days
        forecast = []
        for i in range(len(daily["time"])):
            code = daily["weathercode"][i]
            desc, icon = WEATHER_CODES.get(code, ("Unknown", "❓"))
            forecast.append({
                "date": daily["time"][i],
                "temp_min": daily["temperature_2m_min"][i],
                "temp_max": daily["temperature_2m_max"][i],
                "description": desc,
                "icon": icon,
                "sunrise": daily["sunrise"][i],
                "sunset": daily["sunset"][i],
            })

        return {
            "location": {"lat": lat, "lon": lon},
            "current": {
                "time": current_time,
                "temperature": current_temp,
                "description": current_desc,
                "icon": current_icon
            },
            "today": {
                "date": today["date"],
                "temp_min": today["temp_min"],
                "temp_max": today["temp_max"],
                "description": today_desc,
                "icon": today_icon,
                "sunrise": today["sunrise"],
                "sunset": today["sunset"]
            },
            "forecast": forecast
        }

    except (requests.RequestException, KeyError, IndexError, TypeError):
        return None
