import os
import json
import time
import base64
import secrets
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from graph.workflow import run_diagnostic_pipeline

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Qatar Telecom Multimodal Diagnostic RAG API",
    description="LangGraph + Gemini 3.5/3.8 + ChromaDB grounded in Qatar Consumer Protection Law No. 8 (2008)",
    version="4.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()
ADMIN_USERNAME = (os.getenv("ADMIN_USERNAME") or "admin").strip().strip('"').strip("'")
ADMIN_PASSWORD = (os.getenv("ADMIN_PASSWORD") or "qatar2026").strip().strip('"').strip("'")

# ============================================================================
# SQLITE PERSISTENT STORAGE (AUDIT LOGS + CONSENTED PICKUP CONTACTS)
# ============================================================================
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "audit_logs.db"


def _init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                user_query TEXT NOT NULL,
                images_json TEXT NOT NULL,
                diagnostic_json TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pickup_requests (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                mobile_number TEXT NOT NULL,
                doha_location TEXT NOT NULL,
                device_issue TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _save_audit_entry(entry: dict) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO audit_logs (id, timestamp, user_query, images_json, diagnostic_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                entry["id"],
                entry["timestamp"],
                entry["userQuery"],
                json.dumps(entry["images"]),
                json.dumps(entry["diagnostic"]),
            ),
        )
        conn.commit()


def _load_audit_entries(limit: int = 100) -> List[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT id, timestamp, user_query, images_json, diagnostic_json
            FROM audit_logs
            ORDER BY rowid ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        {
            "id": row[0],
            "timestamp": row[1],
            "userQuery": row[2],
            "images": json.loads(row[3]),
            "diagnostic": json.loads(row[4]),
        }
        for row in rows
    ]


def _clear_audit_entries() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM audit_logs")
        conn.commit()


def _save_pickup_request(req: dict) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO pickup_requests (id, created_at, customer_name, mobile_number, doha_location, device_issue, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                req["id"],
                req["createdAt"],
                req["customerName"],
                req["mobileNumber"],
                req["dohaLocation"],
                req["deviceIssue"],
                req["status"],
            ),
        )
        conn.commit()


def _load_pickup_requests(limit: int = 100) -> List[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, customer_name, mobile_number, doha_location, device_issue, status
            FROM pickup_requests
            ORDER BY rowid DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        {
            "id": row[0],
            "createdAt": row[1],
            "customerName": row[2],
            "mobileNumber": row[3],
            "dohaLocation": row[4],
            "deviceIssue": row[5],
            "status": row[6],
        }
        for row in rows
    ]


def _clear_pickup_requests() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM pickup_requests")
        conn.commit()


_init_db()


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    provided_user = (credentials.username or "").strip()
    provided_pass = (credentials.password or "").strip()

    is_valid_user = secrets.compare_digest(
        provided_user.encode("utf-8"), ADMIN_USERNAME.encode("utf-8")
    )
    is_valid_pass = secrets.compare_digest(
        provided_pass.encode("utf-8"), ADMIN_PASSWORD.encode("utf-8")
    )
    if not (is_valid_user and is_valid_pass):
        logger.warning("Failed admin login attempt for username: %r", provided_user)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administrator credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return provided_user


class DiagnosticAPIResponse(BaseModel):
    status: str
    pii_scrubbed: bool
    is_out_of_scope: bool
    image_count: int
    customer_en: str
    customer_ar: str
    response_en: str
    response_ar: str
    hardware_assessment: str
    policy_context: str
    agent_history: list[str]
    latency_seconds: float


class PickupRequestCreate(BaseModel):
    customer_name: str
    mobile_number: str
    doha_location: str
    device_issue: str = ""


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "model": "gemini-3.5-flash-lite",
        "law_version": "Qatar Law No. 8 (2008)",
        "storage": "sqlite",
    }


@app.get("/api/audit-logs")
def get_audit_logs(_admin: str = Depends(verify_admin)):
    return {"logs": _load_audit_entries()}


@app.delete("/api/audit-logs")
def clear_audit_logs(_admin: str = Depends(verify_admin)):
    _clear_audit_entries()
    return {"status": "cleared"}


@app.post("/api/pickup-request")
def create_pickup_request(body: PickupRequestCreate):
    name = body.customer_name.strip()
    mobile = body.mobile_number.strip()
    location = body.doha_location.strip()
    if not name or not mobile or not location:
        raise HTTPException(status_code=400, detail="Name, mobile number, and Doha location are required.")

    ticket_id = f"QT-PKP-{int(time.time() * 1000) % 1000000}"
    record = {
        "id": ticket_id,
        "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "customerName": name,
        "mobileNumber": mobile,
        "dohaLocation": location,
        "deviceIssue": body.device_issue.strip()[:300],
        "status": "Pending Courier Dispatch",
    }
    _save_pickup_request(record)
    return {"status": "scheduled", "ticket": record}


@app.get("/api/pickup-requests")
def list_pickup_requests(_admin: str = Depends(verify_admin)):
    return {"pickups": _load_pickup_requests()}


@app.delete("/api/pickup-requests")
def delete_pickup_requests(_admin: str = Depends(verify_admin)):
    _clear_pickup_requests()
    return {"status": "cleared"}


@app.post("/api/diagnose", response_model=DiagnosticAPIResponse)
async def diagnose_device(
    query: str = Form(...),
    images: List[UploadFile] = File(default=[]),
    image: Optional[UploadFile] = File(None),
):
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")

    start_time = time.perf_counter()

    all_uploads: List[UploadFile] = [f for f in images if f and f.filename]
    if image is not None and image.filename:
        all_uploads.append(image)

    image_tuples: List[Tuple[bytes, str]] = []
    admin_image_previews: List[dict] = []

    for upload in all_uploads[:4]:
        raw_bytes = await upload.read()
        if not raw_bytes:
            continue
        mime = upload.content_type or "image/jpeg"
        image_tuples.append((raw_bytes, mime))
        b64_str = base64.b64encode(raw_bytes).decode("utf-8")
        admin_image_previews.append(
            {
                "name": upload.filename or "defect_photo.jpg",
                "dataUrl": f"data:{mime};base64,{b64_str}",
            }
        )

    clean_query = query.strip()
    result_state = run_diagnostic_pipeline(
        query=clean_query,
        images=image_tuples,
    )

    elapsed = round(time.perf_counter() - start_time, 2)

    payload = DiagnosticAPIResponse(
        status="success",
        pii_scrubbed=bool(result_state.get("pii_scrubbed", False)),
        is_out_of_scope=bool(result_state.get("is_out_of_scope", False)),
        image_count=len(image_tuples),
        customer_en=result_state.get("customer_en") or result_state.get("response_en", ""),
        customer_ar=result_state.get("customer_ar") or result_state.get("response_ar", ""),
        response_en=result_state.get("response_en", ""),
        response_ar=result_state.get("response_ar", ""),
        hardware_assessment=result_state.get("hardware_assessment", ""),
        policy_context=result_state.get("policy_context", ""),
        agent_history=result_state.get("agent_history", []),
        latency_seconds=elapsed,
    )

    safe_audit_query = result_state.get("scrubbed_query") or clean_query

    _save_audit_entry(
        {
            "id": f"{int(time.time() * 1000)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "userQuery": safe_audit_query,
            "images": admin_image_previews,
            "diagnostic": payload.model_dump(),
        }
    )

    return payload