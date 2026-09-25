import logging
import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

logger = logging.getLogger(__name__)


@tool
async def google_search(query: str) -> str:
    """Search Google Custom Search and return up to three speech-friendly results."""
    query = query.strip()
    if not query:
        return "Search query खाली है।"

    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_engine_id = os.getenv("SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        missing = []
        if not api_key:
            missing.append("GOOGLE_SEARCH_API_KEY")
        if not search_engine_id:
            missing.append("SEARCH_ENGINE_ID")
        return f"Missing environment variables: {', '.join(missing)}"

    try:
        response = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": api_key,
                "cx": search_engine_id,
                "q": query,
                "num": 3,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        logger.exception("Google Search request failed")
        return f"Google Search API request failed: {exc}"

    results = data.get("items", [])
    if not results:
        return "कोई search results नहीं मिले।"

    lines = ["Top search results:"]
    for index, item in enumerate(results, start=1):
        title = item.get("title", "No title").strip()
        snippet = item.get("snippet", "").strip()
        lines.append(f"{index}. {title}. {snippet}")

    return "\n".join(lines)


@tool
async def get_current_datetime() -> str:
    """Return the computer's current local date and time."""
    return datetime.now().strftime("%d %B %Y, %I:%M %p")
