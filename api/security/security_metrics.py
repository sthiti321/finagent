import sqlite3

from api.security.audit import AUDIT_DB
from api.security.incident_response import INCIDENT_DB


def get_security_metrics():
    metrics = {
        "audit_events": 0,
        "security_incidents": 0,
        "critical_incidents": 0,
        "high_incidents": 0,
        "resolved_incidents": 0,
    }

    # Audit metrics
    if AUDIT_DB.exists():
        conn = sqlite3.connect(AUDIT_DB)

        metrics["audit_events"] = conn.execute(
            "SELECT COUNT(*) FROM audit_events"
        ).fetchone()[0]

        conn.close()

    # Incident metrics
    if INCIDENT_DB.exists():
        conn = sqlite3.connect(INCIDENT_DB)

        metrics["security_incidents"] = conn.execute(
            "SELECT COUNT(*) FROM incidents"
        ).fetchone()[0]

        metrics["critical_incidents"] = conn.execute(
            """
            SELECT COUNT(*)
            FROM incidents
            WHERE severity = 'CRITICAL'
            """
        ).fetchone()[0]

        metrics["high_incidents"] = conn.execute(
            """
            SELECT COUNT(*)
            FROM incidents
            WHERE severity = 'HIGH'
            """
        ).fetchone()[0]

        metrics["resolved_incidents"] = conn.execute(
            """
            SELECT COUNT(*)
            FROM incidents
            WHERE status = 'RESOLVED'
            """
        ).fetchone()[0]

        conn.close()

    return metrics