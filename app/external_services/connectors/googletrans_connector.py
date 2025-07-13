from typing import Optional
from app.external_services.googletrans import translate_text
from googletrans import Translator


class GoogleTranslateConnector:

    def __init__(self):
        self.translator = Translator()

    async def translate(self, text: str, target_lang: str, origin_lang: str = 'auto') -> str:
        """
        Translate a single text to the specified target language.

        Args:
            text (str): The input text to translate.
            target_lang (str): The target language code (e.g., 'en', 'de').

        Returns:
            Optional[str]: The translated string or None if it fails.
        """
        return await translate_text(self.translator, text, target_lang, origin_lang)