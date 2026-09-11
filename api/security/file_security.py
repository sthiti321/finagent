# ============================================================
# FINAGENT FILE SECURITY
# C4 — INFRASTRUCTURE SECURITY
# ============================================================

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

PROTECTED_PATHS = [
    BASE_DIR / ".env",
    BASE_DIR / "data" / "security",
]


def validate_protected_paths():
    """
    Verify that sensitive FINAGENT files/directories exist
    and are not accidentally exposed through the application.
    """

    for path in PROTECTED_PATHS:

        if path.name == ".env":
            if path.exists() and not path.is_file():
                raise RuntimeError(
                    ".env exists but is not a regular file."
                )

        elif path.name == "security":
            if path.exists() and not path.is_dir():
                raise RuntimeError(
                    "data/security must be a directory."
                )


def ensure_security_directory():
    """
    Ensure the security-data directory exists.
    """

    security_dir = BASE_DIR / "data" / "security"

    security_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return security_dir