import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

INCIDENT_DB = (
    BASE_DIR
    / "data"
    / "security"
    / "incidents.db"
)


SEVERITY_LEVELS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


INCIDENT_STATUSES = {
    "DETECTED",
    "INVESTIGATING",
    "CONTAINED",
    "RESOLVED",
}


def init_incident_db():
    INCIDENT_DB.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(INCIDENT_DB)

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            source_ip TEXT,
            endpoint TEXT,
            username TEXT,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            created_by TEXT DEFAULT 'SYSTEM',
            resolved_by TEXT,
            resolved_at TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def create_incident(
    event_type: str,
    severity: str,
    description: str,
    source_ip: str = None,
    endpoint: str = None,
    username: str = None,
    created_by: str = "SYSTEM",
):
    severity = severity.upper()

    if severity not in SEVERITY_LEVELS:
        raise ValueError("Invalid incident severity.")

    incident_id = f"INC-{uuid.uuid4().hex[:12].upper()}"

    timestamp = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(INCIDENT_DB)

    conn.execute(
        """
        INSERT INTO incidents (
            incident_id,
            timestamp,
            event_type,
            severity,
            source_ip,
            endpoint,
            username,
            description,
            status,
            created_by
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            incident_id,
            timestamp,
            event_type,
            severity,
            source_ip,
            endpoint,
            username,
            description,
            "DETECTED",
            created_by,
        ),
    )

    conn.commit()
    conn.close()

    return incident_id


def get_incidents(
    status: str = None,
    severity: str = None,
    limit: int = 100,
):
    if limit < 1:
        limit = 1

    if limit > 500:
        limit = 500

    query = """
        SELECT
            incident_id,
            timestamp,
            event_type,
            severity,
            source_ip,
            endpoint,
            username,
            description,
            status,
            created_by,
            resolved_by,
            resolved_at
        FROM incidents
        WHERE 1=1
    """

    params = []

    if status:
        status = status.upper()

        if status not in INCIDENT_STATUSES:
            raise ValueError("Invalid incident status.")

        query += " AND status = ?"
        params.append(status)

    if severity:
        severity = severity.upper()

        if severity not in SEVERITY_LEVELS:
            raise ValueError("Invalid incident severity.")

        query += " AND severity = ?"
        params.append(severity)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    conn = sqlite3.connect(INCIDENT_DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        query,
        params,
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def update_incident_status(
    incident_id: str,
    status: str,
    resolved_by: str = None,
):
    status = status.upper()

    if status not in INCIDENT_STATUSES:
        raise ValueError("Invalid incident status.")

    conn = sqlite3.connect(INCIDENT_DB)
    conn.row_factory = sqlite3.Row

    existing = conn.execute(
        """
        SELECT incident_id, status
        FROM incidents
        WHERE incident_id = ?
        """,
        (incident_id,),
    ).fetchone()

    if not existing:
        conn.close()
        return False

    current_status = existing["status"]

    allowed_transitions = {
        "DETECTED": {
            "INVESTIGATING",
            "CONTAINED",
        },
        "INVESTIGATING": {
            "CONTAINED",
            "RESOLVED",
        },
        "CONTAINED": {
            "INVESTIGATING",
            "RESOLVED",
        },
        "RESOLVED": set(),
    }

    if status != current_status:
        if status not in allowed_transitions.get(
            current_status,
            set()
        ):
            conn.close()

            raise ValueError(
                f"Invalid status transition: "
                f"{current_status} -> {status}"
            )

    resolved_at = None
    resolved_by_value = None

    if status == "RESOLVED":
        if not resolved_by:
            conn.close()
            raise ValueError(
                "resolved_by is required when resolving an incident."
            )

        resolved_at = datetime.now(timezone.utc).isoformat()
        resolved_by_value = resolved_by

    else:
        resolved_at = None
        resolved_by_value = None

    conn.execute(
        """
        UPDATE incidents
        SET
            status = ?,
            resolved_by = ?,
            resolved_at = ?
        WHERE incident_id = ?
        """,
        (
            status,
            resolved_by_value,
            resolved_at,
            incident_id,
        ),
    )

    conn.commit()
    conn.close()

    return True
    status = status.upper()

    if status not in INCIDENT_STATUSES:
        raise ValueError("Invalid incident status.")

    conn = sqlite3.connect(INCIDENT_DB)

    existing = conn.execute(
        """
        SELECT incident_id
        FROM incidents
        WHERE incident_id = ?
        """,
        (incident_id,),
    ).fetchone()

    if not existing:
        conn.close()
        return False

    resolved_at = None

    if status == "RESOLVED":
        resolved_at = datetime.now(timezone.utc).isoformat()

    conn.execute(
        """
        UPDATE incidents
        SET
            status = ?,
            resolved_by = ?,
            resolved_at = ?
        WHERE incident_id = ?
        """,
        (
            status,
            resolved_by,
            resolved_at,
            incident_id,
        ),
    )

    conn.commit()
    conn.close()

    return True


def count_recent_events(
    event_type: str,
    source_ip: str = None,
    minutes: int = 10,
):
    conn = sqlite3.connect(INCIDENT_DB)

    query = """
        SELECT COUNT(*)
        FROM incidents
        WHERE event_type = ?
        AND timestamp >= datetime('now', ?)
    """

    params = [
        event_type,
        f"-{minutes} minutes",
    ]

    if source_ip:
        query += " AND source_ip = ?"
        params.append(source_ip)

    count = conn.execute(
        query,
        params,
    ).fetchone()[0]

    conn.close()

    return count

def determine_incident_severity(
    event_type: str,
    source_ip: str = None,
):
    recent_count = count_recent_events(
        event_type=event_type,
        source_ip=source_ip,
        minutes=10,
    )

    if recent_count >= 10:
        return "CRITICAL"

    if recent_count >= 5:
        return "HIGH"

    if event_type == "RATE_LIMIT_EXCEEDED":
        return "HIGH"

    if event_type in {
        "UNAUTHORIZED_ACCESS",
        "LOGIN_FAILED",
    }:
        return "MEDIUM"

    if event_type == "FORBIDDEN_ACCESS":
        return "HIGH"

    if event_type == "IP_BLOCKED":
        return "CRITICAL"

    return "LOW"

BLOCK_THRESHOLD = 10
BLOCK_DURATION_MINUTES = 30


def is_ip_blocked(source_ip: str):
    if not source_ip:
        return False

    conn = sqlite3.connect(INCIDENT_DB)

    row = conn.execute(
        """
        SELECT COUNT(*)
        FROM incidents
        WHERE source_ip = ?
        AND timestamp >= datetime('now', ?)
        """,
        (
            source_ip,
            f"-{BLOCK_DURATION_MINUTES} minutes",
        ),
    ).fetchone()

    conn.close()

    return row[0] >= BLOCK_THRESHOLD


def should_block_ip(source_ip: str):
    if not source_ip:
        return False

    recent_events = count_recent_events(
        event_type="LOGIN_FAILED",
        source_ip=source_ip,
        minutes=10,
    )

    recent_unauthorized = count_recent_events(
        event_type="UNAUTHORIZED_ACCESS",
        source_ip=source_ip,
        minutes=10,
    )

    recent_rate_limits = count_recent_events(
        event_type="RATE_LIMIT_EXCEEDED",
        source_ip=source_ip,
        minutes=10,
    )

    total_suspicious_events = (
        recent_events
        + recent_unauthorized
        + recent_rate_limits
    )

    return total_suspicious_events >= BLOCK_THRESHOLD

init_incident_db()