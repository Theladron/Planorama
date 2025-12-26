import requests
import json
import re
import time
from datetime import datetime


def fetch_local_items(
    api_key: str,
    town_name: str,
    lat: float,
    lon: float,
    language: str,
    content_type: str,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> list:
    """
    Fetches real-world geographic data (e.g., campsites, hotels) near a town using Perplexity AI.
    """
    prompts = {
        "en": f"""You must return exactly three real and verifiable {content_type} in or near 
                {town_name} (latitude {lat}, longitude {lon}), using only real search results. 
                Output must be a JSON array with exactly three entries, no extra text or reasoning. 
                Each entry must have a title, url, description, latitude and longitude. 
                Do not include any <think> or other commentary. Strictly follow this structure:

[
  {{
    "title": "...",
    "url": "https://...",
    "description": "...",
    "lat": 53.x,
    "lon": 10.x
  }},
  ...
]

Reject any site that lacks real coordinates or a confirmed working URL. Output nothing outside of the JSON.""",

        "de": f"""Gib genau drei echte und überprüfbare {content_type} in oder nahe bei {town_name} 
        (Breitengrad {lat}, Längengrad {lon}) aus, basierend auf realen Suchergebnissen. 
        Gib ausschließlich ein JSON-Array mit genau drei Einträgen zurück, ohne zusätzlichen 
        Text oder Erklärungen. Jeder Eintrag muss folgende Felder enthalten: title, url, 
        description, lat, lon. Gib absolut keinen Kommentar oder <think>-Block aus.

Folge dieser Struktur:

[
  {{
    "title": "...",
    "url": "https://...",
    "description": "...",
    "lat": 53.x,
    "lon": 10.x
  }},
  ...
]

Verwerfe alle Orte ohne echte Koordinaten oder funktionierende URL. Gib nur das JSON zurück."""
    }

    return _query_perplexity(api_key, prompts.get(language.lower()), lat, lon, max_retries, retry_delay)


def fetch_public_transport(
    api_key: str,
    start_city: str,
    start_lat: float,
    start_lon: float,
    end_city: str,
    end_lat: float,
    end_lon: float,
    language: str = "en",
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> list:
    """
    Fetches public transport options between two cities using Perplexity AI.
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    prompts = {
        "en": f"""You must return exactly three real and verifiable public transport route options from {start_city} (latitude {start_lat}, longitude {start_lon}) to {end_city} (latitude {end_lat}, longitude {end_lon}) as of the current time: {current_time}.

Use only real search results. The output must be a JSON array with exactly three entries. Each entry must contain:

- "method_of_transport": e.g. "train", "bus", "tram", "ferry", "flight" or "plane"
- "url": a real and working link to buy tickets or view the route
- "description": a short summary of the route, including key stops or transfers and estimated duration
- "departure_time": a real and verifiable scheduled departure time in 24h format (e.g. "15:42") that is not in the past
- "price": a rough real-world price in euros (e.g. "€29.90" or a range like "€19–49")

IMPORTANT: If feasible (if there are airports near {start_city} and {end_city} that make sense to use), include at least one flight route. Also include at least one bus route if available. Prioritize diverse transportation methods.

Strictly output only the JSON array in this exact format:

[
  {{
    "method_of_transport": "train",
    "url": "https://...",
    "description": "Take ICE from Hamburg Hbf to Berlin Hbf, direct route.",
    "departure_time": "14:45",
    "price": "€29.90"
  }},
  ...
]

Do not include markdown, explanations, commentary, or anything outside the JSON array. Reject entries with missing or unverifiable data.""",

        "de": f"""Gib genau drei echte und überprüfbare öffentliche Verkehrsverbindungen von {start_city} (Breitengrad {start_lat}, Längengrad {start_lon}) nach {end_city} (Breitengrad {end_lat}, Längengrad {end_lon}) an – mit Abfahrtszeitpunkt zum aktuellen Zeitpunkt: {current_time}.

Nutze ausschließlich echte Suchergebnisse. Das Ergebnis muss ein JSON-Array mit genau drei Einträgen sein. Jeder Eintrag muss Folgendes enthalten:

- "method_of_transport": z.B. "Zug", "Bus", "Tram", "Fähre", "Flug" oder "Flugzeug"
- "url": funktionierender Link zum Ticket oder zur Routenansicht
- "description": Kurzbeschreibung mit Umstiegen und Dauer
- "departure_time": geplante Abfahrtszeit im 24h-Format (z.B. "15:42"), die in der Zukunft liegt
- "price": realistischer Preis in Euro (z.B. "€29.90" oder "€19–49")

WICHTIG: Falls machbar (wenn es Flughäfen in der Nähe von {start_city} und {end_city} gibt, die Sinn ergeben), schließe mindestens eine Flugroute ein. Schließe auch mindestens eine Busverbindung ein, falls verfügbar. Priorisiere vielfältige Verkehrsmittel.

Gib ausschließlich das JSON-Array in diesem Format aus – ohne Erklärung, Kommentare oder sonstigen Text."""
    }

    return _query_perplexity(api_key, prompts.get(language.lower()), start_lat, start_lon, max_retries, retry_delay)


def _query_perplexity(api_key: str,
                      prompt: str,
                      lat: float,
                      lon: float,
                      max_retries: int,
                      retry_delay: float) -> list:
    if not prompt:
        raise ValueError("Invalid or missing language prompt.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar",
        "web_search_options": {
            "search_context_size": "high",
            "user_location": {
                "country": "DE",
                "latitude": lat,
                "longitude": lon
            }
        },
        "messages": [
            {"role": "system",
             "content": "You are a strict assistant. Output only valid JSON when instructed. No explanation or internal thoughts."},
            {"role": "user", "content": prompt}
        ]
    }

    for attempt in range(max_retries):
        response = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=payload)

        if response.status_code != 200:
            raise RuntimeError(f"API error {response.status_code}: {response.text}")

        try:
            raw_content = response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as error:
            raise ValueError("Invalid response format.") from error

        match = re.search(r"(\[\s*{.*?}\s*\])", raw_content, re.DOTALL)
        if match:
            raw_block = match.group(1)
            try:
                cleaned_block = raw_block.replace('\n', '').replace('\\"', '"')
                result_data = json.loads(cleaned_block)
                return result_data
            except json.JSONDecodeError:
                pass  # retry
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
        else:
            raise ValueError("Could not extract valid JSON block from response after multiple attempts.")
