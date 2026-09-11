from datetime import datetime
from functools import lru_cache

from investigation_agent import (
    get_customer_profile,
    get_transactions,
    get_behavior_profile,
    calculate_fraud_score,
    calculate_anomaly_score,
    analyze_network,
    get_related_accounts,
    search_policies,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_fraud_severity(score):
    """
    Convert fraud model score into a severity level.

    Assumes the fraud model returns a score between 0 and 1.
    """

    score = float(score or 0)

    if score >= 0.70:
        return "HIGH"

    elif score >= 0.30:
        return "MEDIUM"

    else:
        return "LOW"


def get_transaction_severity(suspicious_count):
    """
    Determine transaction activity severity.
    """

    suspicious_count = int(suspicious_count or 0)

    if suspicious_count >= 3:
        return "HIGH"

    elif suspicious_count > 0:
        return "MEDIUM"

    return "LOW"


def get_anomaly_severity(anomaly_count, max_score):
    """
    Determine anomaly detection severity.
    """

    anomaly_count = int(anomaly_count or 0)
    max_score = float(max_score or 0)

    if anomaly_count >= 10 or max_score >= 0.70:
        return "HIGH"

    elif anomaly_count > 0 or max_score >= 0.30:
        return "MEDIUM"

    return "LOW"


def get_related_account_severity(account_count):
    """
    Determine severity based on number of related accounts.
    """

    account_count = int(account_count or 0)

    if account_count >= 10:
        return "HIGH"

    elif account_count >= 3:
        return "MEDIUM"

    return "LOW"


# ============================================================
# EVIDENCE AGENT
# ============================================================

@lru_cache(maxsize=256)
def build_evidence(customer_id):

    evidence = []

    # ========================================================
    # 1. CUSTOMER PROFILE
    # ========================================================

    profile = get_customer_profile(customer_id)

    if profile:

        evidence.append({
            "evidence_type": "CUSTOMER_PROFILE",
            "severity": "INFO",
            "source": "customer_data",
            "finding": (
                f"Customer {customer_id} profile retrieved. "
                f"Name: {profile.get('name', 'Unknown')}, "
                f"Age: {profile.get('age', 'Unknown')}, "
                f"Gender: {profile.get('gender', 'Unknown')}, "
                f"Occupation: {profile.get('occupation', 'Unknown')}, "
                f"City: {profile.get('city', 'Unknown')}, "
                f"Income: {profile.get('income', 'Unknown')}, "
                f"Customer since: "
                f"{profile.get('customer_since', 'Unknown')}."
            ),
            "data": profile
        })

    else:

        evidence.append({
            "evidence_type": "CUSTOMER_PROFILE",
            "severity": "INFO",
            "source": "customer_data",
            "finding": (
                f"No customer profile found for "
                f"{customer_id}."
            ),
            "data": {
                "customer_id": customer_id,
                "found": False
            }
        })

    # ========================================================
    # 2. TRANSACTION ACTIVITY
    # ========================================================

    transactions = get_transactions(
        customer_id,
        limit=20
    )

    if transactions:

        suspicious_count = sum(
            1
            for transaction in transactions
            if transaction.get("is_suspicious") == 1
        )

        severity = get_transaction_severity(
            suspicious_count
        )

        evidence.append({
            "evidence_type": "TRANSACTION_ACTIVITY",
            "severity": severity,
            "source": "transaction_data",
            "finding": (
                f"{len(transactions)} recent transactions "
                f"reviewed. "
                f"{suspicious_count} were marked suspicious."
            ),
            "data": {
                "transaction_count": len(transactions),
                "suspicious_transaction_count": suspicious_count
            }
        })

    else:

        evidence.append({
            "evidence_type": "TRANSACTION_ACTIVITY",
            "severity": "INFO",
            "source": "transaction_data",
            "finding": (
                f"No recent transactions found for "
                f"customer {customer_id}."
            ),
            "data": {
                "transaction_count": 0,
                "suspicious_transaction_count": 0
            }
        })

    # ========================================================
    # 3. CUSTOMER BEHAVIOR
    # ========================================================

    behavior = get_behavior_profile(
        customer_id
    )

    if behavior:

        average_amount = float(
            behavior.get("average_amount", 0)
        )

        median_amount = float(
            behavior.get("median_amount", 0)
        )

        transaction_frequency = behavior.get(
            "transaction_frequency",
            0
        )

        typical_merchant = behavior.get(
            "typical_merchant",
            "Unknown"
        )

        typical_location = behavior.get(
            "typical_location",
            "Unknown"
        )

        typical_device = behavior.get(
            "typical_device",
            "Unknown"
        )

        typical_hour = behavior.get(
            "typical_hour",
            "Unknown"
        )

        evidence.append({
            "evidence_type": "CUSTOMER_BEHAVIOR",
            "severity": "MEDIUM",
            "source": "behavior_analysis",
            "finding": (
                f"Average transaction amount: "
                f"{average_amount:.2f}. "
                f"Median transaction amount: "
                f"{median_amount:.2f}. "
                f"Transaction frequency: "
                f"{transaction_frequency}. "
                f"Typical merchant: "
                f"{typical_merchant}. "
                f"Typical location: "
                f"{typical_location}. "
                f"Typical device: "
                f"{typical_device}. "
                f"Typical transaction hour: "
                f"{typical_hour}."
            ),
            "data": behavior
        })

    # ========================================================
    # 4. FRAUD MODEL RISK
    # ========================================================

    fraud = calculate_fraud_score(
        customer_id
    )

    if fraud:

        max_risk_score = float(
            fraud.get("max_risk_score", 0)
        )

        average_risk_score = float(
            fraud.get("average_risk_score", 0)
        )

        high_risk_count = fraud.get(
            "high_risk_count",
            0
        )

        medium_risk_count = fraud.get(
            "medium_risk_count",
            0
        )

        low_risk_count = fraud.get(
            "low_risk_count",
            0
        )

        severity = get_fraud_severity(
            max_risk_score
        )

        evidence.append({
            "evidence_type": "MODEL_RISK",
            "severity": severity,
            "source": "fraud_model",
            "finding": (
                f"Maximum model risk score: "
                f"{max_risk_score:.6f}. "
                f"Average model risk score: "
                f"{average_risk_score:.6f}. "
                f"High-risk transactions: "
                f"{high_risk_count}. "
                f"Medium-risk transactions: "
                f"{medium_risk_count}. "
                f"Low-risk transactions: "
                f"{low_risk_count}."
            ),
            "data": fraud
        })

    # ========================================================
    # 5. ANOMALY DETECTION
    # ========================================================

    anomaly = calculate_anomaly_score(
        customer_id
    )

    if anomaly:

        anomaly_count = int(
            anomaly.get(
                "anomalous_transactions",
                0
            )
        )

        max_anomaly_score = float(
            anomaly.get(
                "maximum_anomaly_score",
                0
            )
        )

        average_anomaly_score = float(
            anomaly.get(
                "average_anomaly_score",
                0
            )
        )

        severity = get_anomaly_severity(
            anomaly_count,
            max_anomaly_score
        )

        evidence.append({
            "evidence_type": "ANOMALY_DETECTION",
            "severity": severity,
            "source": "anomaly_detection",
            "finding": (
                f"{anomaly_count} anomalous transactions "
                f"detected. "
                f"Maximum anomaly score: "
                f"{max_anomaly_score:.4f}. "
                f"Average anomaly score: "
                f"{average_anomaly_score:.4f}."
            ),
            "data": anomaly
        })

    # ========================================================
    # 6. NETWORK RISK
    # ========================================================

    network = analyze_network(
        customer_id
    )

    if network:

        network_score = float(
            network.get(
                "network_risk_score",
                0
            )
        )

        network_level = str(
            network.get(
                "network_risk_level",
                "LOW"
            )
        ).upper()

        account_count = network.get(
            "account_count",
            0
        )

        transaction_count = network.get(
            "transaction_count",
            0
        )

        merchant_count = network.get(
            "merchant_count",
            0
        )

        device_count = network.get(
            "device_count",
            0
        )

        shared_device_count = network.get(
            "shared_device_count",
            0
        )

        evidence.append({
            "evidence_type": "NETWORK_RISK",
            "severity": network_level,
            "source": "network_analysis",
            "finding": (
                f"Network risk level: "
                f"{network_level}. "
                f"Network risk score: "
                f"{network_score:.2f}. "
                f"Accounts: {account_count}. "
                f"Transactions: {transaction_count}. "
                f"Merchants: {merchant_count}. "
                f"Devices: {device_count}. "
                f"Shared devices: "
                f"{shared_device_count}."
            ),
            "data": network
        })

    # ========================================================
    # 7. RELATED ACCOUNTS
    # ========================================================

    related_accounts = get_related_accounts(
        customer_id
    )

    if related_accounts is None:
        related_accounts = []

    related_count = len(
        related_accounts
    )

    severity = get_related_account_severity(
        related_count
    )

    evidence.append({
        "evidence_type": "RELATED_ACCOUNTS",
        "severity": severity,
        "source": "account_relationships",
        "finding": (
            f"{related_count} related accounts "
            f"identified from transaction activity."
        ),
        "data": related_accounts
    })

    # ========================================================
    # 8. POLICY CONTEXT / RAG
    # ========================================================

    policy_query = """
    AML investigation suspicious transactions
    customer risk network relationships escalation
    transaction monitoring unusual behavior
    related accounts fund flows coordinated activity
    """

    policy_results = search_policies(
        policy_query
    )

    if policy_results:

        evidence.append({
            "evidence_type": "POLICY_CONTEXT",
            "severity": "INFO",
            "source": "policy_knowledge_base",
            "finding": (
                f"{len(policy_results)} relevant AML/KYC "
                f"policy sections retrieved."
            ),
            "data": policy_results
        })

    # ========================================================
    # RETURN EVIDENCE PACKAGE
    # ========================================================

    return {
        "customer_id": customer_id,
        "generated_at": datetime.now().isoformat(),
        "evidence_count": len(evidence),
        "evidence": evidence
    }


# ============================================================
# PRINT EVIDENCE REPORT
# ============================================================

def print_evidence_report(evidence_package):

    print("\n" + "=" * 70)
    print("FINAGENT - EVIDENCE AGENT")
    print("=" * 70)

    print(
        f"\nCustomer: "
        f"{evidence_package['customer_id']}"
    )

    print(
        f"Evidence items: "
        f"{evidence_package['evidence_count']}"
    )

    print("\nEvidence Findings:")
    print("-" * 70)

    for index, item in enumerate(
        evidence_package["evidence"],
        start=1
    ):

        print(
            f"\n[{index}] "
            f"{item['evidence_type']}"
        )

        print(
            f"Severity : "
            f"{item['severity']}"
        )

        print(
            f"Source   : "
            f"{item['source']}"
        )

        print(
            f"Finding  : "
            f"{item['finding']}"
        )

    print("\n" + "=" * 70)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    customer_id = "CUST00804"

    evidence_package = build_evidence(
        customer_id
    )

    print_evidence_report(
        evidence_package
    )