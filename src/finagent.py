from supervisor_agent import supervisor
from evidence_agent import build_evidence
from risk_engine import calculate_final_risk
from report_agent import generate_report


def run_finagent(customer_id):

    print("\n" + "=" * 70)
    print("FINAGENT - AUTONOMOUS FINANCIAL CRIME INVESTIGATION")
    print("=" * 70)

    print(f"\nCustomer: {customer_id}")

    # Supervisor
    print("\n[1/4] Running Supervisor Agent...")
    supervisor(customer_id)

    # Evidence
    print("\n[2/4] Building Evidence Package...")
    build_evidence(customer_id)

    # Risk Engine
    print("\n[3/4] Running Risk Engine...")
    risk = calculate_final_risk(customer_id)

    print(
        f"Final Risk Score: {risk['final_risk_score']}/100"
    )

    print(
        f"Final Risk Level: {risk['final_risk_level']}"
    )

    # Report
    print("\n[4/4] Generating V7 Investigation Report...")

    report = generate_report(customer_id)

    print(report)

    return {
        "customer_id": customer_id,
        "risk": risk,
        "report": report
    }


if __name__ == "__main__":

    customer_id = "CUST00001"

    run_finagent(customer_id)