# Perplexity API Test Scripts

These scripts help test the Perplexity API with updated models to verify compatibility with the current parsing logic.

## Files

1. **`test_perplexity_api.py`** - Uses app configuration (requires app setup)
2. **`test_perplexity_standalone.py`** - Standalone version (can run independently)

## Usage

### Standalone Version (Recommended)

```bash
# Basic usage - tests with "sonar" model
python tests/test_perplexity_standalone.py YOUR_API_KEY

# Test specific model
python tests/test_perplexity_standalone.py YOUR_API_KEY sonar-pro

# Test public transport instead of local items
python tests/test_perplexity_standalone.py YOUR_API_KEY sonar public_transport
```

### App-integrated Version

```bash
# Make sure you're in the project root and have .env configured
python tests/test_perplexity_api.py
```

## What It Tests

The scripts will:
1. Call the Perplexity API with a test prompt
2. Show the **full response** structure
3. Attempt to parse the response using the **current parsing logic**
4. Verify if the response format is compatible

## Models to Try

Based on Perplexity documentation, try these models:
- `sonar` - Standard sonar model
- `sonar-pro` - Pro version
- `sonar-online` - Online version  
- `llama-3.1-sonar-small-128k-online`
- `llama-3.1-sonar-large-128k-online`

## Expected Output

The script will show:
- Full API response JSON
- Raw content extracted from response
- Whether JSON parsing succeeds
- Compatibility status with current code

If a model works, you'll see:
```
✓ Successfully parsed JSON!
✓ Model 'sonar' is COMPATIBLE with current parsing logic!
```

Then update `app/external_services/ai_suggestions.py` line 140 to use the working model.

