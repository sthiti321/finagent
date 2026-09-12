import os
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)


TRANSACTIONS_FILE = os.path.join(
    DATA_DIR,
    "transactions",
    "transactions.csv"
)

RISK_FILE = os.path.join(
    DATA_DIR,
    "transactions",
    "risk_results.csv"
)

ANOMALY_FILE = os.path.join(
    DATA_DIR,
    "transactions",
    "anomaly_detection_results.csv"
)

NETWORK_FILE = os.path.join(
    DATA_DIR,
    "transactions",
    "aml_network_pattern_results.csv"
)


def normalize_customer_id(customer_id):
    """
    Convert short customer IDs used by the application
    into the full customer IDs used by the datasets.

    Examples:
        C050  -> CUST00050
        C913  -> CUST00913
        CUST00050 -> CUST00050
    """

    customer_id = str(
        customer_id
    ).strip().upper()

    if customer_id.startswith("CUST"):
        return customer_id

    if customer_id.startswith("C"):
        number = customer_id[1:]

        if number.isdigit():
            return f"CUST{int(number):05d}"

    return customer_id


def calculate_final_risk(customer_id):

    original_customer_id = str(
        customer_id
    ).strip().upper()

    customer_id = normalize_customer_id(
        customer_id
    )

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


    # ---------------------------------------------------------
    # CUSTOMER TRANSACTIONS
    # ---------------------------------------------------------

    customer_transactions = transactions[
        transactions["customer_id"]
        == customer_id
    ]


    # ---------------------------------------------------------
    # MODEL RISK
    # ---------------------------------------------------------

    customer_risk = risk[
        risk["transaction_id"].isin(
            customer_transactions[
                "transaction_id"
            ]
        )
    ]


    model_risk = (
        customer_risk["risk_score"].max()
        if not customer_risk.empty
        else 0
    )


    # ---------------------------------------------------------
    # ANOMALY RISK
    # ---------------------------------------------------------

    customer_anomaly = anomaly[
        anomaly["customer_id"]
        == customer_id
    ]


    anomaly_score = (
        customer_anomaly[
            "anomaly_score"
        ].max()
        if not customer_anomaly.empty
        else 0
    )

    anomaly_risk = (
        anomaly_score * 100
    )


    # ---------------------------------------------------------
    # NETWORK RISK
    # ---------------------------------------------------------

    customer_network = network[
        network["customer_id"]
        == customer_id
    ]


    network_risk = (
        customer_network[
            "network_risk_score"
        ].iloc[0]
        if not customer_network.empty
        else 0
    )


    # ---------------------------------------------------------
    # SUSPICIOUS TRANSACTIONS
    # ---------------------------------------------------------

    suspicious_count = int(
        customer_transactions[
            "is_suspicious"
        ].sum()
    )


    suspicious_risk = min(
        suspicious_count * 2,
        100
    )


    # ---------------------------------------------------------
    # FINAL WEIGHTED RISK
    # ---------------------------------------------------------

    final_score = (
        (model_risk * 0.40)
        + (anomaly_risk * 0.20)
        + (network_risk * 0.30)
        + (suspicious_risk * 0.10)
    )


    final_score = min(
        final_score,
        100
    )


    # ---------------------------------------------------------
    # RISK LEVEL
    # ---------------------------------------------------------

    if final_score >= 70:
        risk_level = "HIGH"

    elif final_score >= 30:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"


    # ---------------------------------------------------------
    # RESULT
    # ---------------------------------------------------------

    return {
        "customer_id": original_customer_id,
        "dataset_customer_id": customer_id,
        "model_risk": round(
            model_risk,
            2
        ),
        "anomaly_risk": round(
            anomaly_risk,
            2
        ),
        "network_risk": round(
            network_risk,
            2
        ),
        "suspicious_transaction_count": suspicious_count,
        "suspicious_transaction_risk": round(
            suspicious_risk,
            2
        ),
        "final_risk_score": round(
            final_score,
            2
        ),
        "final_risk_level": risk_level
    }


if __name__ == "__main__":

    customer_id = "C050"

    result = calculate_final_risk(
        customer_id
    )

    print("\n" + "=" * 70)
    print("FINAGENT - RISK ENGINE")
    print("=" * 70)

    for key, value in result.items():
        print(
            f"{key}: {value}"
        )
