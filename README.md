# FRIDAY — Voice Desktop AI Assistant

FRIDAY is a Python voice assistant prototype built around LiveKit Agents, Gemini, LangChain, and Windows desktop automation.

## Current capabilities

- Real-time voice conversation through LiveKit + Gemini Live
- Hinglish assistant personality
- Google Custom Search
- Current date/time
- Current weather
- Desktop app launching/closing
- File and folder operations
- Keyboard and mouse automation
- Basic JSON conversation memory

## Requirements

- Python 3.10–3.14
- A LiveKit project
- A Google Gemini API key
- Optional Google Custom Search credentials
- Optional OpenWeather API key
- Windows for the desktop-control features

## Setup

Create a virtual environment:

    python -m venv .venv
    .venv\Scripts\activate

Install dependencies:

    python -m pip install --upgrade pip
    pip install -r requirements.txt

Create a local .env file from .env.example and fill in your credentials.

Run the assistant:

    python agent.py console

## Environment variables

- LIVEKIT_URL
- LIVEKIT_API_KEY
- LIVEKIT_API_SECRET
- GOOGLE_API_KEY
- GOOGLE_SEARCH_API_KEY (optional)
- SEARCH_ENGINE_ID (optional)
- OPENWEATHER_API_KEY (optional)
- FRIDAY_USER_ID (optional)

## Security

Never commit .env, API keys, conversation memory, or desktop-control logs.

The desktop-control tools can click, type, open, close, rename, and delete files. Add explicit permission/confirmation controls before giving FRIDAY unattended autonomy.
