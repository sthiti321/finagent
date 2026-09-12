const API_BASE = "https://repeat-objective-template-sold.trycloudflare.com";


/* ============================================================
   GENERIC API REQUEST
============================================================ */

export async function apiRequest(
  endpoint,
  options = {},
  token = null
) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(
    `${API_BASE}${endpoint}`,
    {
      ...options,
      headers,
    }
  );

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const message =
      data?.detail ||
      data?.message ||
      data?.error ||
      `Request failed with ${response.status}`;

    throw new Error(message);
  }

  return data;
}


/* ============================================================
   AUTHENTICATION
============================================================ */

export async function login(
  username,
  password
) {
  return apiRequest(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify({
        username,
        password,
      }),
    }
  );
}


/* ============================================================
   CASES
============================================================ */

export async function getCases(
  token
) {
  return apiRequest(
    "/cases?limit=100",
    {},
    token
  );
}


export async function getCase(
  caseId,
  token
) {
  return apiRequest(
    `/cases/${encodeURIComponent(
      caseId
    )}`,
    {},
    token
  );
}


export async function createCase(
  customerId,
  token
) {
  return apiRequest(
    `/cases?customer_id=${encodeURIComponent(
      customerId
    )}`,
    {
      method: "POST",
    },
    token
  );
}


export async function updateCaseStatus(
  caseId,
  status,
  token
) {
  return apiRequest(
    `/cases/${encodeURIComponent(
      caseId
    )}?status=${encodeURIComponent(
      status
    )}`,
    {
      method: "PATCH",
    },
    token
  );
}


/* ============================================================
   CUSTOMER
============================================================ */

export async function getCustomer(
  customerId,
  token
) {
  return apiRequest(
    `/customers/${encodeURIComponent(
      customerId
    )}`,
    {},
    token
  );
}


/* ============================================================
   CUSTOMER RISK
============================================================ */

export async function getCustomerRisk(
  customerId,
  token
) {
  return apiRequest(
    `/customers/${encodeURIComponent(
      customerId
    )}/risk`,
    {},
    token
  );
}


/* ============================================================
   INVESTIGATION
============================================================ */

export async function startInvestigation(
  customerId,
  token
) {
  return apiRequest(
    `/customers/${encodeURIComponent(
      customerId
    )}/investigate`,
    {
      method: "POST",
    },
    token
  );
}


/* ============================================================
   EVIDENCE
============================================================ */

export async function getCustomerEvidence(
  customerId,
  token
) {
  return apiRequest(
    `/customers/${encodeURIComponent(
      customerId
    )}/evidence`,
    {},
    token
  );
}


/* ============================================================
   REPORTS
============================================================ */

export async function getCustomerReport(
  customerId,
  token
) {
  return apiRequest(
    `/customers/${encodeURIComponent(
      customerId
    )}/report`,
    {},
    token
  );
}


/* ============================================================
   NETWORK INTELLIGENCE
============================================================ */

export async function getCustomerNetwork(
  customerId,
  token
) {
  return apiRequest(
    `/customers/${encodeURIComponent(
      customerId
    )}/network`,
    {},
    token
  );
}


export async function getRelatedAccounts(
  customerId,
  token
) {
  return apiRequest(
    `/customers/${encodeURIComponent(
      customerId
    )}/related-accounts`,
    {},
    token
  );
}


/* ============================================================
   SECURITY
============================================================ */

export async function getSecurityMetrics(
  token
) {
  return apiRequest(
    "/security/metrics",
    {},
    token
  );
}


export async function getSecurityPosture(
  token
) {
  return apiRequest(
    "/security/posture",
    {},
    token
  );
}


export async function getSecurityIncidents(
  token
) {
  return apiRequest(
    "/security/incidents?limit=100",
    {},
    token
  );
}


/* ============================================================
   AUDIT
============================================================ */

export async function getAuditEvents(
  token
) {
  return apiRequest(
    "/security/audit?limit=100",
    {},
    token
  );
}