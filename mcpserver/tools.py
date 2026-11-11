"""
MCP Server Tools Definition.
Exposes modular tools via standard Model Context Protocol schema with fault isolation.
"""

from typing import Any, Dict, List
from core.guardrails import PIIGuardrail
from core.vector_store import PolicyVectorStore
from core.vision import VisualDiagnosticEngine

_guardrail = PIIGuardrail()
_vision = VisualDiagnosticEngine()
_vector_store = PolicyVectorStore()


class HardwareDiagnosticMCPServer:
    @staticmethod
    def get_tool_manifest() -> List[Dict[str, Any]]:
        return [
            {
                "name": "presidio_scrubber",
                "description": "Scrubs PII and Qatar IDs from text strings prior to LLM processing.",
                "input_schema": {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                },
            },
            {
                "name": "gemini_vision_inspector",
                "description": "Inspects mobile hardware images to identify physical defects.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "raw_bytes": {"type": "string"},
                        "context": {"type": "string"},
                    },
                },
            },
            {
                "name": "chromadb_policy_retriever",
                "description": "Retrieves matching Qatar warranty policy chunks from vector store.",
                "input_schema": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if tool_name == "presidio_scrubber":
                res = _guardrail.scrub_text(arguments.get("text", ""))
                return {"status": "success", "result": res}

            elif tool_name == "gemini_vision_inspector":
                bytes_data = arguments.get("raw_bytes")
                if not bytes_data:
                    return {"status": "skipped", "result": "No image attached for visual inspection."}
                diag = _vision.analyze_damage(bytes_data, arguments.get("context", ""))
                return {"status": "success", "result": diag}

            elif tool_name == "chromadb_policy_retriever":
                docs = _vector_store.retrieve_relevant_policy(arguments.get("query", ""))
                return {"status": "success", "result": docs}

            else:
                return {"status": "error", "message": f"Tool '{tool_name}' not found."}

        except Exception as e:
            return {"status": "error", "message": f"MCP execution fault: {str(e)}"}