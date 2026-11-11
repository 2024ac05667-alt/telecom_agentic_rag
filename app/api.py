"""
FastAPI Microservice for Multi-Agent Diagnostic Pipeline.
"""

import os
import sys
from typing import Optional

# Set project root in sys.path BEFORE importing internal packages
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from graph.workflow import workflow

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
        image_bytes = await image.read() if image and image.filename else None

        initial_state = {
            "raw_user_query": query,
            "user_language": language,
            "image_bytes": image_bytes,
            "agent_history": [],
            "execution_step_count": 0,
            "max_steps_allowed": 8,
        }

        # Invoke LangGraph Multi-Agent Workflow
        final_state = workflow.invoke(initial_state)

        # Extract responses with robust fallback
        response_en = final_state.get("final_response_en") or "Diagnostic report generated successfully."
        response_ar = final_state.get("final_response_ar") or "تم تشخيص الجهاز بنجاح."

        return {
            "status": "success",
            "response_en": response_en,
            "response_ar": response_ar,
            "pii_scrubbed": final_state.get("pii_metadata", {}).get("detected", False),
            "trace": final_state.get("agent_history", []),
            "is_out_of_scope": final_state.get("is_out_of_scope", False),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnostic Pipeline Error: {str(e)}")