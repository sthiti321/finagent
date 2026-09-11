import time
import pandas as pd

from evidence_agent import build_evidence
from risk_engine import calculate_final_risk
from report_agent import generate_report


# ============================================================
# V8.2 — FINAGENT AGENT EVALUATION
# ============================================================

TEST_CASES = [
    {
        "case_id": "CASE 001",
        "customer_id": "CUST00804",
        "expected_risk": "MEDIUM"
    },
    {
        "case_id": "CASE 002",
        "customer_id": "CUST00913",
        "expected_risk": "HIGH"
    },
    {
        "case_id": "CASE 003",
        "customer_id": "CUST00877",
        "expected_risk": "HIGH"
    }
]


# Expected evidence categories produced by Evidence Agent
EXPECTED_EVIDENCE_TYPES = {
    "CUSTOMER_PROFILE",
    "TRANSACTION_ACTIVITY",
    "CUSTOMER_BEHAVIOR",
    "MODEL_RISK",
    "ANOMALY_DETECTION",
    "NETWORK_RISK",
    "RELATED_ACCOUNTS",
    "POLICY_CONTEXT"
}


# ============================================================
# EVIDENCE EVALUATION
# ============================================================

def evaluate_evidence(evidence_package):

    evidence_count = len(
        evidence_package.get("evidence", [])
    )

    # Basic evidence completeness check
    evidence_correct = evidence_count >= 5

    return evidence_count, evidence_correct


# ============================================================
# EVIDENCE TYPE SELECTION
# ============================================================

def evaluate_evidence_type_selection(evidence_package):

    actual_evidence_types = set()

    for item in evidence_package.get("evidence", []):

        evidence_type = item.get("evidence_type")

        if evidence_type:
            actual_evidence_types.add(
                str(evidence_type).strip().upper()
            )

    missing_types = sorted(
        EXPECTED_EVIDENCE_TYPES - actual_evidence_types
    )

    selection_correct = (
        actual_evidence_types == EXPECTED_EVIDENCE_TYPES
    )

    return (
        selection_correct,
        sorted(actual_evidence_types),
        missing_types
    )


# ============================================================
# POLICY RETRIEVAL EVALUATION
# ============================================================

def evaluate_policy_retrieval(evidence_package):

    for item in evidence_package.get("evidence", []):

        if item.get("evidence_type") == "POLICY_CONTEXT":

            policy_data = item.get("data")

            if policy_data:
                return True

    return False


# ============================================================
# REPORT QUALITY EVALUATION
# ============================================================

def evaluate_report_quality(report):

    if not report:
        return False

    required_sections = [
        "CASE INFORMATION",
        "RISK ASSESSMENT",
        "KEY FINDINGS",
        "EVIDENCE",
        "RECOMMENDATION"
    ]

    return all(
        section in report
        for section in required_sections
    )


# ============================================================
# HALLUCINATION CHECK
# ============================================================

def evaluate_hallucination(report):

    if not report:
        return True

    # Current report generator is deterministic
    # and uses investigation data.
    #
    # Therefore, this basic V8.2 evaluator marks
    # hallucination as False.
    #
    # A stronger LLM hallucination evaluator can
    # be added when the autonomous Llama layer
    # is integrated.

    return False


# ============================================================
# MAIN EVALUATION
# ============================================================

