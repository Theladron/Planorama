"""
Test script to check Perplexity API response format with updated models.
This helps verify if the current parsing logic can handle the new API responses.
"""
import os
import sys
import json
import requests
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config_loader import settings


def test_perplexity_api(model_name: str, test_type: str = "local_items"):
    """
    Test Perplexity API with a specific model and return full response.
    
    Args:
        model_name: The model to test (e.g., "sonar", "sonar-pro", "sonar-online")
        test_type: "local_items" or "public_transport"
    """
    api_key = settings.AI_API_KEY
    
    if not api_key:
        print("ERROR: AI_API_KEY not set in environment variables")
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    if test_type == "local_items":
        # Test for local items (hotels, activities, etc.)
        prompt = """You must return exactly three real and verifiable hotels in or near 
                Hamburg (latitude 53.576158, longitude 10.007046), using only real search results. 
                Output must be a JSON array with exactly three entries, no extra text or reasoning. 
                Each entry must have a title, url, description, latitude and longitude. 
                Do not include any <think> or other commentary. Strictly follow this structure:

[
  {
    "title": "...",
    "url": "https://...",
    "description": "...",
    "lat": 53.x,
    "lon": 10.x
  },
  ...
]

Reject any site that lacks real coordinates or a confirmed working URL. Output nothing outside of the JSON."""
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system",
                 "content": "You are a strict assistant. Output only valid JSON when instructed. No explanation or internal thoughts."},
                {"role": "user", "content": prompt}
            ]
        }
        
        # Add web search options if model supports it
        if "sonar" in model_name.lower():
            payload["web_search_options"] = {
                "search_context_size": "high",
                "user_location": {
                    "country": "DE",
                    "latitude": 53.576158,
                    "longitude": 10.007046
                }
            }
    
    else:  # public_transport
        prompt = """You must return exactly three real and verifiable public transport route options from Hamburg (latitude 53.576158, longitude 10.007046) to Berlin (latitude 52.524932, longitude 13.407032).

Use only real search results. The output must be a JSON array with exactly three entries. Each entry must contain:

- "method_of_transport": e.g. "train", "bus", "tram", "ferry"
- "url": a real and working link to buy tickets or view the route
- "description": a short summary of the route, including key stops or transfers and estimated duration
- "departure_time": a real and verifiable scheduled departure time in 24h format (e.g. "15:42") that is not in the past
- "price": a rough real-world price in euros (e.g. "€29.90" or a range like "€19–49")

Strictly output only the JSON array in this exact format:

[
  {
    "method_of_transport": "train",
    "url": "https://...",
    "description": "Take ICE from Hamburg Hbf to Berlin Hbf, direct route.",
    "departure_time": "14:45",
    "price": "€29.90"
  },
  ...
]

Do not include markdown, explanations, commentary, or anything outside the JSON array. Reject entries with missing or unverifiable data."""
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system",
                 "content": "You are a strict assistant. Output only valid JSON when instructed. No explanation or internal thoughts."},
                {"role": "user", "content": prompt}
            ]
        }
        
        if "sonar" in model_name.lower():
            payload["web_search_options"] = {
                "search_context_size": "high",
                "user_location": {
                    "country": "DE",
                    "latitude": 53.576158,
                    "longitude": 10.007046
                }
            }
    
    print(f"\n{'='*80}")
    print(f"Testing model: {model_name}")
    print(f"Test type: {test_type}")
    print(f"{'='*80}\n")
    
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"\n{'='*80}")
        print("FULL RESPONSE:")
        print(f"{'='*80}\n")
        
        if response.status_code == 200:
            response_data = response.json()
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
            # Try to extract content like the current code does
            print(f"\n{'='*80}")
            print("EXTRACTED CONTENT (as current code would parse it):")
            print(f"{'='*80}\n")
            
            try:
                raw_content = response_data["choices"][0]["message"]["content"]
                print("Raw content:")
                print(raw_content)
                print(f"\n{'='*80}")
                print("Content length:", len(raw_content))
                print(f"{'='*80}\n")
                
                # Try to find JSON array like current code does
                import re
                match = re.search(r"(\[\s*{.*?}\s*\])", raw_content, re.DOTALL)
                if match:
                    raw_block = match.group(1)
                    print("Found JSON block:")
                    print(raw_block)
                    print(f"\n{'='*80}")
                    print("Attempting to parse JSON:")
                    print(f"{'='*80}\n")
                    try:
                        cleaned_block = raw_block.replace('\n', '').replace('\\"', '"')
                        result_data = json.loads(cleaned_block)
                        print("✓ Successfully parsed JSON!")
                        print(json.dumps(result_data, indent=2, ensure_ascii=False))
                        return response_data
                    except json.JSONDecodeError as e:
                        print(f"✗ Failed to parse JSON: {e}")
                        print(f"Cleaned block: {cleaned_block[:500]}...")
                else:
                    print("✗ No JSON array found in response")
                    print("First 500 chars of content:")
                    print(raw_content[:500])
                    
            except (KeyError, IndexError) as e:
                print(f"✗ Error extracting content: {e}")
                print("Response structure:")
                print(json.dumps(response_data, indent=2, ensure_ascii=False))
        else:
            print(f"ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"✗ Exception occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    return None


def main():
    """Test different Perplexity models to find a working one."""
    print("\n" + "="*80)
    print("PERPLEXITY API TEST SCRIPT")
    print("="*80)
    print("\nThis script tests the Perplexity API with different models")
    print("to verify response format compatibility with current parsing logic.\n")
    
    # Models to test (based on Perplexity docs)
    models_to_test = [
        "sonar",           # Standard sonar model
        "sonar-pro",       # Pro version
        "sonar-online",    # Online version
        "llama-3.1-sonar-small-128k-online",
        "llama-3.1-sonar-large-128k-online",
    ]
    
    test_type = "local_items"  # Change to "public_transport" to test that
    
    print(f"Testing with: {test_type}\n")
    
    for model in models_to_test:
        result = test_perplexity_api(model, test_type)
        if result:
            print(f"\n✓ Model '{model}' works! Response structure is compatible.")
            print("\nYou can update app/external_services/ai_suggestions.py")
            print(f"to use model: '{model}' instead of 'sonar-reasoning'\n")
            break
        else:
            print(f"\n✗ Model '{model}' failed or returned incompatible format\n")
            input("Press Enter to test next model...")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

