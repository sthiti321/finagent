import os
from pathlib import Path

from api.security.audit import AUDIT_DB
from api.security.incident_response import INCIDENT_DB
from api.security.dependency_security import check_dependencies


BASE_DIR = Path(__file__).resolve().parent.parent.parent


def check_jwt_secret():
    secret = os.getenv("FINAGENT_JWT_SECRET")

    if not secret:
        return {
            "status": "FAIL",
            "message": "JWT secret is not configured.",
        }

    if len(secret) < 32:
        return {
            "status": "FAIL",
            "message": "JWT secret is too short.",
        }

    return {
        "status": "PASS",
        "message": "JWT secret is configured securely.",
    }


def check_audit_database():
    if AUDIT_DB.exists():
        return {
            "status": "PASS",
            "message": "Audit database exists.",
        }

    return {
        "status": "FAIL",
        "message": "Audit database is missing.",
    }


def check_incident_database():
    if INCIDENT_DB.exists():
        return {
            "status": "PASS",
            "message": "Incident database exists.",
        }

    return {
        "status": "FAIL",
        "message": "Incident database is missing.",
    }


def check_environment():
    environment = os.getenv(
        "FINAGENT_ENVIRONMENT",
        "development",
    )

    return {
        "status": "PASS",
        "environment": environment,
    }


def run_security_health_check():
    checks = {
        "jwt_secret": check_jwt_secret(),
        "audit_database": check_audit_database(),
        "incident_database": check_incident_database(),
        "environment": check_environment(),
        "dependencies": check_dependencies(),
    }

    failed_checks = [
        name
        for name, result in checks.items()
        if result["status"] == "FAIL"
    ]

    overall_status = (
        "FAIL"
        if failed_checks
        else "PASS"
    )

    return {
        "overall_status": overall_status,
        "checks": checks,
        "failed_checks": failed_checks,
    }