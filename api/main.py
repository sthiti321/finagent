import sys
from pathlib import Path


# ============================================================
# SOURCE DIRECTORY
# ============================================================

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))


# ============================================================
# FASTAPI IMPORTS
# ============================================================

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Query,
    Request,
    BackgroundTasks,
)

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware


# ============================================================
# SECURITY IMPORTS
# ============================================================

from api.security.config_security import (
    validate_security_config
)

from api.security.api_security import (
    limiter,
    check_request_size,
    add_security_headers,
    validate_http_method,
)

from api.security.file_security import (
    validate_protected_paths,
    ensure_security_directory,
)

from api.security.auth import (
    AUTH_DB,
    get_current_user,
    require_permission,
    create_token,
    verify_password
)

from api.security.data_security import (
    secure_response
)

from api.security.monitoring import (
    log_security_event
)

from api.security.incident_response import (
    get_incidents,
    update_incident_status,
    should_block_ip,
)

from api.security.audit import (
    record_audit_event,
    get_audit_events,
    verify_audit_integrity,
)

from api.security.security_health import run_security_health_check
from api.security.security_metrics import get_security_metrics

# ============================================================
# SECURITY INITIALIZATION
# ============================================================

validate_security_config()

ensure_security_directory()
validate_protected_paths()


# ============================================================
# FINAGENT MODULES
# ============================================================

from investigation_agent import (
    CUSTOMERS_FILE,
    get_customer_profile,
    get_transactions,
    get_behavior_profile,
    calculate_fraud_score,
    calculate_anomaly_score,
    analyze_network,
    get_related_accounts,
    search_policies,
)


import pandas as pd

from risk_engine import calculate_final_risk
from evidence_agent import build_evidence
from report_agent import generate_report

from api.case_manager import (
    create_case,
    get_case,
    get_cases,
    update_case_status,
    attach_case_data,
)


# ============================================================
# LOGIN MODEL
# ============================================================

class LoginRequest(BaseModel):
    username: str
    password: str


# ============================================================
# FINAGENT FASTAPI
# ============================================================

app = FastAPI(
    title="FinAgent API",
    description="Autonomous Financial Crime Investigation API",
    version="9.0.0"
)


app.state.limiter = limiter

app.add_middleware(
    SlowAPIMiddleware
)


# ============================================================
# TRUSTED HOST SECURITY
# ============================================================

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "127.0.0.1",
        "localhost",
    ]
)


# ============================================================
# SECURITY MIDDLEWARE
# ============================================================

@app.middleware("http")
async def security_middleware(request: Request, call_next):

    await check_request_size(request)
    await validate_http_method(request)

    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    if should_block_ip(client_ip):
        log_security_event(
            event="IP_BLOCKED",
            message=(
                f"client={client_ip} "
                f"path={request.url.path} "
                f"reason=security_threshold_exceeded"
            ),
            level="WARNING",
            source_ip=client_ip,
        )

        return JSONResponse(
            status_code=403,
            content={
                "error": "Access blocked",
                "message": "Request blocked due to repeated security violations."
            }
        )

    log_security_event(
        event="HTTP_REQUEST",
        message=(
            f"method={request.method} "
            f"path={request.url.path} "
            f"client={client_ip}"
        ),
        level="INFO",
        source_ip=client_ip,
    )

    response = await add_security_headers(
        request,
        call_next
    )

    if response.status_code == 401:

        log_security_event(
            event="UNAUTHORIZED_ACCESS",
            message=(
                f"method={request.method} "
                f"path={request.url.path} "
                f"client={client_ip}"
            ),
            level="WARNING",
            source_ip=client_ip,
        )

    elif response.status_code == 403:

        log_security_event(
            event="FORBIDDEN_ACCESS",
            message=(
                f"method={request.method} "
                f"path={request.url.path} "
                f"client={client_ip}"
            ),
            level="WARNING",
            source_ip=client_ip,
        )

    elif response.status_code == 429:

        log_security_event(
            event="RATE_LIMIT_EXCEEDED",
            message=(
                f"method={request.method} "
                f"path={request.url.path} "
                f"client={client_ip}"
            ),
            level="WARNING",
            source_ip=client_ip,
        )

    return response


