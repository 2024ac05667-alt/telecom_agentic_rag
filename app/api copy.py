"""
FastAPI Microservice for Multi-Agent Diagnostic Pipeline.
"""

from typing import Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from graph.workflow import workflow
import os
import sys
from typing import optional

PROJECT_ROOT=  os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

app = FastAPI(
    title="Qatar Mobile Multi-Agent API",
    version="2.0.0",
    description="Multi-Agent Supervisor RAG Agent with MCP Tools",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "online", "system": "Dell Latitude Node (24GB RAM Active)"}


@app.post("/diagnose")
async def process_diagnosis(
    query: str = Form(...),
    language: str = Form("en"),
    image: Optional[UploadFile] = File(None),
):
    try:
        image_bytes = await image.read() if image else None

        initial_state = {
            "raw_user_query": query,
            "anonymized_query": "",
            "image_bytes": image_bytes,
            "user_language": language,
            "next_agent": "Supervisor",
            "agent_history": [],
            "execution_step_count": 0,
            "max_steps_allowed": 8,
            "is_out_of_scope": False,
            "is_service_unsupported": False,
            "is_system_overflow": False,
            "fallback_reason": "",
            "pii_metadata": {},
            "visual_inspection_report": "",
            "retrieved_policy_chunks": [],
            "final_response_en": "",
            "final_response_ar": "",
        }

        final_output = workflow.invoke(initial_state)

        return {
            "success": True,
            "execution_trace": final_output.get("agent_history", []),
            "pii_scrubbed": final_output.get("pii_metadata", {}).get("detected", False),
            "diagnosis": final_output.get("visual_inspection_report", ""),
            "response_en": final_output.get("final_response_en", ""),
            "response_ar": final_output.get("final_response_ar", ""),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))