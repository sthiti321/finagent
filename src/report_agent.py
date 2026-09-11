from datetime import datetime
from functools import lru_cache
import psycopg

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

from risk_engine import calculate_final_risk


DATABASE_URL = "postgresql://nfl@localhost:5432/finagent_rag"


@lru_cache(maxsize=256)
def generate_report(customer_id):

    # ---------------------------------------------------------
    # Collect investigation evidence
    # ---------------------------------------------------------

    profile = get_customer_profile(customer_id)
    transactions = get_transactions(customer_id, limit=20)
    behavior = get_behavior_profile(customer_id)
    fraud = calculate_fraud_score(customer_id)
    anomaly = calculate_anomaly_score(customer_id)
    network = analyze_network(customer_id)
    related = get_related_accounts(customer_id)

    policies = search_policies(
        "AML investigation suspicious transactions customer risk escalation",
        top_k=3,
    )

    risk = calculate_final_risk(customer_id)

    # ---------------------------------------------------------
    # Case information
    # ---------------------------------------------------------

    account_id = "N/A"

    if transactions:
        account_id = transactions[0].get("account_id", "N/A")

    case_id = f"CASE-{customer_id}"

    investigation_date = datetime.now().strftime("%Y-%m-%d")

    # ---------------------------------------------------------
    # Risk calculations
    # ---------------------------------------------------------

    fraud_risk = float(
        fraud.get("max_risk_score", 0)
    )

    aml_risk = float(
        (
            risk.get("network_risk", 0)
            + risk.get("suspicious_transaction_risk", 0)
        )
        / 2
    )

    behavioral_risk = float(
        risk.get("anomaly_risk", 0)
    )

    overall_score = float(
        risk.get("final_risk_score", 0)
    )

    overall_level = risk.get(
        "final_risk_level",
        "LOW"
    )

    # ---------------------------------------------------------
    # Key findings
    # ---------------------------------------------------------

    findings = []

    if behavioral_risk >= 50:
        findings.append(
            "Transaction behavior shows significant abnormal activity."
        )

    if anomaly.get("anomalous_transactions", 0) > 0:
        findings.append(
            f"{anomaly.get('anomalous_transactions')} "
            "anomalous transactions detected."
        )

    if network.get("shared_device_count", 0) > 0:
        findings.append(
            f"Device activity is associated with "
            f"{network.get('shared_device_count')} "
            "shared-device relationships."
        )

    if network.get("network_risk_score", 0) >= 70:
        findings.append(
            "Suspicious transaction network activity detected."
        )

    if len(policies) > 0:
        findings.append(
            "Relevant AML/KYC policy guidance was retrieved "
            "for the investigation."
        )

    if not findings:
        findings.append(
            "No significant suspicious indicators were identified."
        )

    # ---------------------------------------------------------
    # Transaction evidence
    # ---------------------------------------------------------

    transaction_ids = [
        str(tx.get("transaction_id"))
        for tx in transactions
        if tx.get("transaction_id") is not None
    ]

    transaction_text = ", ".join(transaction_ids)

    if not transaction_text:
        transaction_text = "No transaction IDs available."

    # ---------------------------------------------------------
    # Related account evidence
    # ---------------------------------------------------------

    account_ids = []

    for account in related:

        if isinstance(account, dict):

            account_id_value = account.get("account_id")

            if account_id_value:
                account_ids.append(
                    str(account_id_value)
                )

    if account_id != "N/A":
        account_ids.insert(
            0,
            str(account_id)
        )

    account_ids = list(
        dict.fromkeys(account_ids)
    )

    account_text = ", ".join(account_ids)

    if not account_text:
        account_text = "No related account IDs available."

    # ---------------------------------------------------------
    # Policy evidence
    # ---------------------------------------------------------

    policy_text = []

    # Get unique policy document titles.
    document_titles = {}

    for policy in policies:

        if not isinstance(policy, dict):
            continue

        document_id = policy.get("document_id")

        if document_id is None:
            continue

        if document_id not in document_titles:

            with psycopg.connect(DATABASE_URL) as conn:

                with conn.cursor() as cur:

                    cur.execute(
                        """
                        SELECT title
                        FROM documents
                        WHERE document_id = %s
                        """,
                        (document_id,)
                    )

                    row = cur.fetchone()

                    if row:
                        document_titles[document_id] = str(
                            row[0]
                        )

    policy_text = list(
        document_titles.values()
    )

    if not policy_text:

        for policy in policies:

            if isinstance(policy, dict):

                content = str(
                    policy.get("content", "")
                ).strip()

                title = None

                for line in content.splitlines():

                    line = line.strip()

                    if line.startswith("# "):

                        title = line[2:].strip()
                        break

                if title and title not in policy_text:
                    policy_text.append(title)

            else:

                title = str(policy)

                if title not in policy_text:
                    policy_text.append(title)

    if not policy_text:

        policy_text.append(
            "No policy references available."
        )

    # ---------------------------------------------------------
    # Graph/network evidence
    # ---------------------------------------------------------

    graph_relationships = (
        f"Connected accounts: "
        f"{network.get('account_count', 0)}\n"
        f"Connected merchants: "
        f"{network.get('merchant_count', 0)}\n"
        f"Connected devices: "
        f"{network.get('device_count', 0)}\n"
        f"Shared devices: "
        f"{network.get('shared_device_count', 0)}\n"
        f"Related accounts: "
        f"{len(related)}"
    )

    # ---------------------------------------------------------
    # Final recommendation
    # ---------------------------------------------------------

    if overall_level == "HIGH":

        recommendation = (
            "Manual investigation recommended. "
            "The case should be reviewed by a financial crime "
            "investigator and escalated according to applicable "
            "AML policy."
        )

    elif overall_level == "MEDIUM":

        recommendation = (
            "Enhanced review recommended. "
            "Additional investigation should be performed before "
            "closing the case."
        )

    else:

        recommendation = (
            "Routine monitoring recommended. "
            "No immediate escalation is indicated by the "
            "automated assessment."
        )

    # ---------------------------------------------------------
    # Build V7 report
    # ---------------------------------------------------------

    report = f"""
======================================================================
FINAGENT — INVESTIGATION REPORT
======================================================================

CASE INFORMATION
----------------------------------------------------------------------

Customer            : {customer_id}
Customer Name       : {profile.get("name", "N/A")}
Account             : {account_id}
Investigation Date  : {investigation_date}
Case ID             : {case_id}

======================================================================
RISK ASSESSMENT
----------------------------------------------------------------------

Fraud Risk          : {fraud_risk:.2f}/100
AML Risk            : {aml_risk:.2f}/100
Behavioral Risk     : {behavioral_risk:.2f}/100

Overall Score       : {overall_score:.2f}/100
Overall Risk        : {overall_level}

======================================================================
KEY FINDINGS
----------------------------------------------------------------------

"""

    for index, finding in enumerate(
        findings,
        start=1
    ):
        report += (
            f"{index}. {finding}\n"
        )

    report += f"""
======================================================================
EVIDENCE
----------------------------------------------------------------------

Transaction IDs
---------------
{transaction_text}

Account IDs
-----------
{account_text}

Graph Relationships
-------------------
{graph_relationships}

Policy References
-----------------
"""

    for index, policy in enumerate(
        policy_text,
        start=1
    ):
        report += (
            f"{index}. {policy}\n"
        )

    report += f"""
Model Scores
------------
Maximum Model Risk Score       : {fraud.get("max_risk_score", 0)}
Average Model Risk Score       : {fraud.get("average_risk_score", 0)}
Maximum Anomaly Score          : {anomaly.get("maximum_anomaly_score", 0)}
Average Anomaly Score          : {anomaly.get("average_anomaly_score", 0)}
Network Risk Score             : {network.get("network_risk_score", 0)}
Recent Transactions Reviewed   : {len(transactions)}
Suspicious Transactions
(Full History)                 : {risk.get("suspicious_transaction_count", 0)}

======================================================================
RECOMMENDATION
----------------------------------------------------------------------

{recommendation}

======================================================================
REPORT DISCLAIMER
----------------------------------------------------------------------

This report is an automated investigation assessment generated by
FinAgent. Risk indicators and model scores should be reviewed by an
appropriately authorized financial crime investigator before final
action is taken.

======================================================================
END OF INVESTIGATION REPORT
======================================================================
"""

    return report


if __name__ == "__main__":

    customer_id = "CUST00001"

    print(
        "Generating V7 investigation report..."
    )

    report = generate_report(
        customer_id
    )

    print(report)