"""
Model Context Protocol (MCP) Microservice Server for Qatar Mobile Diagnostics.
Exposes Presidio PII Scrubbing, Gemini Flash Vision Inspection, and ChromaDB
Legal Policy Retrieval as standardized MCP tools over stdio transport.
"""

import sys
import json
import base64
import logging
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is on sys.path when spawned as an MCP stdio subprocess
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging strictly to stderr so stdout remains clean for MCP JSON-RPC
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("qatar_mobile_mcp_server")

# Compatible with both MCP Python SDK v2 (MCPServer) and v1 (FastMCP)
try:
    from mcp.server import MCPServer as _MCPServerClass
except ImportError:
    from mcp.server.fastmcp import FastMCP as _MCPServerClass

from core.guardrails import PIIGuardrail
from core.vision import inspect_device_images
from core.vector_store import query_legal_docs

mcp = _MCPServerClass("QatarMobileDiagnosticMCP")

# Lazy singleton for Presidio so fast tools don't pay spaCy load overhead unless invoked
_guardrail_instance: PIIGuardrail | None = None


def _get_guardrail() -> PIIGuardrail:
    global _guardrail_instance
    if _guardrail_instance is None:
        _guardrail_instance = PIIGuardrail()
    return _guardrail_instance


@mcp.tool()
def presidio_scrubber(text: str) -> str:
    """
    Scrubs PII, phone numbers, and 11-digit Qatar National IDs (QID) via Microsoft Presidio
    prior to LLM processing. Returns JSON string with clean_text, pii_detected, and detected_entities.
    """
    result = _get_guardrail().scrub_text(text)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def gemini_vision_inspector(
    images_payload_json: str,
    user_query: str = "",
) -> str:
    """
    Inspects up to 4 base64-encoded device photos via Gemini Flash for physical hardware defects.
    Expects images_payload_json as a JSON list of {"b64": "...", "mime_type": "image/jpeg"}.
    """
    try:
        items = json.loads(images_payload_json) if images_payload_json else []
    except Exception:
        items = []

    decoded_images: list[tuple[bytes, str]] = []
    for item in items[:4]:
        b64_str = item.get("b64", "")
        mime_type = item.get("mime_type", "image/jpeg")
        if b64_str:
            decoded_images.append((base64.b64decode(b64_str), mime_type))

    return inspect_device_images(images=decoded_images, user_query=user_query)


@mcp.tool()
def chromadb_policy_retriever(query: str, top_k: int = 2) -> str:
    """
    Retrieves matching Qatar Consumer Protection Law No. 8 (2008), Ministerial Decision No. 68 (2012),
    and CRA SLA clauses from ChromaDB. Returns JSON list of matched policy strings.
    """
    docs: List[str] = query_legal_docs(query_text=query, top_k=top_k)
    return json.dumps(docs, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")