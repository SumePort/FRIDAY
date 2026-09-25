import logging
import os

import requests
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

logger = logging.getLogger(__name__)


def get_current_city() -> str:
    """Best-effort city detection from the current public IP."""
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        response.raise_for_status()
        return response.json().get("city") or ""
    except requests.RequestException:
        logger.exception("Could not determine current city")
        return ""


@tool
async def get_weather(city: str = "") -> str:
    """Return current weather for a city, or detect the city when omitted."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "OPENWEATHER_API_KEY environment variable नहीं मिली।"

    city = city.strip() or get_current_city()
    if not city:
        return "Current city detect नहीं हो पाई। कृपया city का नाम बताइए।"

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": api_key,
                "units": "metric",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        logger.exception("Weather request failed for %s", city)
        return f"{city} का weather fetch नहीं हो पाया।"

    weather = data.get("weather", [{}])[0].get("description", "Unknown").title()
    main = data.get("main", {})
    wind = data.get("wind", {})

    return (
        f"Weather in {city}: "
        f"{weather}, {main.get('temp', 'N/A')}°C, "
        f"humidity {main.get('humidity', 'N/A')}%, "
        f"wind {wind.get('speed', 'N/A')} m/s."
    )
