"""Google Translate connector for text translation."""
from typing import Optional
from app.external_services.googletrans import translate_text
from googletrans import Translator


class GoogleTranslateConnector:
    """Connector for Google Translate API."""
    
    def __init__(self):
        """Initialize the Google Translate connector."""
        self.translator = Translator()

    async def translate(self, text: str, target_lang: str, origin_lang: str = 'auto') -> str:
        """Translate text to a target language.
        
        Args:
            text: The input text to translate.
            target_lang: Target language code (e.g., 'en', 'de').
            origin_lang: Source language code (e.g., 'en', 'de', 'auto'), defaults to 'auto'.
            
        Returns:
            Translated text string, or None if translation fails.
        """
        return await translate_text(self.translator, text, target_lang, origin_lang)