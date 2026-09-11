import os
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

TRANSACTIONS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "transactions",
    "transactions.csv"
)

RISK_FILE = os.path.join(
    BASE_DIR,
    "data",
    "transactions",
    "risk_results.csv"
)

ANOMALY_FILE = os.path.join(
    BASE_DIR,
    "data",
    "transactions",
    "anomaly_detection_results.csv"
)

NETWORK_FILE = os.path.join(
    BASE_DIR,
    "data",
    "transactions",
    "network_risk_results.csv"
)


def get_risk_level(score):

    if score >= 70:
        return "HIGH"

    elif score >= 30:
        return "MEDIUM"

    else:
        return "LOW"


def main():

    print("=" * 70)
    print("FINDING LOW / MEDIUM / HIGH TEST CUSTOMERS")
    print("=" * 70)

    print("\nLoading data...")

    transactions = pd.read_csv(
        TRANSACTIONS_FILE
    )

    risk = pd.read_csv(
        RISK_FILE
    )

    anomaly = pd.read_csv(
        ANOMALY_FILE
    )

    network = pd.read_csv(
        NETWORK_FILE
    )

    print(
        "Transactions:",
        len(transactions)
    )

    print(
        "Risk records:",
        len(risk)
    )

    print(
        "Anomaly records:",
        len(anomaly)
    )

    print(
        "Network records:",
        len(network)
    )


    # ========================================================
    # MODEL RISK
    # ========================================================

    # risk_results.csv contains transaction_id,
    # but does not contain customer_id.

    risk_with_customer = risk.merge(
        transactions[
            [
                "transaction_id",
                "customer_id"
            ]
        ],
        on="transaction_id",
        how="left"
    )

    model_risk = (
        risk_with_customer
        .groupby("customer_id")["risk_score"]
        .max()
        .reset_index()
        .rename(
            columns={
                "risk_score": "model_risk"
            }
        )
    )


    # ========================================================
    # ANOMALY RISK
    # ========================================================

    anomaly_risk = (
        anomaly
        .groupby("customer_id")["anomaly_score"]
        .max()
        .reset_index()
        .rename(
            columns={
                "anomaly_score":
                "maximum_anomaly_score"
            }
        )
    )

    anomaly_risk["anomaly_risk"] = (
        anomaly_risk["maximum_anomaly_score"]
        * 100
    )


    # ========================================================
    # NETWORK RISK
    # ========================================================

    account_customer = (
        transactions[
            [
                "account_id",
                "customer_id"
            ]
        ]
        .drop_duplicates()
    )

    network_customer = network.merge(
        account_customer,
        on="account_id",
        how="left"
    )

    network_risk = (
        network_customer
        .groupby("customer_id")["network_risk_score"]
        .max()
        .reset_index()
        .rename(
            columns={
                "network_risk_score":
                "network_risk"
            }
        )
    )


    # ========================================================
    # SUSPICIOUS TRANSACTION RISK
    # ========================================================

    suspicious = (
        transactions
        .groupby("customer_id")["is_suspicious"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "is_suspicious":
                "suspicious_count"
            }
        )
    )

    suspicious["suspicious_risk"] = (
        suspicious["suspicious_count"] * 2
    ).clip(upper=100)


    # ========================================================
    # COMBINE RESULTS
    # ========================================================

    results = model_risk.merge(
        anomaly_risk[
            [
                "customer_id",
                "anomaly_risk"
            ]
        ],
        on="customer_id",
        how="outer"
    )

    results = results.merge(
        network_risk,
        on="customer_id",
        how="outer"
    )

    results = results.merge(
        suspicious[
            [
                "customer_id",
                "suspicious_risk"
            ]
        ],
        on="customer_id",
        how="outer"
    )

    results = results.fillna(0)


    # ========================================================
    # FINAL RISK SCORE
    # Same weights as risk_engine.py
    # ========================================================

    results["final_risk_score"] = (
        results["model_risk"] * 0.40
        + results["anomaly_risk"] * 0.20
        + results["network_risk"] * 0.30
        + results["suspicious_risk"] * 0.10
    )

    results["final_risk_score"] = (
        results["final_risk_score"]
        .clip(upper=100)
    )

    results["risk_level"] = (
        results["final_risk_score"]
        .apply(get_risk_level)
    )


    # ========================================================
    # RISK DISTRIBUTION
    # ========================================================

    print("\nRisk distribution:")

    print(
        results["risk_level"]
        .value_counts()
    )


    # ========================================================
    # REPRESENTATIVE TEST CUSTOMERS
    # ========================================================

    print("\n" + "=" * 70)
    print("REPRESENTATIVE TEST CUSTOMERS")
    print("=" * 70)

    selected = []

    target_scores = {
        "LOW": 20,
        "MEDIUM": 50,
        "HIGH": 85
    }

    for level in [
        "LOW",
        "MEDIUM",
        "HIGH"
    ]:

        matching = results[
            results["risk_level"] == level
        ].copy()

        if matching.empty:

            print(
                f"\n{level}: No customer found"
            )

            continue

        matching["distance"] = (
            matching["final_risk_score"]
            - target_scores[level]
        ).abs()

        customer = (
            matching
            .sort_values("distance")
            .iloc[0]
        )

        print(f"\n{level}:")

        print(
            "Customer ID :",
            customer["customer_id"]
        )

        print(
            "Risk Score  :",
            round(
                customer["final_risk_score"],
                2
            )
        )

        print(
            "Risk Level  :",
            customer["risk_level"]
        )

        selected.append(customer)


    # ========================================================
    # SAVE RESULTS
    # ========================================================

    output_file = os.path.join(
        BASE_DIR,
        "data",
        "transactions",
        "customer_risk_evaluation.csv"
    )

    results[
        [
            "customer_id",
            "model_risk",
            "anomaly_risk",
            "network_risk",
            "suspicious_risk",
            "final_risk_score",
            "risk_level"
        ]
    ].sort_values(
        "final_risk_score",
        ascending=False
    ).to_csv(
        output_file,
        index=False
    )

    print(
        "\nFull results saved to:"
    )

    print(output_file)


if __name__ == "__main__":

    main()