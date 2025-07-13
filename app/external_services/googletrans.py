from googletrans import Translator
from typing import Optional

async def translate_text(translator: Translator, text: str, target_lang: str, origin_lang: str) -> Optional[str]:
    """
    Translates a given text to the specified language using Google Translate.

    Args:
        translator (googletrans.Translator): Google Translate translator instance.
        text (str): The text to translate.
        target_lang (str): Target language code (e.g., 'en' for English, 'de' for German).

    Returns:
        Optional[str]: Translated text, or None if translation failed.
    """
    try:
        result = await translator.translate(text, src=origin_lang, dest=target_lang)
        return result.text
    except Exception:
        return None