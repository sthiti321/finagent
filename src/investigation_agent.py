import os
import re
import pandas as pd
import psycopg

from sentence_transformers import SentenceTransformer
from pgvector.psycopg import register_vector

from api.security.ai_security import (
    validate_customer_id,
    validate_rag_query,
    validate_top_k,
    validate_retrieved_content,
)

from functools import lru_cache


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(BASE_DIR, "data")

CUSTOMERS_FILE = os.path.join(
    DATA_DIR, "customers", "customers.csv"
)

ACCOUNTS_FILE = os.path.join(
    DATA_DIR, "accounts", "accounts.csv"
)

TRANSACTIONS_FILE = os.path.join(
    DATA_DIR, "transactions", "transactions.csv"
)

BEHAVIOR_FILE = os.path.join(
    DATA_DIR, "transactions",
    "customer_behavior_profiles.csv"
)

RISK_FILE = os.path.join(
    DATA_DIR, "transactions",
    "risk_results.csv"
)

ANOMALY_FILE = os.path.join(
    DATA_DIR, "transactions",
    "anomaly_detection_results.csv"
)

NETWORK_PATTERN_FILE = os.path.join(
    DATA_DIR, "transactions",
    "aml_network_pattern_results.csv"
)


# ============================================================
# DATABASE
# ============================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://nfl@localhost:5432/finagent_rag"
)

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# ============================================================
# CACHED DATA LOADERS
# ============================================================

@lru_cache(maxsize=1)
def load_customers_data():
    """
    Load customer data once and reuse it.
    """
    return pd.read_csv(
        CUSTOMERS_FILE
    )


@lru_cache(maxsize=1)
def load_accounts_data():
    """
    Load account data once and reuse it.
    """
    return pd.read_csv(
        ACCOUNTS_FILE
    )


@lru_cache(maxsize=1)
def load_transactions_data():
    """
    Load transaction data once and reuse it.
    """
    return pd.read_csv(
        TRANSACTIONS_FILE,
        parse_dates=["timestamp"]
    )


@lru_cache(maxsize=1)
def load_behavior_data():
    """
    Load customer behavior profiles once.
    """
    return pd.read_csv(
        BEHAVIOR_FILE
    )


@lru_cache(maxsize=1)
def load_risk_data():
    """
    Load fraud/risk results once.
    """
    return pd.read_csv(
        RISK_FILE
    )


@lru_cache(maxsize=1)
def load_anomaly_data():
    """
    Load anomaly results once.
    """
    return pd.read_csv(
        ANOMALY_FILE
    )


@lru_cache(maxsize=1)
def load_network_data():
    """
    Load network analysis results once.
    """
    return pd.read_csv(
        NETWORK_PATTERN_FILE
    )


# ============================================================
# LOAD EMBEDDING MODEL ONCE
# ============================================================

_embedding_model = None


def get_embedding_model():
    """
    Load the embedding model only once.

    This prevents SentenceTransformer from being
    reloaded every time search_policies() is called.
    """

    global _embedding_model

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(
            EMBEDDING_MODEL
        )

    return _embedding_model


# ============================================================
# CUSTOMER ID NORMALIZATION
# ============================================================

def normalize_customer_id(customer_id):

    if customer_id is None:
        return None

    customer_id = validate_customer_id(
        customer_id
    )

    value = str(
        customer_id
    ).strip().upper()

    # Extract trailing digits
    match = re.search(
        r"(\d+)$",
        value
    )

    if not match:
        return None

    return int(
        match.group(1)
    )


# ============================================================
# 1. CUSTOMER PROFILE
# ============================================================

def get_customer_profile(customer_id):

    customers = load_customers_data()

    result = customers[
        customers["customer_id"]
        .astype(str)
        .str.strip()
        == str(customer_id).strip()
    ]

    if result.empty:

        # Try normalized ID comparison
        target_number = normalize_customer_id(
            customer_id
        )

        if target_number is not None:

            normalized_ids = (
                customers["customer_id"]
                .apply(normalize_customer_id)
            )

            result = customers[
                normalized_ids == target_number
            ]

    if result.empty:
        return {
            "found": False,
            "message": (
                f"Customer {customer_id} "
                f"not found."
            )
        }

    customer = result.iloc[
        0
    ].to_dict()

    customer["found"] = True

    return customer


# ============================================================
# 2. TRANSACTIONS
# ============================================================

