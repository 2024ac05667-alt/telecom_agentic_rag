"""
Vision Module for Hardware Diagnostic Analysis using Gemini 2.5 Flash.
"""

import google.generativeai as genai
from config.settings import settings

genai.configure(api_key=settings.GEMINI_API_KEY)


class VisualDiagnosticEngine:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.VISION_MODEL_NAME)

    def analyze_damage(self, image_bytes: bytes, user_description: str = "") -> str:
        if not image_bytes:
            return "No physical hardware image submitted."

        prompt = f"""
        You are an expert mobile device repair technician for Qatar Mobile. 
        Examine the image carefully alongside the user's description: '{user_description}'.
        Identify visible physical defects (e.g., screen crack, battery swelling, port erosion, water damage indicator).
        Provide a concise 2-sentence technical diagnostic summary.
        """

        image_part = {"mime_type": "image/jpeg", "data": image_bytes}

        try:
            response = self.model.generate_content([prompt, image_part])
            return response.text.strip()
        except Exception as e:
            return f"Visual inspection failure: {str(e)}"