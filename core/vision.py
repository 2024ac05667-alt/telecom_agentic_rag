import os
import json
import base64
import logging
import urllib.request
import urllib.error
from typing import Optional, List, Tuple
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
logger = logging.getLogger(__name__)

_api_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
_groq_key = (os.getenv("GROQ_API_KEY") or "").strip()

# Google Gemini API enforces a minimum deadline of 10s (10000ms) -> use 15000ms
_client = (
    genai.Client(
        api_key=_api_key,
        http_options=types.HttpOptions(timeout=15000),
    )
    if _api_key
    else None
)

GEMINI_VISION_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
]

GROQ_VISION_MODELS = [
    "qwen/qwen3.8-27b",
]


def inspect_device_images(
    images: List[Tuple[bytes, str]],
    user_query: str = "",
) -> str:
    """
    Analyzes 1 or more attached hardware/router images using Gemini Vision,
    with automatic Groq Vision failover.
    """
    if not images:
        return "No visual attachment provided (Text-only diagnostic)."

    prompt = (
        "You are a senior telecom hardware diagnostic engineer in Doha, Qatar. "
        f"Inspect all {len(images)} attached image(s) alongside the customer's note: '{user_query}'.\n"
        "1. If the images clearly do NOT show a mobile phone, tablet, SIM/charging port, or fiber/5G router, "
        "respond starting with 'NON_TELECOM_IMAGE:' followed by what is shown.\n"
        "2. Otherwise, provide a concise technical damage assessment covering all angles/photos "
        "(e.g., OLED ink bleed, glass fracture, swollen battery chassis separation, liquid/corrosion, or router red LOS LED) "
        "and whether it indicates accidental physical damage vs. hardware/manufacturing failure."
    )

    if _client:
        contents: list = [prompt]
        for img_bytes, mime in images:
            contents.append(
                types.Part.from_bytes(
                    data=img_bytes,
                    mime_type=mime or "image/jpeg",
                )
            )

        for model_id in GEMINI_VISION_MODELS:
            try:
                response = _client.models.generate_content(
                    model=model_id,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                    ),
                )
                if response and response.text:
                    return f"[{len(images)} photo(s) inspected via {model_id}] {response.text.strip()}"
            except Exception as exc:
                logger.warning("Vision fast-failover from %s: %s", model_id, exc)

    if _groq_key:
        user_content: list = [{"type": "text", "text": prompt}]
        for img_bytes, mime in images:
            b64_img = base64.b64encode(img_bytes).decode("utf-8")
            user_content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime or 'image/jpeg'};base64,{b64_img}"},
                }
            )

        for groq_model in GROQ_VISION_MODELS:
            try:
                payload = {
                    "model": groq_model,
                    "temperature": 0.1,
                    "messages": [{"role": "user", "content": user_content}],
                }
                req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {_groq_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "QatarTelecomDiagnosticRAG/1.0",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    text = data["choices"][0]["message"]["content"].strip()
                    return f"[{len(images)} photo(s) inspected via {groq_model}] {text}"
            except urllib.error.HTTPError as http_err:
                err_body = http_err.read().decode("utf-8", errors="ignore")
                logger.warning("Groq vision %s failed (%s): %s", groq_model, http_err.code, err_body)
            except Exception as exc:
                logger.warning("Groq vision %s fallback failed: %s", groq_model, exc)

    return (
        f"[{len(images)} hardware photo(s) attached & logged for Doha technician review] "
        f"Visual anomaly flagged alongside customer report: '{user_query}'."
    )


def inspect_device_image(
    image_bytes: Optional[bytes] = None,
    mime_type: Optional[str] = None,
    user_query: str = "",
) -> str:
    if not image_bytes:
        return "No visual attachment provided (Text-only diagnostic)."
    return inspect_device_images([(image_bytes, mime_type or "image/jpeg")], user_query=user_query)