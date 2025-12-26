"""
Standalone test script for Perplexity API - can run without app setup.
Usage: python tests/test_perplexity_standalone.py YOUR_API_KEY
"""
import sys
import json
import requests
import re


def test_perplexity_api(api_key: str, model_name: str, test_type: str = "local_items"):
    """
    Test Perplexity API with a specific model and return full response.
    
    Args:
        api_key: Perplexity API key
        model_name: The model to test (e.g., "sonar", "sonar-pro")
        test_type: "local_items" or "public_transport"
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    if test_type == "local_items":
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
    
    # Add web search options if model supports it
    if "sonar" in model_name.lower() or "online" in model_name.lower():
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
                print(f"Content length: {len(raw_content)} characters")
                print(f"{'='*80}\n")
                
                # Try to find JSON array like current code does
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
                        print(f"\n✓ Model '{model_name}' is COMPATIBLE with current parsing logic!")
                        return True
                    except json.JSONDecodeError as e:
                        print(f"✗ Failed to parse JSON: {e}")
                        print(f"Cleaned block (first 500 chars): {cleaned_block[:500]}...")
                        return False
                else:
                    print("✗ No JSON array found in response")
                    print("First 500 chars of content:")
                    print(raw_content[:500])
                    return False
                    
            except (KeyError, IndexError) as e:
                print(f"✗ Error extracting content: {e}")
                print("Response structure:")
                print(json.dumps(response_data, indent=2, ensure_ascii=False))
                return False
        else:
            print(f"ERROR: {response.status_code}")
            error_text = response.text
            
            # Check for 401 - Authentication error
            if response.status_code == 401:
                print("\n" + "="*80)
                print("⚠️  AUTHENTICATION ERROR (401)")
                print("="*80)
                print("\nPossible issues:")
                print("1. API key is invalid or expired")
                print("2. API key format is incorrect")
                print("3. API key should start with 'pplx-' (e.g., pplx-xxxxxxxxxxxxx)")
                print("\nTo get your API key:")
                print("1. Go to https://www.perplexity.ai/")
                print("2. Sign up or log in")
                print("3. Navigate to Settings > API")
                print("4. Copy your API key")
                print("\nMake sure you're using the full API key, not a placeholder.")
                print("="*80 + "\n")
            
            # Try to parse error JSON
            try:
                error_json = json.loads(error_text)
                if "error" in error_json:
                    error_msg = error_json['error'].get('message', 'N/A')
                    print(f"\nError message: {error_msg}")
                    if "deprecated" in error_msg.lower() or "model" in error_msg.lower():
                        print("\n⚠️  Model-related error detected. Try a different model.")
            except:
                pass
            
            print(f"\nRaw error response:")
            print(error_text[:500])  # First 500 chars
            return False
            
    except Exception as e:
        print(f"✗ Exception occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Test different Perplexity models."""
    if len(sys.argv) < 2:
        print("Usage: python tests/test_perplexity_standalone.py YOUR_API_KEY [model_name] [test_type]")
        print("\nExample:")
        print("  python tests/test_perplexity_standalone.py pplx-xxx...")
        print("  python tests/test_perplexity_standalone.py pplx-xxx... sonar local_items")
        print("  python tests/test_perplexity_standalone.py pplx-xxx... sonar-pro public_transport")
        print("\nNote: API key should start with 'pplx-' and be your full Perplexity API key")
        sys.exit(1)
    
    api_key = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "sonar"
    test_type = sys.argv[3] if len(sys.argv) > 3 else "local_items"
    
    # Validate API key format
    if not api_key.startswith("pplx-") and len(api_key) < 20:
        print("\n⚠️  WARNING: API key doesn't look correct.")
        print("Perplexity API keys typically start with 'pplx-'")
        print(f"Your key starts with: {api_key[:10]}...")
        print("\nContinue anyway? (This might fail with 401 error)")
        response = input("Press Enter to continue or Ctrl+C to cancel: ")
    
    print("\n" + "="*80)
    print("PERPLEXITY API TEST SCRIPT (Standalone)")
    print("="*80)
    print(f"\nAPI Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"Model: {model_name}")
    print(f"Test Type: {test_type}\n")
    
    success = test_perplexity_api(api_key, model_name, test_type)
    
    if success:
        print(f"\n{'='*80}")
        print("✓ SUCCESS: Model is compatible!")
        print(f"{'='*80}\n")
        print(f"Update app/external_services/ai_suggestions.py line 140:")
        print(f'  Change: "model": "sonar-reasoning"')
        print(f'  To:     "model": "{model_name}"\n')
    else:
        print(f"\n{'='*80}")
        print("✗ FAILED: Model returned incompatible format or error")
        print(f"{'='*80}\n")
        print("Try a different model:")
        print("  - sonar")
        print("  - sonar-pro")
        print("  - sonar-online")
        print("  - llama-3.1-sonar-small-128k-online")
        print("  - llama-3.1-sonar-large-128k-online\n")


if __name__ == "__main__":
    main()

