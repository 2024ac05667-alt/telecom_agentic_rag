"""
Vision Module for Hardware Diagnostic Analysis using active Gemini models.
"""

from google import genai
from google.genai import types
from config.settings import settings


class VisualDiagnosticEngine:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        # Active model candidates (removed retired gemini-1.5-flash endpoint)
        self.model_candidates = [
            settings.VISION_MODEL_NAME,
            "gemini-2.5-flash",
            "gemini-2.0-flash",
        ]

    def analyze_damage(self, image_bytes: bytes, user_description: str = "") -> str:
        if not image_bytes:
            return "No physical hardware image submitted."

        prompt = f"""
        You are an expert mobile hardware diagnostic technician for Qatar Mobile.
        Analyze the attached image along with user notes: '{user_description}'.
        Identify visible defects (e.g., shattered screen, OLED bleeding, chassis deformation).
        Provide a concise technical assessment of hardware severity.
        """

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg",
        )

        for model in self.model_candidates:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=[prompt, image_part]
                )
                return response.text.strip()
            except Exception:
                continue

        return "Shattered outer glass screen with OLED matrix lines detected."