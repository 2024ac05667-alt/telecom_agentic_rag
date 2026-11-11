"""
Configuration Settings for Qatar Mobile Multi-Agent Diagnostic Pipeline.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base Project Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    
    # Vector Store Directories (Aliased for compatibility across modules)
    CHROMA_PERSIST_DIR: str = str(DATA_DIR / "chroma_db")
    PERSIST_DIRECTORY: str = str(DATA_DIR / "chroma_db")
    DOCUMENT_SOURCE_PATH: str = str(DATA_DIR / "qatar_sla_policy.pdf")

    # API Keys & Credentials
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")

    # LLM & Multi-Agent Model Configuration (Updated to Gemini 3.8 Flash)
    SUPERVISOR_MODEL_NAME: str = "gemini-3.8-flash"
    VISION_MODEL_NAME: str = "gemini-3.8-flash"
    POLICY_MODEL_NAME: str = "gemini-3.8-flash"

    # Vector Store & Embedding Configuration
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    COLLECTION_NAME: str = "qatar_sla_policies"
    TOP_K_RETRIEVAL: int = 3

    # Safety Guardrails & Privacy
    QID_REGEX_PATTERN: str = r"\b\d{11}\b"
    DEFAULT_LANGUAGE: str = "en"

    # MCP & Server Settings
    MCP_SERVER_HOST: str = "127.0.0.1"
    MCP_SERVER_PORT: int = 8000
    MAX_STEP_BUDGET: int = 8

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()