# ============================================================
# AUTHENTICATION
# ============================================================

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    credentials: LoginRequest
):

    import sqlite3

    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    conn = sqlite3.connect(AUTH_DB)
    conn.row_factory = sqlite3.Row

    user = conn.execute(
        """
        SELECT username, password_hash, role, active
        FROM users
        WHERE username = ?
        """,
        (credentials.username,)
    ).fetchone()

    conn.close()

    # --------------------------------------------------------
    # USERNAME NOT FOUND
    # --------------------------------------------------------

    if not user:

        log_security_event(
            event="LOGIN_FAILED",
            message=(
                f"username={credentials.username} "
                f"client={client_ip}"
            ),
            level="WARNING",
            source_ip=client_ip,
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # --------------------------------------------------------
    # INACTIVE ACCOUNT
    # --------------------------------------------------------

    if not user["active"]:

        log_security_event(
            event="LOGIN_FAILED",
            message=(
                f"username={credentials.username} "
                f"reason=inactive_account "
                f"client={client_ip}"
            ),
            level="WARNING",
            source_ip=client_ip,
        )

        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    # --------------------------------------------------------
    # PASSWORD VERIFICATION
    # --------------------------------------------------------

    if not verify_password(
        credentials.password,
        user["password_hash"]
    ):

        log_security_event(
            event="LOGIN_FAILED",
            message=(
                f"username={credentials.username} "
                f"client={client_ip}"
            ),
            level="WARNING",
            source_ip=client_ip,
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # --------------------------------------------------------
    # SUCCESSFUL LOGIN
    # --------------------------------------------------------

    log_security_event(
        event="LOGIN_SUCCESS",
        message=(
            f"username={user['username']} "
            f"role={user['role']} "
            f"client={client_ip}"
        ),
        level="INFO",
        source_ip=client_ip,
    )

    record_audit_event(
        username=user["username"],
        action="LOGIN",
        resource="AUTHENTICATION",
        ip_address=client_ip,
        result="SUCCESS",
        details="User logged in successfully",
    )

    token = create_token(
        username=user["username"],
        role=user["role"]
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"]
    }


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://finagent-rrpw.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PATCH",
        "PUT",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "application": "FinAgent",
        "version": "9.0.0",
        "status": "running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# CUSTOMER PROFILE
# ============================================================

@app.get("/customers/{customer_id}")
def customer_profile(
    customer_id: str,
    current_user=Depends(
        require_permission("customer:read")
    )
):

    profile = get_customer_profile(
        customer_id
    )

    if not profile:

        raise HTTPException(
            status_code=404,
            detail=f"Customer {customer_id} not found."
        )

    return secure_response(profile)


# ============================================================
# CUSTOMER TRANSACTIONS
# ============================================================

@app.get("/customers/{customer_id}/transactions")
def customer_transactions(
    customer_id: str,

    limit: int = Query(
        20,
        ge=1,
        le=100
    ),

    current_user=Depends(
        require_permission("transaction:read")
    )
):

    transactions = get_transactions(
        customer_id,
        limit=limit
    )

    import math

    transactions = [
        {
            key: (
                None
                if isinstance(value, float)
                and math.isnan(value)
                else value
            )
            for key, value in transaction.items()
        }
        for transaction in transactions
    ]

    return secure_response({
        "customer_id": customer_id,
        "count": len(transactions),
        "transactions": transactions
    })


# ============================================================
# CUSTOMER BEHAVIOR
# ============================================================

@app.get("/customers/{customer_id}/behavior")
def customer_behavior(
    customer_id: str,
    current_user=Depends(
        require_permission("customer:read")
    )
):

    behavior = get_behavior_profile(
        customer_id
    )

    if not behavior:

        raise HTTPException(
            status_code=404,
            detail="Behavior profile not found."
        )

    return secure_response(behavior)


# ============================================================
# FRAUD RISK
# ============================================================

@app.get("/customers/{customer_id}/fraud-risk")
def fraud_risk(
    customer_id: str,
    current_user=Depends(
        require_permission("risk:read")
    )
):

    result = calculate_fraud_score(
        customer_id
    )

    if not result:

        raise HTTPException(
            status_code=404,
            detail="Fraud risk data not found."
        )

    return secure_response(result)


# ============================================================
# ANOMALY RISK
# ============================================================

@app.get("/customers/{customer_id}/anomaly-risk")
def anomaly_risk(
    customer_id: str,
    current_user=Depends(
        require_permission("risk:read")
    )
):

    result = calculate_anomaly_score(
        customer_id
    )

    if not result:

        raise HTTPException(
            status_code=404,
            detail="Anomaly data not found."
        )

    return secure_response(result)


# ============================================================
# NETWORK RISK
# ============================================================

@app.get("/customers/{customer_id}/network")
def customer_network(
    customer_id: str,
    current_user=Depends(
        require_permission("network:read")
    )
):

    result = analyze_network(
        customer_id
    )

    if not result.get("found"):

        raise HTTPException(
            status_code=404,
            detail=result.get(
                "message",
                "Network analysis not found."
            )
        )

    return secure_response(result)


# ============================================================
# RELATED ACCOUNTS
# ============================================================

@app.get("/customers/{customer_id}/related-accounts")
def related_accounts(
    customer_id: str,
    current_user=Depends(
        require_permission("network:read")
    )
):

    accounts = get_related_accounts(
        customer_id
    )

    return secure_response({
        "customer_id": customer_id,
        "count": len(accounts),
        "accounts": accounts
    })


# ============================================================
# FINAL RISK
# ============================================================

@app.get("/customers/{customer_id}/risk")
def final_risk(
    request: Request,
    customer_id: str,
    current_user=Depends(
        require_permission("risk:read")
    )
):
    result = calculate_final_risk(
        customer_id
    )

    record_audit_event(
        username=current_user.get(
    "username",
    current_user.get("sub", "ADMIN")
),
        action="RISK_VIEWED",
        resource="CUSTOMER_RISK",
        resource_id=customer_id,
        ip_address=(
            request.client.host
            if request.client
            else "unknown"
        ),
        result="SUCCESS",
        details="Customer final risk assessment viewed",
    )

    return secure_response(result)


# ============================================================
# EVIDENCE
# ============================================================

@app.get("/customers/{customer_id}/evidence")
def customer_evidence(
    customer_id: str,
    current_user=Depends(
        require_permission("evidence:read")
    )
):

    evidence = build_evidence(
        customer_id
    )

    return secure_response(evidence)


# ============================================================
# POLICY SEARCH
# ============================================================

@app.get("/policies/search")
def policy_search(
    query: str,
    top_k: int = 3,
    current_user=Depends(
        require_permission("policy:read")
    )
):

    results = search_policies(
        query,
        top_k=top_k
    )

    return secure_response({
        "query": query,
        "count": len(results),
        "results": results
    })


# ============================================================
# INVESTIGATION REPORT
# ============================================================

@app.get("/customers/{customer_id}/report")
@limiter.limit("20/minute")
async def investigation_report(
    request: Request,
    customer_id: str,
    current_user=Depends(
        require_permission("report:generate")
    )
):

    report = generate_report(
        customer_id
    )

    return secure_response({
        "customer_id": customer_id,
        "report": report
    })



# ============================================================
# FULL INVESTIGATION — AUTOMATIC CASE CREATION
# ============================================================

# ============================================================
# BACKGROUND CASE INVESTIGATION
# ============================================================

def complete_case_investigation(
    case_id: str,
    customer_id: str,
    username: str,
    client_ip: str,
):
    import json

    try:
        evidence = build_evidence(customer_id)

        attach_case_data(
            case_id=case_id,
            field="evidence_data",
            data=json.dumps(evidence, default=str),
        )

        report = generate_report(customer_id)

        attach_case_data(
            case_id=case_id,
            field="report_data",
            data=json.dumps(report, default=str),
        )

        attach_case_data(
            case_id=case_id,
            field="investigation_data",
            data=json.dumps(
                {
                    "customer_id": customer_id,
                    "investigated_by": username,
                    "investigation_status": "COMPLETED",
                },
                default=str,
            ),
        )

        record_audit_event(
            username=username,
            action="CASE_INVESTIGATION_COMPLETED",
            resource="INVESTIGATION_CASE",
            resource_id=case_id,
            ip_address=client_ip,
            result="SUCCESS",
            details=(
                f"Background investigation completed for "
                f"customer {customer_id}"
            ),
        )

    except Exception as exc:
        record_audit_event(
            username=username,
            action="CASE_INVESTIGATION_FAILED",
            resource="INVESTIGATION_CASE",
            resource_id=case_id,
            ip_address=client_ip,
            result="FAILURE",
            details=str(exc),
        )


@app.post("/customers/{customer_id}/investigate")
@limiter.limit("10/minute")
async def investigate(
    request: Request,
    background_tasks: BackgroundTasks,
    customer_id: str,
    current_user=Depends(
        require_permission("case:investigate")
    )
):
    import json

    username = current_user.get(
        "username",
        current_user.get("sub", "ADMIN")
    )

    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    customer = get_customer_profile(customer_id)

    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer {customer_id} not found."
        )

    case = create_case(
        customer_id=customer_id,
        created_by=username,
    )

    case_id = case["case_id"]

    update_case_status(
        case_id=case_id,
        status="INVESTIGATING",
    )

    risk = calculate_final_risk(customer_id)

    attach_case_data(
        case_id=case_id,
        field="risk_data",
        data=json.dumps(risk, default=str),
    )

    record_audit_event(
        username=username,
        action="INVESTIGATION_STARTED",
        resource="INVESTIGATION_CASE",
        resource_id=case_id,
        ip_address=client_ip,
        result="SUCCESS",
        details=(
            f"Investigation started for customer "
            f"{customer_id}"
        ),
    )

    background_tasks.add_task(
        complete_case_investigation,
        case_id,
        customer_id,
        username,
        client_ip,
    )

    return secure_response({
        "message": "Investigation started successfully",
        "case_id": case_id,
        "customer_id": customer_id,
        "status": "INVESTIGATING",
        "risk": risk,
        "processing": {
            "evidence": "IN_PROGRESS",
            "report": "IN_PROGRESS",
        },
    })

# ============================================================
# DASHBOARD RISK OVERVIEW
# ============================================================

@app.get("/dashboard/risk-overview")
async def dashboard_risk_overview(
    current_user=Depends(
        require_permission("risk:read")
    ),
):
    customers = pd.read_csv(
        CUSTOMERS_FILE
    )

    customer_ids = (
        customers["customer_id"]
        .astype(str)
        .str.strip()
        .tolist()
    )

    results = []

    for customer_id in customer_ids:
        try:
            risk = calculate_final_risk(
                customer_id
            )

            results.append(risk)

        except Exception:
            continue

    high_risk = [
        item
        for item in results
        if item["final_risk_level"] == "HIGH"
    ]

    medium_risk = [
        item
        for item in results
        if item["final_risk_level"] == "MEDIUM"
    ]

    low_risk = [
        item
        for item in results
        if item["final_risk_level"] == "LOW"
    ]

    high_risk = sorted(
        high_risk,
        key=lambda item: item["final_risk_score"],
        reverse=True,
    )

    active_cases = get_cases(
        status="OPEN"
    ) + get_cases(
        status="INVESTIGATING"
    ) + get_cases(
        status="CONTAINED"
    )

    return secure_response({
        "summary": {
            "total_customers": len(results),
            "high_risk": len(high_risk),
            "medium_risk": len(medium_risk),
            "low_risk": len(low_risk),
            "active_cases": len(active_cases),
        },

        "top_high_risk_customers":
            high_risk[:10],
    })



# ============================================================
# INVESTIGATION CASES
# ============================================================

@app.post("/cases")
async def create_investigation_case(
    customer_id: str,
    request: Request,
    current_user=Depends(
        require_permission("case:investigate")
    ),
):
    import json

    username = current_user.get(
        "username",
        current_user.get("sub", "ADMIN")
    )

    customer = get_customer_profile(customer_id)

    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer {customer_id} not found."
        )

    # --------------------------------------------------------
    # CALCULATE CUSTOMER RISK
    # --------------------------------------------------------

    risk = calculate_final_risk(
        customer_id
    )

    # --------------------------------------------------------
    # CREATE CASE
    # --------------------------------------------------------

    case = create_case(
        customer_id=customer_id,
        created_by=username,
    )

    case_id = case["case_id"]

    # --------------------------------------------------------
    # ATTACH RISK TO CASE
    # --------------------------------------------------------

    attach_case_data(
        case_id=case_id,
        field="risk_data",
        data=json.dumps(
            risk,
            default=str
        ),
    )

    # --------------------------------------------------------
    # AUDIT EVENT
    # --------------------------------------------------------

    record_audit_event(
        username=username,
        action="CASE_CREATED",
        resource="INVESTIGATION_CASE",
        resource_id=case_id,
        ip_address=(
            request.client.host
            if request.client
            else "unknown"
        ),
        result="SUCCESS",
        details=(
            f"Investigation case created for "
            f"customer {customer_id} "
            f"with risk level {risk['final_risk_level']}"
        ),
    )

    # --------------------------------------------------------
    # RETURN CASE WITH RISK
    # --------------------------------------------------------

    return secure_response(
        get_case(case_id)
    )


