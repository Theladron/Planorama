from googletrans import Translator
from typing import Optional

"""Google Translate integration for text translation."""
from googletrans import Translator
from typing import Optional

async def translate_text(translator: Translator, text: str, target_lang: str, origin_lang: str) -> Optional[str]:
    """Translate text to a target language using Google Translate.
    
    Args:
        translator: Google Translate translator instance.
        text: The text to translate.
        target_lang: Target language code (e.g., 'en' for English, 'de' for German).
        origin_lang: Source language code (e.g., 'en', 'de', or 'auto').
        
    Returns:
        Translated text if successful, None if translation failed.
    """
    try:
        result = await translator.translate(text, src=origin_lang, dest=target_lang)
        return result.text
    except Exception:
        return None