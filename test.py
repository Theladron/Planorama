import requests
import json

# Replace this with your actual Perplexity API key
API_KEY = "your_api_key_here"

url = "https://api.perplexity.ai/chat/completions"

headers = {
    "Authorization": f"Bearer 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",
    "Content-Type": "application/json"
}
lat=53.576158
lon=10.007046
town_name = "Hamburg"
content_type = "Museums"


payload = {
    "model": "sonar-reasoning",
    "usage_tier": "low",
    "web_search_options": {
        "search_context_size": "high",
        "user_location": {
            "country": "DE",
            "latitude": 53.576158,
            "longitude": 10.007046
        }
    },
    "messages": [
        {
            "role": "system",
            "content": "You are a strict assistant. Output only valid JSON when instructed. No explanation or internal thoughts."
        },
        {
            "role": "user",
            "content": (
f"""You must return exactly three real and verifiable {content_type} in or near {town_name} (latitude {lat}, longitude {lon}), using only real search results. Output must be a JSON array with exactly three entries, no extra text or reasoning. Each entry must have a title, url, description, latitude and longitude. Do not include any <think> or other commentary. Strictly follow this structure:

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

Reject any site that lacks real coordinates or a confirmed working URL. Output nothing outside of the JSON."""
            )
        }
    ]
}

resp = requests.post("https://api.perplexity.ai/chat/completions",
                     headers=headers,
                     json=payload)

response = requests.post(url, headers=headers, json=payload)

# Print the full JSON response (debugging or exploration)
print(response.status_code)
if response.status_code == 200:
    print(json.dumps(response.json(), indent=4))
else:
    print(f"Error {response.status_code}: {response.text}")