@app.get("/cases")
async def list_investigation_cases(
    customer_id: str = Query(None),
    status: str = Query(None),
    limit: int = Query(100, ge=1, le=500),
    current_user=Depends(
        require_permission("case:investigate")
    ),
):
    try:
        cases = get_cases(
            customer_id=customer_id,
            status=status,
            limit=limit,
        )

        return secure_response({
            "count": len(cases),
            "cases": cases,
        })

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@app.get("/cases/{case_id}")
async def get_investigation_case(
    case_id: str,
    current_user=Depends(
        require_permission("case:investigate")
    ),
):
    case = get_case(case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Investigation case not found."
        )

    return secure_response(case)


@app.patch("/cases/{case_id}")
async def update_investigation_case(
    case_id: str,
    status: str,
    request: Request,
    current_user=Depends(
        require_permission("case:investigate")
    ),
):
    username = current_user.get(
        "username",
        current_user.get("sub", "ADMIN")
    )

    try:
        updated = update_case_status(
            case_id=case_id,
            status=status,
        )

        if not updated:
            raise HTTPException(
                status_code=404,
                detail="Investigation case not found."
            )

        record_audit_event(
            username=username,
            action="CASE_STATUS_UPDATED",
            resource="INVESTIGATION_CASE",
            resource_id=case_id,
            ip_address=(
                request.client.host
                if request.client
                else "unknown"
            ),
            result="SUCCESS",
            details=f"Case status changed to {status.upper()}",
        )

        return secure_response({
            "message": "Case status updated successfully",
            "case": get_case(case_id),
        })

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ============================================================
# SECURITY INCIDENTS
# ============================================================

