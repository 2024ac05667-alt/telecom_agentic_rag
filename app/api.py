import os
import uuid
import json
import time
import sqlite3
import secrets
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from graph.workflow import run_diagnostic_pipeline

app = FastAPI(title="Qatar Telecom AI Diagnostic & SLA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Create & mount persistent disk storage for uploaded device photos
DATA_DIR = Path("data")
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "audit_logs.db"

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# 2. HTTP Basic Auth for Enterprise Admin Monitor
security = HTTPBasic()
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "qatar2026")


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    valid_user = secrets.compare_digest(credentials.username, ADMIN_USER)
    valid_pass = secrets.compare_digest(credentials.password, ADMIN_PASS)
    if not (valid_user and valid_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# 3. Initialize SQLite Database
def init_db():
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


init_db()


class PickupPayload(BaseModel):
    customer_name: str
    mobile_number: str
    doha_location: str
    device_issue: str = ""


@app.post("/api/diagnose")
async def diagnose_device(
    query: str = Form(...),
    images: List[UploadFile] = File(default=[]),
    image: Optional[UploadFile] = File(default=None),
):
    start_time = time.perf_counter()
    image_tuples: List[Tuple[bytes, str]] = []
    saved_images_meta: List[dict] = []
    saved_urls: List[str] = []

    all_uploads = list(images or [])
    if image is not None:
        all_uploads.append(image)

    for idx, upload in enumerate(all_uploads[:4]):
        raw_bytes = await upload.read()
        if not raw_bytes:
            continue

        ext = os.path.splitext(upload.filename or f"photo_{idx}.jpg")[1] or ".jpg"
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = UPLOAD_DIR / unique_name
        file_path.write_bytes(raw_bytes)

        public_url = f"http://127.0.0.1:8000/uploads/{unique_name}"
        saved_urls.append(public_url)
        saved_images_meta.append(
            {
                "name": upload.filename or unique_name,
                "dataUrl": public_url,
            }
        )
        image_tuples.append((raw_bytes, upload.content_type or "image/jpeg"))

    state = run_diagnostic_pipeline(query=query, images=image_tuples)
    latency = round(time.perf_counter() - start_time, 2)

    diagnostic_payload = {
        "status": "blocked" if state.get("is_out_of_scope") else "completed",
        "pii_scrubbed": bool(state.get("pii_scrubbed")),
        "is_out_of_scope": bool(state.get("is_out_of_scope")),
        "image_count": len(image_tuples),
        "image_urls": saved_urls,
        "customer_en": state.get("customer_en", ""),
        "customer_ar": state.get("customer_ar", ""),
        "response_en": state.get("response_en", ""),
        "response_ar": state.get("response_ar", ""),
        "hardware_assessment": state.get("hardware_assessment", ""),
        "policy_context": state.get("policy_context", ""),
        "agent_history": state.get("agent_history", []),
        "latency_seconds": latency,
    }

    log_id = f"LOG-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    scrubbed_q = state.get("scrubbed_query") or query

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO audit_logs (id, timestamp, user_query, images_json, diagnostic_json) VALUES (?, ?, ?, ?, ?)",
            (
                log_id,
                timestamp,
                scrubbed_q,
                json.dumps(saved_images_meta),
                json.dumps(diagnostic_payload),
            ),
        )

    return diagnostic_payload


@app.post("/api/pickup-request")
def create_pickup_request(payload: PickupPayload):
    ticket_id = f"QT-PKP-{uuid.uuid4().hex[:6].upper()}"
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO pickup_requests
            (id, created_at, customer_name, mobile_number, doha_location, device_issue, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                created_at,
                payload.customer_name.strip(),
                payload.mobile_number.strip(),
                payload.doha_location.strip(),
                payload.device_issue.strip(),
                "Scheduled",
            ),
        )

    return {
        "status": "scheduled",
        "ticket": {
            "id": ticket_id,
            "createdAt": created_at,
            "customerName": payload.customer_name.strip(),
            "mobileNumber": payload.mobile_number.strip(),
            "dohaLocation": payload.doha_location.strip(),
            "deviceIssue": payload.device_issue.strip(),
            "status": "Scheduled",
        },
    }


@app.get("/api/audit-logs")
def get_audit_logs(_: str = Depends(verify_admin)):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT id, timestamp, user_query, images_json, diagnostic_json FROM audit_logs ORDER BY rowid ASC"
        ).fetchall()

    logs = [
        {
            "id": row[0],
            "timestamp": row[1],
            "userQuery": row[2],
            "images": json.loads(row[3]),
            "diagnostic": json.loads(row[4]),
        }
        for row in rows
    ]
    return {"logs": logs}


@app.delete("/api/audit-logs")
def clear_audit_logs(_: str = Depends(verify_admin)):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM audit_logs")
    return {"status": "cleared"}


@app.get("/api/pickup-requests")
def get_pickup_requests(_: str = Depends(verify_admin)):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, customer_name, mobile_number, doha_location, device_issue, status
            FROM pickup_requests ORDER BY rowid DESC
            """
        ).fetchall()

    pickups = [
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
    return {"pickups": pickups}