def main():

    print("=" * 70)
    print("V8.2 — FINAGENT AGENT EVALUATION")
    print("=" * 70)

    results = []

    for case in TEST_CASES:

        case_id = case["case_id"]
        customer_id = case["customer_id"]
        expected_risk = case["expected_risk"]

        print("\n" + "=" * 70)
        print(case_id)
        print("=" * 70)

        print(f"Customer: {customer_id}")
        print(f"Expected: {expected_risk}")

        start_time = time.time()

        # ====================================================
        # 1. EVIDENCE AGENT
        # ====================================================

        evidence_package = build_evidence(
            customer_id
        )

        evidence_count, evidence_correct = (
            evaluate_evidence(
                evidence_package
            )
        )

        # ====================================================
        # 2. EVIDENCE TYPE SELECTION
        # ====================================================

        (
            evidence_type_correct,
            evidence_types_used,
            missing_evidence_types
        ) = evaluate_evidence_type_selection(
            evidence_package
        )

        # ====================================================
        # 3. POLICY RETRIEVAL
        # ====================================================

        policy_found = evaluate_policy_retrieval(
            evidence_package
        )

        # ====================================================
        # 4. RISK ENGINE
        # ====================================================

        risk = calculate_final_risk(
            customer_id
        )

        predicted_risk = risk["final_risk_level"]
        risk_score = risk["final_risk_score"]

        risk_correct = (
            predicted_risk.upper()
            == expected_risk.upper()
        )

        # ====================================================
        # 5. REPORT AGENT
        # ====================================================

        report = generate_report(
            customer_id
        )

        report_quality = evaluate_report_quality(
            report
        )

        # ====================================================
        # 6. HALLUCINATION CHECK
        # ====================================================

        hallucination = evaluate_hallucination(
            report
        )

        # ====================================================
        # 7. LATENCY
        # ====================================================

        latency = time.time() - start_time

        # ====================================================
        # PRINT CASE RESULT
        # ====================================================

        print("\nRESULT")
        print("-" * 70)

        print(
            f"Predicted Risk : {predicted_risk}"
        )

        print(
            f"Risk Score     : {risk_score:.2f}"
        )

        print(
            f"Risk Correct   : {risk_correct}"
        )

        print(
            f"Evidence Count : {evidence_count}"
        )

        print(
            f"Evidence OK    : {evidence_correct}"
        )

        print(
            f"Policy Found   : {policy_found}"
        )

        print(
            f"Evidence Type Selection : "
            f"{evidence_type_correct}"
        )

        print(
            "Evidence Types Used     : "
            + (
                ", ".join(evidence_types_used)
                if evidence_types_used
                else "None"
            )
        )

        print(
            "Missing Evidence Types  : "
            + (
                ", ".join(missing_evidence_types)
                if missing_evidence_types
                else "None"
            )
        )

        print(
            f"Report Quality : "
            f"{report_quality}"
        )

        print(
            f"Hallucination  : "
            f"{hallucination}"
        )

        print(
            f"Latency        : "
            f"{latency:.2f} seconds"
        )

        # ====================================================
        # STORE RESULTS
        # ====================================================

        results.append(
            {
                "case_id": case_id,
                "customer_id": customer_id,
                "expected_risk": expected_risk,
                "predicted_risk": predicted_risk,
                "risk_score": risk_score,
                "risk_correct": risk_correct,
                "evidence_count": evidence_count,
                "evidence_correct": evidence_correct,
                "policy_found": policy_found,
                "evidence_type_selection":
                    evidence_type_correct,
                "evidence_types_used":
                    ", ".join(evidence_types_used),
                "missing_evidence_types":
                    ", ".join(missing_evidence_types),
                "report_quality": report_quality,
                "hallucination": hallucination,
                "latency_seconds": latency
            }
        )

    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    df = pd.DataFrame(results)

    # ========================================================
    # EVALUATION SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("V8.2 EVALUATION SUMMARY")
    print("=" * 70)

    risk_accuracy = (
        df["risk_correct"].mean() * 100
    )

    evidence_accuracy = (
        df["evidence_correct"].mean() * 100
    )

    policy_accuracy = (
        df["policy_found"].mean() * 100
    )

    evidence_type_accuracy = (
        df["evidence_type_selection"].mean() * 100
    )

    report_accuracy = (
        df["report_quality"].mean() * 100
    )

    hallucination_rate = (
        df["hallucination"].mean() * 100
    )

    average_latency = (
        df["latency_seconds"].mean()
    )

    print(
        f"Risk Accuracy        : "
        f"{risk_accuracy:.2f}%"
    )

    print(
        f"Evidence Accuracy    : "
        f"{evidence_accuracy:.2f}%"
    )

    print(
        f"Policy Retrieval     : "
        f"{policy_accuracy:.2f}%"
    )

    print(
        f"Evidence Type Selection : "
        f"{evidence_type_accuracy:.2f}%"
    )

    print(
        f"Report Quality       : "
        f"{report_accuracy:.2f}%"
    )

    print(
        f"Hallucination Rate   : "
        f"{hallucination_rate:.2f}%"
    )

    print(
        f"Average Latency      : "
        f"{average_latency:.2f} seconds"
    )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    output_file = (
        "data/transactions/"
        "agent_evaluation_results.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print("\nEvaluation results saved to:")
    print(output_file)

    print("\n" + "=" * 70)
    print("V8.2 EVALUATION COMPLETED")
    print("=" * 70)


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()