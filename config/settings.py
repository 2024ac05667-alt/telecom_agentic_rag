"""
Centralized Configuration Settings for Qatar Mobile Multimodal Diagnostic Agent.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "Qatar Mobile Multimodal Hardware Diagnostic Agent"
    VERSION: str = "2.1.0"
    DEBUG: bool = True

    # API Keys (empty string default prevents passing invalid placeholder tokens)
    GEMINI_API_KEY: str = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
    GROQ_API_KEY: str = (os.getenv("GROQ_API_KEY") or "").strip()
    PREFER_GROQ: bool = os.getenv("PREFER_GROQ", "false").strip().lower() == "true"

    # Unified Persistent Storage Paths
    PERSIST_DIRECTORY: str = str(PROJECT_ROOT / "chroma_db")
    COLLECTION_NAME: str = "qatar_telecom_consumer_law"

    # Model Failover Chains
    GEMINI_VISION_MODELS: list[str] = [
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash",
    ]
    GEMINI_TEXT_MODELS: list[str] = [
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash",
    ]
    GROQ_TEXT_MODELS: list[str] = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.8-27b",
    ]

    # LangGraph Step Budget Guardrail
    MAX_AGENT_STEPS: int = 8

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()