def get_transactions(
    customer_id,
    limit=20
):

    transactions = load_transactions_data()

    target_number = normalize_customer_id(
        customer_id
    )

    normalized_ids = (
        transactions["customer_id"]
        .apply(normalize_customer_id)
    )

    result = transactions[
        normalized_ids == target_number
    ].sort_values(
        "timestamp",
        ascending=False
    ).head(
        limit
    )

    if result.empty:
        return []

    return result.to_dict(
        "records"
    )


# ============================================================
# 3. TRANSACTION DETAILS
# ============================================================

def get_transaction_details(
    transaction_id
):

    transactions = load_transactions_data()

    result = transactions[
        transactions["transaction_id"]
        .astype(str)
        == str(transaction_id)
    ]

    if result.empty:
        return {
            "found": False,
            "message": (
                f"Transaction {transaction_id} "
                f"not found."
            )
        }

    transaction = result.iloc[
        0
    ].to_dict()

    transaction["found"] = True

    return transaction


# ============================================================
# 4. CUSTOMER BEHAVIOR PROFILE
# ============================================================

def get_behavior_profile(
    customer_id
):

    behavior = load_behavior_data()

    target_number = normalize_customer_id(
        customer_id
    )

    normalized_ids = (
        behavior["customer_id"]
        .apply(normalize_customer_id)
    )

    result = behavior[
        normalized_ids == target_number
    ]

    if result.empty:
        return {
            "found": False,
            "message": (
                f"No behavior profile found "
                f"for {customer_id}."
            )
        }

    profile = result.iloc[
        0
    ].to_dict()

    profile["found"] = True

    return profile
# ============================================================
# 5. FRAUD SCORE
# ============================================================

