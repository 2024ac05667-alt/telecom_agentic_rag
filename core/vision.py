"""
Multimodal Hardware Defect Vision Inspector for Doha Connect (dohaconnect.qa).
"""

import logging
from typing import List, Tuple, Optional
from google import genai
from google.genai import types
from config.settings import settings

logger = logging.getLogger(__name__)

_vision_client = (
    genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=15000),
    )
    if settings.GEMINI_API_KEY
    else None
)


def inspect_device_images(
    images: Optional[List[Tuple[bytes, str]]] = None,
    user_query: str = "",
) -> str:
    """
    Inspects up to 4 customer-uploaded images for Doha Connect (dohaconnect.qa):
    - Recognizes smartphones, tablets, laptops/MacBooks, gaming consoles (PS5, Nintendo Switch),
      smartwatches, smart TVs/streaming boxes, power banks, and charging/screen hardware.
    - If ALL images are unrelated to consumer electronics/gadgets, returns 'NON_TELECOM_IMAGE'.
    - If AT LEAST ONE image shows a valid consumer electronic device, skips any unrelated
      images and diagnoses all valid hardware photos together.
    """
    valid_images = [(b, m) for (b, m) in (images or []) if b]
    if not valid_images:
        return "No images attached — text-only diagnostic triage."

    if not _vision_client:
        return "Vision client unconfigured — proceeding with text-based diagnostic triage."

    prompt = (
        "You are an expert hardware diagnostic vision inspector for Doha Connect (dohaconnect.qa), "
        "a consumer electronics retailer and repair center in Doha, Qatar.\n"
        "Examine EVERY attached image individually:\n"
        "1. Determine whether each image shows a consumer electronic product sold or serviced by Doha Connect: "
        "smartphones (iPhone, Samsung Galaxy, etc.), tablets (iPad, etc.), laptops/MacBooks, gaming consoles/controllers "
        "(PS5, Nintendo Switch), smartwatches, smart TVs/streaming boxes, air purifiers, or power banks/chargers.\n"
        "2. If NONE of the attached images show a consumer electronic device, respond ONLY with the exact token: NON_TELECOM_IMAGE\n"
        "3. If AT LEAST ONE image shows a valid consumer electronic device, ignore any unrelated/non-device image(s) "
        "(such as food, vehicles, or ISP fiber telecom racks) and provide a concise, objective technical defect diagnosis "
        "covering ALL valid device photos (e.g., spiderweb glass fracture from impact, OLED black ink bleed/green vertical lines, "
        "USB-C/HDMI port liquid or green corrosion, swollen lithium battery lifting back cover, or overheating/fan failure). "
        "If you skipped any unrelated image(s), append '[PARTIAL_INVALID_IMAGE]' at the end of your assessment.\n"
        f"Customer Query Context: {user_query}"
    )

    contents: list = [prompt]
    for img_bytes, mime_type in valid_images[:4]:
        contents.append(
            types.Part.from_bytes(
                data=img_bytes,
                mime_type=mime_type or "image/jpeg",
            )
        )

    for model_id in settings.GEMINI_VISION_MODELS:
        try:
            response = _vision_client.models.generate_content(
                model=model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                ),
            )
            text = (response.text or "").strip()
            if text:
                return text
        except Exception as exc:
            logger.warning("Vision failover from %s: %s", model_id, exc)

    return "Vision Service Busy — proceeding with customer text description and Qatar Consumer Law RAG."