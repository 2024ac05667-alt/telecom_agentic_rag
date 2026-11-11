"""
Multilingual Translation Module.
Handles Arabic-English bi-directional translation for processing & RTL UI response.
"""

from deep_translator import GoogleTranslator
from google import genai
from config.settings import settings


class TranslatorEngine:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.fallback_ar_to_en = GoogleTranslator(source="auto", target="en")
        self.fallback_en_to_ar = GoogleTranslator(source="en", target="ar")

    def translate_ar_to_en(self, arabic_text: str) -> str:
        if not arabic_text or not arabic_text.strip():
            return ""

        prompt = f"""
        You are a technical translator specializing in consumer electronics diagnostics.
        Translate the following Arabic user input into clear, technical English.
        Preserve technical terms (e.g., screen crack, battery, QID, motherboard).
        Input: {arabic_text}
        """

        try:
            response = self.client.models.generate_content(
                model=settings.SUPERVISOR_MODEL_NAME,
                contents=prompt
            )
            return response.text.strip()
        except Exception:
            return self.fallback_ar_to_en.translate(arabic_text)

    def translate_en_to_ar(self, english_text: str) -> str:
        if not english_text or not english_text.strip():
            return ""

        prompt = f"""
        You are a technical translator.
        Translate the following technical mobile diagnostic report into natural Arabic.
        Input: {english_text}
        """

        try:
            response = self.client.models.generate_content(
                model=settings.SUPERVISOR_MODEL_NAME,
                contents=prompt
            )
            return response.text.strip()
        except Exception:
            return self.fallback_en_to_ar.translate(english_text)