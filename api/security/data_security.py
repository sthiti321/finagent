# ============================================================
# FINAGENT DATA SECURITY
# C2 — DATA SECURITY & PRIVACY
# ============================================================

from typing import Any


# ============================================================
# SENSITIVE FIELD DEFINITIONS
# ============================================================

# Fields that should normally never be exposed completely
FULLY_MASKED_FIELDS = {
    "password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "api_key",
    "jwt",
}

# Financial / PII fields where keeping the last few characters
# is useful for investigation while reducing exposure.
PARTIALLY_MASKED_FIELDS = {
    "account_number": 4,
    "account_no": 4,
    "bank_account": 4,
    "card_number": 4,
    "credit_card": 4,
    "debit_card": 4,
    "aadhaar": 4,
    "aadhaar_number": 4,
    "pan": 4,
    "tax_id": 4,
    "phone": 4,
    "mobile": 4,
}


# ============================================================
# MASKING FUNCTIONS
# ============================================================

def mask_value(
    value: Any,
    visible_characters: int = 4
) -> Any:
    """
    Mask a sensitive value while retaining a small suffix
    useful for identification during investigations.
    """

    if value is None:
        return None

    value = str(value)

    if not value:
        return value

    # If the value is already very short, mask it completely.
    if len(value) <= visible_characters:
        return "*" * len(value)

    return (
        "*" * (len(value) - visible_characters)
        + value[-visible_characters:]
    )


def mask_sensitive_value(
    key: str,
    value: Any
) -> Any:
    """
    Apply the correct masking policy based on the field name.
    """

    normalized_key = key.lower().strip()

    # Completely hide secrets.
    if normalized_key in FULLY_MASKED_FIELDS:
        return "********"

    # Partially hide PII / financial identifiers.
    if normalized_key in PARTIALLY_MASKED_FIELDS:
        visible = PARTIALLY_MASKED_FIELDS[normalized_key]
        return mask_value(
            value,
            visible_characters=visible
        )

    return value


# ============================================================
# RECURSIVE DATA MASKING
# ============================================================

def mask_sensitive_data(data: Any) -> Any:
    """
    Recursively mask sensitive information in dictionaries,
    lists, tuples and other JSON-like structures.

    This allows FINAGENT to protect data returned by existing
    investigation modules without changing their internal logic.
    """

    if isinstance(data, dict):

        masked = {}

        for key, value in data.items():

            if isinstance(key, str):

                masked[key] = mask_sensitive_value(
                    key,
                    mask_sensitive_data(value)
                )

            else:

                masked[key] = mask_sensitive_data(value)

        return masked

    if isinstance(data, list):

        return [
            mask_sensitive_data(item)
            for item in data
        ]

    if isinstance(data, tuple):

        return tuple(
            mask_sensitive_data(item)
            for item in data
        )

    return data


# ============================================================
# SECURITY-SAFE RESPONSE HELPER
# ============================================================

def secure_response(data: Any) -> Any:
    """
    Public helper used by API endpoints before returning
    customer, transaction, evidence or other sensitive data.
    """

    return mask_sensitive_data(data)