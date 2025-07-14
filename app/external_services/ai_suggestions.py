import requests
import json
import re
import time

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

    Parameters:
        api_key (str): Your Perplexity API key.
        town_name (str): Name of the town to search near.
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        language (str): 'en' or 'de' for English or German prompt.
        content_type (str): What to search for (e.g., 'campsites', 'hotels', 'activities').
        max_retries (int): Number of retries if extraction/parsing fails (default 3).
        retry_delay (float): Delay in seconds between retries (default 1 second).

    Returns:
        list[dict]: List of parsed location entries with title, url, description, lat, lon.
    """

    # Prompt templates
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

    prompt = prompts.get(language.lower())
    if not prompt:
        raise ValueError("Invalid language. Use 'en' or 'de'.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar-reasoning",
        "usage_tier": "low",
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
        except (KeyError, IndexError) as e:
            raise ValueError("Invalid response format.") from e

        # Try to extract JSON block and parse
        match = re.search(r"(\[\s*{.*?}\s*\])", raw_content, re.DOTALL)
        if match:
            raw_block = match.group(1)
            try:
                cleaned_block = raw_block.replace('\n', '').replace('\\"', '"')
                result_data = json.loads(cleaned_block)
                return result_data
            except json.JSONDecodeError:
                pass  # parsing failed, will retry
        # If no match or parsing failed:
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
        else:
            raise ValueError("Could not extract valid JSON block from response after multiple attempts.")
