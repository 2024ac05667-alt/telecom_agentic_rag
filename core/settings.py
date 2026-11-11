"""
Configuration Settings for Multimodal Diagnostic Agent.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Qatar Mobile Multimodal Hardware Diagnostic Agent"
    VERSION: str = "2.0.0"
    DEBUG: bool = True

    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")

    # Local Storage Paths
    PERSIST_DIRECTORY: str = "./data/chroma_db"
    DOCUMENT_SOURCE_PATH: str = "./data/qatar_sla_policy.pdf"

    # Model Specs
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    VISION_MODEL_NAME: str = "gemini-2.5-flash"
    SUPERVISOR_MODEL_NAME: str = "gemini-2.5-flash"

    class Config:
        env_file = ".env"


settings = Settings()