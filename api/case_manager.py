import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# DATABASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
CASE_DB = BASE_DIR / "data" / "security" / "cases.db"


# ============================================================
# CASE STATUSES
# ============================================================

CASE_STATUSES = {
    "OPEN",
    "INVESTIGATING",
    "CONTAINED",
    "RESOLVED",
}


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_case_db():
    CASE_DB.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = sqlite3.connect(CASE_DB)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            status TEXT NOT NULL,
            risk_data TEXT,
            evidence_data TEXT,
            investigation_data TEXT,
            report_data TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# CREATE CASE
# ============================================================

def create_case(
    customer_id: str,
    created_by: str,
):
    case_id = f"CASE-{uuid.uuid4().hex[:12].upper()}"

    now = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(CASE_DB)

    conn.execute("""
        INSERT INTO cases (
            case_id,
            customer_id,
            created_by,
            created_at,
            updated_at,
            status,
            risk_data,
            evidence_data,
            investigation_data,
            report_data
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id,
        customer_id,
        created_by,
        now,
        now,
        "OPEN",
        None,
        None,
        None,
        None,
    ))

    conn.commit()
    conn.close()

    return get_case(case_id)


# ============================================================
# GET SINGLE CASE
# ============================================================

def get_case(case_id: str):

    conn = sqlite3.connect(CASE_DB)
    conn.row_factory = sqlite3.Row

    row = conn.execute("""
        SELECT
            case_id,
            customer_id,
            created_by,
            created_at,
            updated_at,
            status,
            risk_data,
            evidence_data,
            investigation_data,
            report_data
        FROM cases
        WHERE case_id = ?
    """, (
        case_id,
    )).fetchone()

    conn.close()

    if not row:
        return None

    return dict(row)


# ============================================================
# GET ALL CASES
# ============================================================

def get_cases(
    customer_id: str = None,
    status: str = None,
    limit: int = 100,
):

    if limit < 1:
        limit = 1

    if limit > 500:
        limit = 500

    if status:

        status = status.upper()

        if status not in CASE_STATUSES:
            raise ValueError(
                "Invalid case status."
            )

    query = """
        SELECT
            case_id,
            customer_id,
            created_by,
            created_at,
            updated_at,
            status,
            risk_data,
            evidence_data,
            investigation_data,
            report_data
        FROM cases
        WHERE 1=1
    """

    params = []

    if customer_id:

        query += """
            AND customer_id = ?
        """

        params.append(
            customer_id
        )

    if status:

        query += """
            AND status = ?
        """

        params.append(
            status
        )

    query += """
        ORDER BY created_at DESC
        LIMIT ?
    """

    params.append(
        limit
    )

    conn = sqlite3.connect(CASE_DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        query,
        params,
    ).fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# UPDATE CASE STATUS
# ============================================================

def update_case_status(
    case_id: str,
    status: str,
):

    status = status.upper()

    if status not in CASE_STATUSES:
        raise ValueError(
            "Invalid case status."
        )

    conn = sqlite3.connect(CASE_DB)
    conn.row_factory = sqlite3.Row

    existing = conn.execute("""
        SELECT
            case_id,
            status
        FROM cases
        WHERE case_id = ?
    """, (
        case_id,
    )).fetchone()

    if not existing:

        conn.close()

        return False

    current_status = existing["status"]

    allowed_transitions = {

        "OPEN": {
            "INVESTIGATING",
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
            set(),
        ):

            conn.close()

            raise ValueError(
                f"Invalid case status transition: "
                f"{current_status} -> {status}"
            )

    updated_at = datetime.now(
        timezone.utc
    ).isoformat()

    conn.execute("""
        UPDATE cases
        SET
            status = ?,
            updated_at = ?
        WHERE case_id = ?
    """, (
        status,
        updated_at,
        case_id,
    ))

    conn.commit()
    conn.close()

    return True


# ============================================================
# ATTACH CASE DATA
# ============================================================

def attach_case_data(
    case_id: str,
    field: str,
    data: str,
):

    allowed_fields = {
        "risk_data",
        "evidence_data",
        "investigation_data",
        "report_data",
    }

    if field not in allowed_fields:

        raise ValueError(
            "Invalid case data field."
        )

    conn = sqlite3.connect(CASE_DB)

    existing = conn.execute("""
        SELECT
            case_id
        FROM cases
        WHERE case_id = ?
    """, (
        case_id,
    )).fetchone()

    if not existing:

        conn.close()

        return False

    updated_at = datetime.now(
        timezone.utc
    ).isoformat()

    query = f"""
        UPDATE cases
        SET
            {field} = ?,
            updated_at = ?
        WHERE case_id = ?
    """

    conn.execute(
        query,
        (
            data,
            updated_at,
            case_id,
        ),
    )

    conn.commit()
    conn.close()

    return True


# ============================================================
# INITIALIZE DATABASE
# ============================================================

init_case_db()