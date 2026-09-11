# ============================================================
# FINAGENT CONFIGURATION SECURITY
# C4 — INFRASTRUCTURE SECURITY
# ============================================================

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


ENVIRONMENT = os.getenv(
    "FINAGENT_ENVIRONMENT",
    "development"
).lower()


IS_PRODUCTION = ENVIRONMENT == "production"


def validate_security_config():
    """
    Validate security-sensitive configuration before startup.
    """

    errors = []

    jwt_secret = os.getenv("FINAGENT_JWT_SECRET", "")

    if not jwt_secret:
        errors.append(
            "FINAGENT_JWT_SECRET is not configured."
        )

    if IS_PRODUCTION:

        if len(jwt_secret) < 64:
            errors.append(
                "Production JWT secret must contain at least 64 characters."
            )

        if os.getenv(
            "FINAGENT_ALLOW_DOCS",
            "false"
        ).lower() == "true":
            errors.append(
                "Swagger/ReDoc must not be enabled in production."
            )

        if os.getenv(
            "FINAGENT_HTTPS_ONLY",
            "true"
        ).lower() != "true":
            errors.append(
                "HTTPS-only mode must be enabled in production."
            )

    if errors:
        raise RuntimeError(
            "Security configuration error:\n- "
            + "\n- ".join(errors)
        )


def security_config():
    """
    Return security configuration used by the application.
    """

    return {
        "environment": ENVIRONMENT,
        "production": IS_PRODUCTION,
        "docs_enabled": (
            os.getenv(
                "FINAGENT_ALLOW_DOCS",
                "true"
            ).lower() == "true"
        ),
        "https_only": (
            os.getenv(
                "FINAGENT_HTTPS_ONLY",
                "false"
            ).lower() == "true"
        ),
    }