def calculate_fraud_score(
    customer_id
):

    transactions = load_transactions_data()

    risk = load_risk_data()

    target_number = normalize_customer_id(
        customer_id
    )

    transaction_ids = (
        transactions["customer_id"]
        .apply(normalize_customer_id)
    )

    customer_transactions = transactions[
        transaction_ids == target_number
    ].copy()

    if customer_transactions.empty:

        return {
            "customer_id": customer_id,
            "transaction_count": 0,
            "max_risk_score": 0.0,
            "average_risk_score": 0.0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0
        }

    required_columns = [
        "transaction_id",
        "risk_score",
        "risk_level"
    ]

    available_columns = [
        column
        for column in required_columns
        if column in risk.columns
    ]

    if len(available_columns) < 3:

        return {
            "customer_id": customer_id,
            "transaction_count": len(
                customer_transactions
            ),
            "max_risk_score": 0.0,
            "average_risk_score": 0.0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "error": (
                "Required columns missing from "
                "risk_results.csv"
            )
        }

    merged = customer_transactions.merge(
        risk[required_columns],
        on="transaction_id",
        how="left"
    )

    # Ensure risk score is numeric
    merged["risk_score"] = pd.to_numeric(
        merged["risk_score"],
        errors="coerce"
    ).fillna(
        0.0
    )

    # Normalize risk level
    merged["risk_level"] = (
        merged["risk_level"]
        .fillna("LOW")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    high_count = int(
        (
            merged["risk_level"]
            == "HIGH"
        ).sum()
    )

    medium_count = int(
        (
            merged["risk_level"]
            == "MEDIUM"
        ).sum()
    )

    low_count = int(
        (
            merged["risk_level"]
            == "LOW"
        ).sum()
    )

    return {
        "customer_id": customer_id,
        "transaction_count": int(
            len(merged)
        ),

        # Fraud/model score is retained
        # in its original 0-1 scale.
        "max_risk_score": float(
            merged["risk_score"].max()
        ),

        "average_risk_score": float(
            merged["risk_score"].mean()
        ),

        "high_risk_count": high_count,
        "medium_risk_count": medium_count,
        "low_risk_count": low_count
    }


# ============================================================
# 6. ANOMALY SCORE
# ============================================================

def calculate_anomaly_score(
    customer_id
):

    anomalies = load_anomaly_data()

    target_number = normalize_customer_id(
        customer_id
    )

    normalized_ids = (
        anomalies["customer_id"]
        .apply(normalize_customer_id)
    )

    result = anomalies[
        normalized_ids == target_number
    ].copy()

    if result.empty:

        return {
            "found": False,
            "message": (
                f"No anomaly data found "
                f"for {customer_id}."
            )
        }

    # Ensure anomaly score is numeric
    result["anomaly_score"] = pd.to_numeric(
        result["anomaly_score"],
        errors="coerce"
    ).fillna(
        0.0
    )

    # Safely convert anomaly flag
    if result["is_anomaly"].dtype == object:

        anomaly_values = (
            result["is_anomaly"]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin([
                "true",
                "1",
                "yes",
                "y",
                "anomaly"
            ])
        )

    else:

        anomaly_values = (
            pd.to_numeric(
                result["is_anomaly"],
                errors="coerce"
            )
            .fillna(0)
            .astype(int)
            .astype(bool)
        )

    return {
        "found": True,
        "customer_id": customer_id,

        "transaction_count": int(
            len(result)
        ),

        "maximum_anomaly_score": float(
            result[
                "anomaly_score"
            ].max()
        ),

        "average_anomaly_score": float(
            result[
                "anomaly_score"
            ].mean()
        ),

        "anomalous_transactions": int(
            anomaly_values.sum()
        )
    }


# ============================================================
# 7. NETWORK ANALYSIS
# ============================================================

def analyze_network(
    customer_id
):

    network = load_network_data()

    if "customer_id" not in network.columns:

        return {
            "found": False,
            "message": (
                "customer_id column missing "
                "from network results."
            )
        }

    target_number = normalize_customer_id(
        customer_id
    )

    # Work on a copy so the cached
    # dataframe itself is never modified.
    network_view = network.copy()

    network_view[
        "normalized_customer_id"
    ] = (
        network_view["customer_id"]
        .apply(normalize_customer_id)
    )

    result = network_view[
        network_view[
            "normalized_customer_id"
        ]
        == target_number
    ]

    if result.empty:

        return {
            "found": False,
            "message": (
                f"No network analysis found "
                f"for {customer_id}."
            )
        }

    row = result.iloc[
        0
    ]

    def safe_int(column):

        value = row.get(
            column,
            0
        )

        try:
            return int(
                float(value)
            )

        except (
            TypeError,
            ValueError
        ):
            return 0

    def safe_float(column):

        value = row.get(
            column,
            0.0
        )

        try:
            return float(
                value
            )

        except (
            TypeError,
            ValueError
        ):
            return 0.0

    return {
        "found": True,
        "customer_id": customer_id,

        "account_count": safe_int(
            "account_count"
        ),

        "transaction_count": safe_int(
            "transaction_count"
        ),

        "merchant_count": safe_int(
            "merchant_count"
        ),

        "device_count": safe_int(
            "device_count"
        ),

        "shared_device_count": safe_int(
            "shared_device_count"
        ),

        "network_risk_score": safe_float(
            "network_risk_score"
        ),

        "network_risk_level": str(
            row.get(
                "network_risk_level",
                "UNKNOWN"
            )
        ).upper()
    }


# ============================================================
# 8. RELATED ACCOUNTS
# ============================================================

def get_related_accounts(
    customer_id
):

    accounts = load_accounts_data()

    transactions = load_transactions_data()

    target_number = normalize_customer_id(
        customer_id
    )

    # Find customer's accounts
    account_customer_ids = (
        accounts["customer_id"]
        .apply(normalize_customer_id)
    )

    customer_accounts = accounts[
        account_customer_ids == target_number
    ]

    if customer_accounts.empty:
        return []

    account_ids = set(
        customer_accounts["account_id"]
        .dropna()
        .astype(str)
    )

    # Transactions involving customer's accounts
    transaction_account_ids = (
        transactions["account_id"]
        .fillna("")
        .astype(str)
    )

    related = transactions[
        transaction_account_ids.isin(
            account_ids
        )
    ]

    if related.empty:
        return []

    # Destination accounts
    destination_accounts = (
        related[
            related[
                "destination_account_id"
            ].notna()
        ][
            "destination_account_id"
        ]
        .astype(str)
        .unique()
    )

    if len(destination_accounts) == 0:
        return []

    result = accounts[
        accounts["account_id"]
        .astype(str)
        .isin(
            destination_accounts
        )
    ]

    return result.to_dict(
        "records"
    )


# ============================================================
# 9. POLICY SEARCH / RAG
# ============================================================

def search_policies(
    query,
    top_k=3
):

    query = validate_rag_query(
        query
    )

    top_k = validate_top_k(
        top_k
    )

    model = get_embedding_model()

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    )

    conn = None

    try:

        conn = psycopg.connect(
            DATABASE_URL
        )

        register_vector(
            conn
        )

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    content,
                    1 - (embedding <=> %s::vector)
                        AS similarity
                FROM document_chunks
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """,
                (
                    query_embedding.tolist(),
                    query_embedding.tolist(),
                    int(top_k)
                )
            )

            results = cur.fetchall()

        return [
            {
                "chunk_id": row[0],
                "document_id": row[1],
                "content": validate_retrieved_content(
                    row[2]
                ),
                "similarity": float(
                    row[3]
                )
            }
            for row in results
        ]

    except Exception as e:

        return [
            {
                "error": (
                    f"Policy search failed: "
                    f"{str(e)}"
                )
            }
        ]

    finally:

        if conn is not None:
            conn.close()

            # ============================================================
# 5. FRAUD SCORE
# ============================================================

def calculate_fraud_score(
    customer_id
):

    transactions = load_transactions_data()

    risk = load_risk_data()

    target_number = normalize_customer_id(
        customer_id
    )

    transaction_ids = (
        transactions["customer_id"]
        .apply(normalize_customer_id)
    )

    customer_transactions = transactions[
        transaction_ids == target_number
    ].copy()

    if customer_transactions.empty:

        return {
            "customer_id": customer_id,
            "transaction_count": 0,
            "max_risk_score": 0.0,
            "average_risk_score": 0.0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0
        }

    required_columns = [
        "transaction_id",
        "risk_score",
        "risk_level"
    ]

    available_columns = [
        column
        for column in required_columns
        if column in risk.columns
    ]

    if len(available_columns) < 3:

        return {
            "customer_id": customer_id,
            "transaction_count": len(
                customer_transactions
            ),
            "max_risk_score": 0.0,
            "average_risk_score": 0.0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "error": (
                "Required columns missing from "
                "risk_results.csv"
            )
        }

    merged = customer_transactions.merge(
        risk[required_columns],
        on="transaction_id",
        how="left"
    )

    # Ensure risk score is numeric
    merged["risk_score"] = pd.to_numeric(
        merged["risk_score"],
        errors="coerce"
    ).fillna(
        0.0
    )

    # Normalize risk level
    merged["risk_level"] = (
        merged["risk_level"]
        .fillna("LOW")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    high_count = int(
        (
            merged["risk_level"]
            == "HIGH"
        ).sum()
    )

    medium_count = int(
        (
            merged["risk_level"]
            == "MEDIUM"
        ).sum()
    )

    low_count = int(
        (
            merged["risk_level"]
            == "LOW"
        ).sum()
    )

    return {
        "customer_id": customer_id,
        "transaction_count": int(
            len(merged)
        ),

        # Fraud/model score is retained
        # in its original 0-1 scale.
        "max_risk_score": float(
            merged["risk_score"].max()
        ),

        "average_risk_score": float(
            merged["risk_score"].mean()
        ),

        "high_risk_count": high_count,
        "medium_risk_count": medium_count,
        "low_risk_count": low_count
    }


# ============================================================
# 6. ANOMALY SCORE
# ============================================================

def calculate_anomaly_score(
    customer_id
):

    anomalies = load_anomaly_data()

    target_number = normalize_customer_id(
        customer_id
    )

    normalized_ids = (
        anomalies["customer_id"]
        .apply(normalize_customer_id)
    )

    result = anomalies[
        normalized_ids == target_number
    ].copy()

    if result.empty:

        return {
            "found": False,
            "message": (
                f"No anomaly data found "
                f"for {customer_id}."
            )
        }

    # Ensure anomaly score is numeric
    result["anomaly_score"] = pd.to_numeric(
        result["anomaly_score"],
        errors="coerce"
    ).fillna(
        0.0
    )

    # Safely convert anomaly flag
    if result["is_anomaly"].dtype == object:

        anomaly_values = (
            result["is_anomaly"]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin([
                "true",
                "1",
                "yes",
                "y",
                "anomaly"
            ])
        )

    else:

        anomaly_values = (
            pd.to_numeric(
                result["is_anomaly"],
                errors="coerce"
            )
            .fillna(0)
            .astype(int)
            .astype(bool)
        )

    return {
        "found": True,
        "customer_id": customer_id,

        "transaction_count": int(
            len(result)
        ),

        "maximum_anomaly_score": float(
            result[
                "anomaly_score"
            ].max()
        ),

        "average_anomaly_score": float(
            result[
                "anomaly_score"
            ].mean()
        ),

        "anomalous_transactions": int(
            anomaly_values.sum()
        )
    }


# ============================================================
# 7. NETWORK ANALYSIS
# ============================================================

def analyze_network(
    customer_id
):

    network = load_network_data()

    if "customer_id" not in network.columns:

        return {
            "found": False,
            "message": (
                "customer_id column missing "
                "from network results."
            )
        }

    target_number = normalize_customer_id(
        customer_id
    )

    # Work on a copy so the cached
    # dataframe itself is never modified.
    network_view = network.copy()

    network_view[
        "normalized_customer_id"
    ] = (
        network_view["customer_id"]
        .apply(normalize_customer_id)
    )

    result = network_view[
        network_view[
            "normalized_customer_id"
        ]
        == target_number
    ]

    if result.empty:

        return {
            "found": False,
            "message": (
                f"No network analysis found "
                f"for {customer_id}."
            )
        }

    row = result.iloc[
        0
    ]

    def safe_int(column):

        value = row.get(
            column,
            0
        )

        try:
            return int(
                float(value)
            )

        except (
            TypeError,
            ValueError
        ):
            return 0

    def safe_float(column):

        value = row.get(
            column,
            0.0
        )

        try:
            return float(
                value
            )

        except (
            TypeError,
            ValueError
        ):
            return 0.0

    return {
        "found": True,
        "customer_id": customer_id,

        "account_count": safe_int(
            "account_count"
        ),

        "transaction_count": safe_int(
            "transaction_count"
        ),

        "merchant_count": safe_int(
            "merchant_count"
        ),

        "device_count": safe_int(
            "device_count"
        ),

        "shared_device_count": safe_int(
            "shared_device_count"
        ),

        "network_risk_score": safe_float(
            "network_risk_score"
        ),

        "network_risk_level": str(
            row.get(
                "network_risk_level",
                "UNKNOWN"
            )
        ).upper()
    }


# ============================================================
# 8. RELATED ACCOUNTS
# ============================================================

def get_related_accounts(
    customer_id
):

    accounts = load_accounts_data()

    transactions = load_transactions_data()

    target_number = normalize_customer_id(
        customer_id
    )

    # Find customer's accounts
    account_customer_ids = (
        accounts["customer_id"]
        .apply(normalize_customer_id)
    )

    customer_accounts = accounts[
        account_customer_ids == target_number
    ]

    if customer_accounts.empty:
        return []

    account_ids = set(
        customer_accounts["account_id"]
        .dropna()
        .astype(str)
    )

    # Transactions involving customer's accounts
    transaction_account_ids = (
        transactions["account_id"]
        .fillna("")
        .astype(str)
    )

    related = transactions[
        transaction_account_ids.isin(
            account_ids
        )
    ]

    if related.empty:
        return []

    # Destination accounts
    destination_accounts = (
        related[
            related[
                "destination_account_id"
            ].notna()
        ][
            "destination_account_id"
        ]
        .astype(str)
        .unique()
    )

    if len(destination_accounts) == 0:
        return []

    result = accounts[
        accounts["account_id"]
        .astype(str)
        .isin(
            destination_accounts
        )
    ]

    return result.to_dict(
        "records"
    )


# ============================================================
# 9. POLICY SEARCH / RAG
# ============================================================

def search_policies(
    query,
    top_k=3
):

    query = validate_rag_query(
        query
    )

    top_k = validate_top_k(
        top_k
    )

    model = get_embedding_model()

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    )

    conn = None

    try:

        conn = psycopg.connect(
            DATABASE_URL
        )

        register_vector(
            conn
        )

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    content,
                    1 - (embedding <=> %s::vector)
                        AS similarity
                FROM document_chunks
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """,
                (
                    query_embedding.tolist(),
                    query_embedding.tolist(),
                    int(top_k)
                )
            )

            results = cur.fetchall()

        return [
            {
                "chunk_id": row[0],
                "document_id": row[1],
                "content": validate_retrieved_content(
                    row[2]
                ),
                "similarity": float(
                    row[3]
                )
            }
            for row in results
        ]

    except Exception as e:

        return [
            {
                "error": (
                    f"Policy search failed: "
                    f"{str(e)}"
                )
            }
        ]

    finally:

        if conn is not None:
            conn.close()