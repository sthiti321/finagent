import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from api.security.incident_response import (
    create_incident,
    determine_incident_severity,
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent

LOG_DIR = BASE_DIR / "data" / "security" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "security.log"


security_logger = logging.getLogger("finagent.security")
security_logger.setLevel(logging.INFO)


if not security_logger.handlers:
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler.setFormatter(formatter)
    security_logger.addHandler(file_handler)


incident_events = {
    "LOGIN_FAILED",
    "UNAUTHORIZED_ACCESS",
    "FORBIDDEN_ACCESS",
    "RATE_LIMIT_EXCEEDED",
    "IP_BLOCKED",
}


def log_security_event(
    event: str,
    level: str,
    message: str,
    source_ip: str = None,
) -> None:
    """Log and record a security event if it matches monitored incidents."""

    log_message = f"EVENT={event} | {message}"

    if level.upper() == "WARNING":
        security_logger.warning(log_message)

    elif level.upper() == "ERROR":
        security_logger.error(log_message)

    else:
        security_logger.info(log_message)

    if event in incident_events:

        severity = determine_incident_severity(
            event_type=event,
            source_ip=source_ip,
        )

        create_incident(
            event_type=event,
            severity=severity,
            description=message,
            source_ip=source_ip,
        )