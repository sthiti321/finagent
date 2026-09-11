# ============================================================
# FINAGENT AI / ML SECURITY
# C5 — AI/ML SECURITY
# ============================================================

import math
import logging
import re


logger = logging.getLogger("finagent.ai_security")


# ------------------------------------------------------------
# LIMITS
# ------------------------------------------------------------

MAX_CUSTOMER_ID_LENGTH = 50
MAX_RAG_QUERY_LENGTH = 500
MAX_RAG_TOP_K = 10


# ------------------------------------------------------------
# SUSPICIOUS RAG / PROMPT-INJECTION PATTERNS
# ------------------------------------------------------------

SUSPICIOUS_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?prior\s+instructions",
    r"disregard\s+(all\s+)?previous\s+instructions",
    r"forget\s+(all\s+)?previous\s+instructions",
    r"system\s+prompt",
    r"developer\s+message",
    r"reveal\s+(your\s+)?instructions",
    r"show\s+(your\s+)?prompt",
    r"override\s+(the\s+)?instructions",
    r"act\s+as\s+(an?\s+)?admin",
    r"you\s+are\s+now\s+",
]


# ------------------------------------------------------------
# CUSTOMER ID VALIDATION
# ------------------------------------------------------------

def validate_customer_id(customer_id: str) -> str:

    if customer_id is None:
        raise ValueError("Customer ID is required.")

    value = str(customer_id).strip()

    if not value:
        raise ValueError("Customer ID cannot be empty.")

    if len(value) > MAX_CUSTOMER_ID_LENGTH:
        raise ValueError("Customer ID is too long.")

    # FINAGENT currently supports IDs such as:
    # CUST00001
    # C00001
    # cust00804
    # 804

    if not re.fullmatch(
        r"[A-Za-z0-9_-]+",
        value
    ):
        raise ValueError(
            "Customer ID contains invalid characters."
        )

    return value


# ------------------------------------------------------------
# RAG QUERY VALIDATION
# ------------------------------------------------------------

def validate_rag_query(query: str) -> str:

    if query is None:
        raise ValueError("Policy search query is required.")

    value = str(query).strip()

    if not value:
        raise ValueError(
            "Policy search query cannot be empty."
        )

    if len(value) > MAX_RAG_QUERY_LENGTH:
        raise ValueError(
            "Policy search query is too long."
        )

    return value


# ------------------------------------------------------------
# TOP-K VALIDATION
# ------------------------------------------------------------

def validate_top_k(top_k: int) -> int:

    try:
        top_k = int(top_k)
    except (TypeError, ValueError):

        raise ValueError(
            "top_k must be an integer."
        )

    if top_k < 1:
        raise ValueError(
            "top_k must be at least 1."
        )

    if top_k > MAX_RAG_TOP_K:
        raise ValueError(
            f"top_k cannot exceed {MAX_RAG_TOP_K}."
        )

    return top_k


# ------------------------------------------------------------
# PROMPT-INJECTION DETECTION
# ------------------------------------------------------------

def contains_suspicious_instruction(text: str) -> bool:

    if not text:
        return False

    text = str(text).lower()

    for pattern in SUSPICIOUS_PATTERNS:

        if re.search(pattern, text):
            return True

    return False


# ------------------------------------------------------------
# RAG CONTENT SANITIZATION
# ------------------------------------------------------------

def validate_retrieved_content(content: str) -> str:

    if content is None:
        return ""

    content = str(content)

    if contains_suspicious_instruction(content):

        logger.warning(
            "Suspicious instruction detected in retrieved "
            "RAG content."
        )

        return (
            "[UNTRUSTED POLICY CONTENT — "
            "INSTRUCTION-LIKE TEXT DETECTED]\n"
            + content
        )

    return content


# ------------------------------------------------------------
# NUMERIC MODEL OUTPUT VALIDATION
# ------------------------------------------------------------

def validate_score(
    value,
    minimum: float = 0.0,
    maximum: float = 100.0
) -> float:

    try:
        value = float(value)
    except (TypeError, ValueError):

        raise ValueError(
            "Model score must be numeric."
        )

    if not math.isfinite(value):

        raise ValueError(
            "Model score must be finite."
        )

    if value < minimum:
        logger.warning(
            "Model score below allowed range: %s",
            value
        )

        value = minimum

    if value > maximum:
        logger.warning(
            "Model score above allowed range: %s",
            value
        )

        value = maximum

    return value