@app.get("/security/incidents")
async def list_security_incidents(
    status: str = Query(None),
    severity: str = Query(None),
    limit: int = Query(100),
    current_user=Depends(
        require_permission("*")
    ),
):

    try:

        return {
            "incidents": get_incidents(
                status=status,
                severity=severity,
                limit=limit,
            )
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ============================================================
# UPDATE SECURITY INCIDENT
# ============================================================

@app.patch("/security/incidents/{incident_id}")
async def update_security_incident(
    incident_id: str,
    status: str,
    request: Request,
    current_user=Depends(
        require_permission("*")
    ),
):

    try:

        updated = update_incident_status(
    incident_id=incident_id,
    status=status,
    resolved_by=current_user.get("username", current_user.get("sub", "ADMIN")),
)

        record_audit_event(
    username=current_user.get(
        "username",
        current_user.get("sub", "ADMIN")
    ),
    action="INCIDENT_STATUS_UPDATED",
    resource="SECURITY_INCIDENT",
    resource_id=incident_id,
    ip_address=(
        request.client.host
        if request.client
        else "unknown"
    ),
    result="SUCCESS",
    details=f"Incident status changed to {status.upper()}",
)

        if not updated:

            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        return {
            "message": "Incident status updated successfully",
            "incident_id": incident_id,
            "status": status.upper(),
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    # ============================================================
# AUDIT TRAIL
# ============================================================

@app.get("/security/audit")
async def list_audit_events(
    limit: int = Query(100),
    current_user=Depends(require_permission("*")),
):
    return {
        "audit_events": get_audit_events(limit)
    }


@app.get("/security/audit/integrity")
async def audit_integrity(
    current_user=Depends(require_permission("*")),
):
    return verify_audit_integrity()

@app.get("/security/health")
async def security_health(
    current_user=Depends(require_permission("*")),
):
    return run_security_health_check()

@app.get("/security/metrics")
async def security_metrics(
    current_user=Depends(require_permission("*")),
):
    return get_security_metrics()

@app.get("/security/posture")
async def security_posture(
    current_user=Depends(require_permission("*")),
):
    health = run_security_health_check()
    metrics = get_security_metrics()

    return {
        "security_status": health["overall_status"],
        "health_checks": health["checks"],
        "failed_checks": health["failed_checks"],
        "metrics": metrics,
    }