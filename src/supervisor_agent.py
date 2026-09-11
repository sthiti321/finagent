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


def supervisor(customer_id):
    """
    Supervisor coordinates the investigation workflow.
    """

    print("\n" + "=" * 70)
    print("FINAGENT SUPERVISOR")
    print("=" * 70)

    print(f"\nStarting investigation for customer: {customer_id}")

    investigation = {
        "customer_id": customer_id
    }

    # --------------------------------------------------------
    # STEP 1: Customer Investigation
    # --------------------------------------------------------

    print("\n[1/8] Getting customer profile...")

    investigation["customer_profile"] = (
        get_customer_profile(customer_id)
    )

    # --------------------------------------------------------
    # STEP 2: Transaction Investigation
    # --------------------------------------------------------

    print("[2/8] Getting recent transactions...")

    investigation["transactions"] = (
        get_transactions(
            customer_id,
            limit=20
        )
    )

    # --------------------------------------------------------
    # STEP 3: Behavior Investigation
    # --------------------------------------------------------

    print("[3/8] Analyzing customer behavior...")

    investigation["behavior"] = (
        get_behavior_profile(
            customer_id
        )
    )

    # --------------------------------------------------------
    # STEP 4: Fraud Risk
    # --------------------------------------------------------

    print("[4/8] Calculating fraud risk...")

    investigation["fraud_risk"] = (
        calculate_fraud_score(
            customer_id
        )
    )

    # --------------------------------------------------------
    # STEP 5: Anomaly Detection
    # --------------------------------------------------------

    print("[5/8] Calculating anomaly risk...")

    investigation["anomaly_risk"] = (
        calculate_anomaly_score(
            customer_id
        )
    )

    # --------------------------------------------------------
    # STEP 6: Network Investigation
    # --------------------------------------------------------

    print("[6/8] Analyzing transaction network...")

    investigation["network"] = (
        analyze_network(
            customer_id
        )
    )

    # --------------------------------------------------------
    # STEP 7: Related Accounts
    # --------------------------------------------------------

    print("[7/8] Finding related accounts...")

    investigation["related_accounts"] = (
        get_related_accounts(
            customer_id
        )
    )

    # --------------------------------------------------------
    # STEP 8: Policy Search
    # --------------------------------------------------------

    print("[8/8] Searching AML/KYC policies...")

    investigation["policies"] = search_policies(
        """
        customer investigation suspicious transactions
        network relationships anomaly risk AML investigation
        """
    )

    print("\nInvestigation workflow completed.")

    return investigation


# ============================================================
# TEST SUPERVISOR
# ============================================================

if __name__ == "__main__":

    customer_id = "C00001"

    result = supervisor(customer_id)

    print("\n" + "=" * 70)
    print("SUPERVISOR RESULT")
    print("=" * 70)

    print("\nCustomer:")
    print(result["customer_profile"])

    print("\nTransactions:")
    print(
        f"{len(result['transactions'])} transactions retrieved"
    )

    print("\nBehavior:")
    print(result["behavior"])

    print("\nFraud Risk:")
    print(result["fraud_risk"])

    print("\nAnomaly Risk:")
    print(result["anomaly_risk"])

    print("\nNetwork:")
    print(result["network"])

    print("\nRelated Accounts:")
    print(
        f"{len(result['related_accounts'])} related accounts"
    )

    print("\nPolicies Retrieved:")
    print(
        f"{len(result['policies'])} policy chunks"
    )