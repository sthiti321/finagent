import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
AUDIT_DB = BASE_DIR / "data" / "security" / "audit.db"


def init_audit_db():
    AUDIT_DB.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(AUDIT_DB)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_events (
            audit_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            resource TEXT,
            resource_id TEXT,
            ip_address TEXT,
            result TEXT NOT NULL,
            details TEXT,
            previous_hash TEXT,
            event_hash TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def _get_last_hash():
    conn = sqlite3.connect(AUDIT_DB)

    row = conn.execute("""
        SELECT event_hash
        FROM audit_events
        ORDER BY rowid DESC
        LIMIT 1
    """).fetchone()

    conn.close()

    return row[0] if row else ""


def _calculate_event_hash(event_data: dict, previous_hash: str):
    payload = {
        **event_data,
        "previous_hash": previous_hash,
    }

    canonical_data = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        canonical_data.encode("utf-8")
    ).hexdigest()


def record_audit_event(
    username: str,
    action: str,
    resource: str = None,
    resource_id: str = None,
    ip_address: str = None,
    result: str = "SUCCESS",
    details: str = None,
):
    audit_id = f"AUD-{uuid.uuid4().hex[:12].upper()}"

    timestamp = datetime.now(timezone.utc).isoformat()

    previous_hash = _get_last_hash()

    event_data = {
        "audit_id": audit_id,
        "timestamp": timestamp,
        "username": username,
        "action": action,
        "resource": resource,
        "resource_id": resource_id,
        "ip_address": ip_address,
        "result": result,
        "details": details,
    }

    event_hash = _calculate_event_hash(
        event_data,
        previous_hash,
    )

    conn = sqlite3.connect(AUDIT_DB)

    conn.execute("""
        INSERT INTO audit_events (
            audit_id,
            timestamp,
            username,
            action,
            resource,
            resource_id,
            ip_address,
            result,
            details,
            previous_hash,
            event_hash
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        audit_id,
        timestamp,
        username,
        action,
        resource,
        resource_id,
        ip_address,
        result,
        details,
        previous_hash,
        event_hash,
    ))

    conn.commit()
    conn.close()

    return audit_id


def get_audit_events(limit: int = 100):
    if limit < 1:
        limit = 1

    if limit > 500:
        limit = 500

    conn = sqlite3.connect(AUDIT_DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            audit_id,
            timestamp,
            username,
            action,
            resource,
            resource_id,
            ip_address,
            result,
            details,
            previous_hash,
            event_hash
        FROM audit_events
        ORDER BY rowid DESC
        LIMIT ?
    """, (limit,)).fetchall()

    conn.close()

    return [dict(row) for row in rows]

def verify_audit_integrity():
    conn = sqlite3.connect(AUDIT_DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            audit_id,
            timestamp,
            username,
            action,
            resource,
            resource_id,
            ip_address,
            result,
            details,
            previous_hash,
            event_hash
        FROM audit_events
        ORDER BY rowid ASC
    """).fetchall()

    conn.close()

    previous_hash = ""

    for row in rows:
        event_data = {
            "audit_id": row["audit_id"],
            "timestamp": row["timestamp"],
            "username": row["username"],
            "action": row["action"],
            "resource": row["resource"],
            "resource_id": row["resource_id"],
            "ip_address": row["ip_address"],
            "result": row["result"],
            "details": row["details"],
        }

        if row["previous_hash"] != previous_hash:
            return {
                "valid": False,
                "audit_id": row["audit_id"],
                "reason": "Previous hash mismatch",
            }

        calculated_hash = _calculate_event_hash(
            event_data,
            previous_hash,
        )

        if calculated_hash != row["event_hash"]:
            return {
                "valid": False,
                "audit_id": row["audit_id"],
                "reason": "Event hash mismatch",
            }

        previous_hash = row["event_hash"]

    return {
        "valid": True,
        "events_checked": len(rows),
        "message": "Audit trail integrity verified successfully.",
    }

init_audit_db()