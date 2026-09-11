import { useEffect, useMemo, useState } from "react";

import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  BarChart3,
  Bell,
  BriefcaseBusiness,
  CheckCircle2,
  ChevronDown,
  CircleDot,
  FileSearch,
  FileText,
  Fingerprint,
  LayoutDashboard,
  LogOut,
  Network,
  RefreshCw,
  Search,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Users,
  X,
  Zap,
} from "lucide-react";

import { motion } from "framer-motion";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  login,
  getCases,
  getCase,
  createCase,
  updateCaseStatus,
  getSecurityMetrics,
  getSecurityPosture,
  getSecurityIncidents,
  getAuditEvents,
  getCustomer,
  getCustomerEvidence,
  getCustomerReport,
} from "./api";


/* ============================================================
   HELPERS
============================================================ */

function unwrap(data) {
  if (data?.data) {
    return data.data;
  }

  return data;
}


function safeJson(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return null;
  }

  if (typeof value === "object") {
    return value;
  }

  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}


async function fetchJson(
  url,
  token,
  options = {}
) {
  const response = await fetch(
    url,
    {
      ...options,
      headers: {
        ...(options.headers || {}),
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  const text = await response.text();

  let data = null;

  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
      data?.message ||
      `Request failed (${response.status})`
    );
  }

  return data;
}


/* ============================================================
   LOGIN
============================================================ */

function LoginScreen({ onLogin }) {
  const [username, setUsername] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    setLoading(true);
    setError("");

    try {
      const result = await login(
        username,
        password
      );

      if (!result?.access_token) {
        throw new Error(
          "Authentication token was not returned."
        );
      }

      localStorage.setItem(
        "finagent_token",
        result.access_token
      );

      localStorage.setItem(
        "finagent_role",
        result.role || ""
      );

      onLogin(result);
    } catch (err) {
      setError(
        err.message ||
        "Login failed."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#070b12] px-6 text-white">

      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-12rem] top-[-12rem] h-[35rem] w-[35rem] rounded-full bg-cyan-400/[0.07] blur-[140px]" />

        <div className="absolute right-[-10rem] bottom-[-12rem] h-[34rem] w-[34rem] rounded-full bg-violet-500/[0.06] blur-[140px]" />
      </div>

      <motion.div
        initial={{
          opacity: 0,
          y: 20,
        }}
        animate={{
          opacity: 1,
          y: 0,
        }}
        className="relative w-full max-w-md rounded-3xl border border-white/[0.08] bg-white/[0.035] p-8 shadow-2xl backdrop-blur-2xl"
      >

        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/[0.08]">
            <ShieldAlert
              size={24}
              className="text-cyan-300"
            />
          </div>

          <div>
            <div className="text-lg font-semibold tracking-[0.16em]">
              FINAGENT
            </div>

            <div className="text-[9px] uppercase tracking-[0.24em] text-slate-600">
              Financial Crime Intelligence
            </div>
          </div>
        </div>

        <div className="mb-7">
          <div className="text-2xl font-semibold">
            Welcome back.
          </div>

          <p className="mt-2 text-sm text-slate-500">
            Sign in to access the intelligence command center.
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-4"
        >

          <div>
            <label className="mb-2 block text-[10px] uppercase tracking-[0.18em] text-slate-600">
              Username
            </label>

            <input
              value={username}
              onChange={(event) =>
                setUsername(
                  event.target.value
                )
              }
              required
              className="h-12 w-full rounded-xl border border-white/[0.07] bg-black/20 px-4 text-sm text-white outline-none transition focus:border-cyan-400/30"
              placeholder="Enter username"
            />
          </div>

          <div>
            <label className="mb-2 block text-[10px] uppercase tracking-[0.18em] text-slate-600">
              Password
            </label>

            <input
              value={password}
              onChange={(event) =>
                setPassword(
                  event.target.value
                )
              }
              required
              type="password"
              className="h-12 w-full rounded-xl border border-white/[0.07] bg-black/20 px-4 text-sm text-white outline-none transition focus:border-cyan-400/30"
              placeholder="Enter password"
            />
          </div>

          {error && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/[0.07] px-4 py-3 text-xs text-red-300">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="flex h-12 w-full items-center justify-center gap-2 rounded-xl border border-cyan-300/20 bg-cyan-300/[0.08] text-sm font-medium text-cyan-200 transition hover:bg-cyan-300/[0.14] disabled:opacity-50"
          >
            <ShieldCheck size={16} />

            {loading
              ? "Authenticating..."
              : "Enter Command Center"}
          </button>

        </form>

        <div className="mt-7 border-t border-white/[0.06] pt-5 text-center text-[9px] uppercase tracking-[0.18em] text-slate-700">
          Secure Financial Crime Intelligence Platform
        </div>

      </motion.div>
    </div>
  );
}


/* ============================================================
   SHARED COMPONENTS
============================================================ */

function SectionHeader({
  eyebrow,
  title,
  subtitle,
  icon: Icon,
}) {
  return (
    <div>
      <div className="mb-2 flex items-center gap-2 text-[10px] uppercase tracking-[0.25em] text-slate-600">
        {Icon && (
          <Icon
            size={12}
            className="text-cyan-300"
          />
        )}

        {eyebrow}
      </div>

      <h2 className="text-3xl font-semibold tracking-tight text-white">
        {title}
      </h2>

      {subtitle && (
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
          {subtitle}
        </p>
      )}
    </div>
  );
}


function StatCard({
  icon: Icon,
  label,
  value,
  meta,
  accent,
}) {
  return (
    <motion.div
      whileHover={{
        y: -3,
      }}
      transition={{
        duration: 0.2,
      }}
      className="group relative overflow-hidden rounded-2xl border border-white/[0.08] bg-white/[0.035] p-5 backdrop-blur-xl"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-white/[0.04] to-transparent" />

      <div className="relative flex items-start justify-between">

        <div>
          <div className="text-[10px] uppercase tracking-[0.18em] text-slate-500">
            {label}
          </div>

          <div className="mt-3 flex items-end gap-2">
            <div className="text-3xl font-semibold text-white">
              {value}
            </div>

            <div className="mb-1 text-xs text-slate-600">
              {meta}
            </div>
          </div>
        </div>

        <div
          className={`rounded-xl border border-white/[0.08] bg-white/[0.04] p-2.5 ${accent}`}
        >
          <Icon size={19} />
        </div>

      </div>
    </motion.div>
  );
}


function RiskBadge({ level }) {
  const normalized =
    String(level || "UNKNOWN").toUpperCase();

  const styles = {
    CRITICAL:
      "text-red-300 bg-red-500/10 border-red-500/20",

    HIGH:
      "text-orange-300 bg-orange-500/10 border-orange-500/20",

    MEDIUM:
      "text-amber-300 bg-amber-500/10 border-amber-500/20",

    LOW:
      "text-emerald-300 bg-emerald-500/10 border-emerald-500/20",

    UNKNOWN:
      "text-slate-300 bg-white/[0.04] border-white/[0.08]",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] font-semibold tracking-[0.15em] ${
        styles[normalized] ||
        styles.UNKNOWN
      }`}
    >
      <CircleDot size={9} />
      {normalized}
    </span>
  );
}


/* ============================================================
   NAVIGATION
============================================================ */

const navItems = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
  },
  {
    label: "Cases",
    icon: BriefcaseBusiness,
  },
  {
    label: "Customers",
    icon: Users,
  },
  {
    label: "Evidence",
    icon: FileSearch,
  },
  {
    label: "Reports",
    icon: FileText,
  },
  {
    label: "Network",
    icon: Network,
  },
  {
    label: "Security",
    icon: ShieldCheck,
  },
  {
    label: "Audit",
    icon: Fingerprint,
  },
];


/* ============================================================
   CUSTOMER VIEW
============================================================ */

function CustomerView({ token }) {
  const [
    customerId,
    setCustomerId,
  ] = useState("");

  const [
    customer,
    setCustomer,
  ] = useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function searchCustomer() {
    const id =
      customerId.trim();

    if (!id) {
      setError(
        "Enter a customer ID."
      );
      return;
    }

    setLoading(true);
    setError("");
    setCustomer(null);

    try {
      const result =
        await getCustomer(
          id,
          token
        );

      const data =
        unwrap(result);

      if (
        data?.found === false
      ) {
        throw new Error(
          data.message ||
          `Customer ${id} not found.`
        );
      }

      setCustomer(data);
    } catch (err) {
      setError(
        err.message ||
        "Unable to load customer."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 12,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="space-y-6 px-5 py-7 lg:px-8"
    >
      <SectionHeader
        eyebrow="Customer Intelligence"
        title="Customers"
        subtitle="Explore customer profiles and investigation context."
        icon={Users}
      />

      <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5">

        <div className="flex flex-col gap-3 sm:flex-row">

          <input
            value={customerId}
            onChange={(event) =>
              setCustomerId(
                event.target.value
              )
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter"
              ) {
                searchCustomer();
              }
            }}
            placeholder="Enter customer ID — e.g. C002"
            className="h-12 flex-1 rounded-xl border border-white/[0.08] bg-black/20 px-4 text-sm text-white outline-none placeholder:text-slate-700 focus:border-cyan-400/30"
          />

          <button
            onClick={searchCustomer}
            disabled={loading}
            className="h-12 rounded-xl border border-cyan-400/20 bg-cyan-400/[0.08] px-6 text-xs font-semibold text-cyan-300 transition hover:bg-cyan-400/[0.14] disabled:opacity-40"
          >
            {loading
              ? "Searching..."
              : "Search Customer"}
          </button>

        </div>

        {error && (
          <div className="mt-4 rounded-xl border border-red-400/10 bg-red-400/[0.05] px-4 py-3 text-xs text-red-300">
            {error}
          </div>
        )}

      </div>

      {!customer &&
        !loading &&
        !error && (
          <div className="rounded-2xl border border-dashed border-white/[0.08] bg-white/[0.015] p-12 text-center">
            <Users
              size={34}
              className="mx-auto text-slate-700"
            />

            <div className="mt-4 text-sm font-medium text-slate-400">
              No customer selected
            </div>

            <p className="mx-auto mt-2 max-w-md text-xs leading-5 text-slate-600">
              Enter a customer ID to view
              the customer record.
            </p>
          </div>
        )}

      {customer && (
        <motion.div
          initial={{
            opacity: 0,
            y: 10,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          className="space-y-5"
        >

          <div className="rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.03] p-6">

            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">

              <div>
                <div className="text-[10px] uppercase tracking-[0.2em] text-slate-600">
                  Customer Intelligence
                </div>

                <h3 className="mt-2 text-2xl font-semibold text-white">
                  {customer.customer_id ||
                    customerId}
                </h3>

                <p className="mt-1 text-xs text-slate-500">
                  Verified customer record
                </p>
              </div>

              <div className="rounded-full border border-emerald-400/15 bg-emerald-400/[0.06] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.15em] text-emerald-300">
                Profile Found
              </div>

            </div>

          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">

            {Object.entries(customer)
              .filter(
                ([key]) =>
                  key !== "found"
              )
              .map(
                ([key, value]) => (
                  <div
                    key={key}
                    className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5"
                  >
                    <div className="text-[9px] uppercase tracking-[0.16em] text-slate-600">
                      {key.replaceAll(
                        "_",
                        " "
                      )}
                    </div>

                    <div className="mt-2 break-words text-sm font-medium text-slate-200">
                      {String(
                        value ?? "—"
                      )}
                    </div>
                  </div>
                )
              )}

          </div>

        </motion.div>
      )}

    </motion.div>
  );
}


/* ============================================================
   EVIDENCE VIEW
============================================================ */

function EvidenceView({ token }) {
  const [customerId, setCustomerId] =
    useState("");

  const [evidence, setEvidence] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function handleSearch() {
    const id =
      customerId.trim();

    if (!id) {
      setError(
        "Enter a customer ID."
      );
      return;
    }

    setLoading(true);
    setError("");
    setEvidence(null);

    try {
      const result =
        await getCustomerEvidence(
          id,
          token
        );

      const data =
        unwrap(result);

      if (
        data?.found === false
      ) {
        throw new Error(
          data.message ||
          `No evidence found for ${id}.`
        );
      }

      setEvidence(data);
    } catch (err) {
      setError(
        err.message ||
        "Unable to load evidence."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 12,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="space-y-6 px-5 py-7 lg:px-8"
    >

      <SectionHeader
        eyebrow="Investigation Support"
        title="Evidence"
        subtitle="Review supporting evidence associated with a customer investigation."
        icon={FileSearch}
      />

      <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5">

        <div className="flex flex-col gap-3 sm:flex-row">

          <input
            value={customerId}
            onChange={(event) =>
              setCustomerId(
                event.target.value
              )
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter"
              ) {
                handleSearch();
              }
            }}
            placeholder="Enter customer ID — e.g. C002"
            className="h-12 flex-1 rounded-xl border border-white/[0.08] bg-black/20 px-4 text-sm text-white outline-none placeholder:text-slate-700 focus:border-cyan-400/30"
          />

          <button
            onClick={handleSearch}
            disabled={loading}
            className="h-12 rounded-xl border border-cyan-400/20 bg-cyan-400/[0.08] px-6 text-xs font-semibold uppercase tracking-[0.12em] text-cyan-300 transition hover:bg-cyan-400/[0.14] disabled:opacity-40"
          >
            {loading
              ? "Loading..."
              : "View Evidence"}
          </button>

        </div>

        {error && (
          <div className="mt-4 rounded-xl border border-red-400/10 bg-red-400/[0.05] px-4 py-3 text-xs text-red-300">
            {error}
          </div>
        )}

      </div>

      {!evidence &&
        !loading &&
        !error && (
          <div className="rounded-2xl border border-dashed border-white/[0.08] bg-white/[0.015] p-12 text-center">

            <FileSearch
              size={34}
              className="mx-auto text-slate-700"
            />

            <div className="mt-4 text-sm font-medium text-slate-400">
              No evidence selected
            </div>

            <p className="mx-auto mt-2 max-w-md text-xs text-slate-600">
              Enter a customer ID to retrieve
              investigation evidence.
            </p>

          </div>
        )}

      {loading && (
        <div className="rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.025] p-10 text-center">

          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-cyan-300/20 border-t-cyan-300" />

          <div className="mt-4 text-sm text-slate-400">
            Collecting evidence...
          </div>

          <div className="mt-1 text-xs text-slate-600">
            FINAGENT is retrieving investigation signals.
          </div>

        </div>
      )}

      {evidence && !loading && (
        <motion.div
          initial={{
            opacity: 0,
            y: 12,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          className="space-y-5"
        >

          <div className="rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.025] p-6">

            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">

              <div>
                <div className="text-[10px] uppercase tracking-[0.22em] text-slate-600">
                  Evidence Intelligence
                </div>

                <h3 className="mt-2 text-2xl font-semibold text-white">
                  Customer {customerId}
                </h3>
              </div>

              <div className="inline-flex w-fit items-center gap-2 rounded-full border border-emerald-400/15 bg-emerald-400/[0.06] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.15em] text-emerald-300">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" />
                Evidence Found
              </div>

            </div>

          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">

            {Object.entries(evidence)
              .filter(
                ([key]) =>
                  key !== "found"
              )
              .map(
                ([key, value]) => {

                  const parsed =
                    safeJson(value);

                  const isObject =
                    parsed !== null &&
                    typeof parsed ===
                      "object";

                  return (
                    <div
                      key={key}
                      className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5"
                    >

                      <div className="text-[9px] uppercase tracking-[0.16em] text-slate-600">
                        {key
                          .replaceAll(
                            "_",
                            " "
                          )
                          .replace(
                            /\b\w/g,
                            (c) =>
                              c.toUpperCase()
                          )}
                      </div>

                      <div className="mt-3">

                        {Array.isArray(
                          parsed
                        ) ? (
                          <div className="space-y-2">

                            {parsed.length ===
                            0 ? (
                              <div className="text-sm text-slate-600">
                                No records found
                              </div>
                            ) : (
                              parsed.map(
                                (
                                  item,
                                  index
                                ) => (
                                  <div
                                    key={
                                      index
                                    }
                                    className="rounded-xl border border-white/[0.05] bg-black/10 p-3"
                                  >
                                    {typeof item ===
                                      "object" &&
                                    item !==
                                      null ? (
                                      <pre className="overflow-auto whitespace-pre-wrap text-[11px] leading-5 text-slate-400">
                                        {JSON.stringify(
                                          item,
                                          null,
                                          2
                                        )}
                                      </pre>
                                    ) : (
                                      <div className="text-xs text-slate-300">
                                        {String(
                                          item
                                        )}
                                      </div>
                                    )}
                                  </div>
                                )
                              )
                            )}

                          </div>
                        ) : isObject ? (
                          <pre className="max-h-72 overflow-auto whitespace-pre-wrap rounded-xl border border-white/[0.05] bg-black/10 p-3 text-[11px] leading-5 text-slate-400">
                            {JSON.stringify(
                              parsed,
                              null,
                              2
                            )}
                          </pre>
                        ) : (
                          <div className="break-words text-sm font-medium text-slate-200">
                            {String(
                              parsed ??
                                "—"
                            )}
                          </div>
                        )}

                      </div>

                    </div>
                  );
                }
              )}

          </div>

          <div className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-6">

            <div className="flex items-center gap-2">
              <ShieldCheck
                size={15}
                className="text-cyan-300"
              />

              <div className="text-[10px] uppercase tracking-[0.18em] text-slate-600">
                Evidence Summary
              </div>
            </div>

            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
              Supporting evidence associated with
              customer {customerId} is available
              for risk assessment and reporting.
            </p>

          </div>

        </motion.div>
      )}

    </motion.div>
  );
}


/* ============================================================
   REPORTS VIEW
============================================================ */

function ReportsView({ token }) {
  const [customerId, setCustomerId] =
    useState("");

  const [report, setReport] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function handleSearch() {
    const id =
      customerId.trim();

    if (!id) {
      setError(
        "Enter a customer ID."
      );
      return;
    }

    setLoading(true);
    setError("");
    setReport(null);

    try {
      const result =
        await getCustomerReport(
          id,
          token
        );

      const data =
        unwrap(result);

      if (
        data?.found === false
      ) {
        throw new Error(
          data.message ||
          `No report found for ${id}.`
        );
      }

      setReport(data);
    } catch (err) {
      setError(
        err.message ||
        "Unable to generate report."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 12,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="space-y-6 px-5 py-7 lg:px-8"
    >

      <SectionHeader
        eyebrow="Investigation Intelligence"
        title="Reports"
        subtitle="Generate and review investigation reports."
        icon={FileText}
      />

      <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5">

        <div className="flex flex-col gap-3 sm:flex-row">

          <input
            value={customerId}
            onChange={(event) =>
              setCustomerId(
                event.target.value
              )
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter"
              ) {
                handleSearch();
              }
            }}
            placeholder="Enter customer ID — e.g. C002"
            className="h-12 flex-1 rounded-xl border border-white/[0.08] bg-black/20 px-4 text-sm text-white outline-none placeholder:text-slate-700 focus:border-violet-400/30"
          />

          <button
            onClick={handleSearch}
            disabled={loading}
            className="h-12 rounded-xl border border-violet-400/20 bg-violet-400/[0.08] px-6 text-xs font-semibold uppercase tracking-[0.12em] text-violet-300 transition hover:bg-violet-400/[0.14] disabled:opacity-40"
          >
            {loading
              ? "Generating..."
              : "Generate Report"}
          </button>

        </div>

        {error && (
          <div className="mt-4 rounded-xl border border-red-400/10 bg-red-400/[0.05] px-4 py-3 text-xs text-red-300">
            {error}
          </div>
        )}

      </div>

      {!report &&
        !loading &&
        !error && (
          <div className="rounded-2xl border border-dashed border-white/[0.08] bg-white/[0.015] p-12 text-center">

            <FileText
              size={34}
              className="mx-auto text-slate-700"
            />

            <div className="mt-4 text-sm font-medium text-slate-400">
              No report selected
            </div>

            <p className="mx-auto mt-2 max-w-md text-xs text-slate-600">
              Enter a customer ID to generate
              an investigation report.
            </p>

          </div>
        )}

      {loading && (
        <div className="rounded-2xl border border-violet-400/10 bg-violet-400/[0.025] p-10 text-center">

          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-violet-300/20 border-t-violet-300" />

          <div className="mt-4 text-sm text-slate-400">
            Generating investigation report...
          </div>

        </div>
      )}

      {report && !loading && (
        <motion.div
          initial={{
            opacity: 0,
            y: 12,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          className="space-y-5"
        >

          <div className="rounded-2xl border border-violet-400/10 bg-violet-400/[0.025] p-6">

            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">

              <div>
                <div className="text-[10px] uppercase tracking-[0.22em] text-slate-600">
                  Investigation Report
                </div>

                <h3 className="mt-2 text-2xl font-semibold text-white">
                  Customer {customerId}
                </h3>
              </div>

              <div className="rounded-full border border-violet-400/15 bg-violet-400/[0.06] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.15em] text-violet-300">
                Report Ready
              </div>

            </div>

          </div>

          <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-6">

            <div className="mb-5 flex items-center gap-2">
              <FileText
                size={16}
                className="text-violet-300"
              />

              <div className="text-[10px] uppercase tracking-[0.18em] text-slate-600">
                Report Content
              </div>
            </div>

            {typeof report ===
            "string" ? (
              <div className="whitespace-pre-wrap text-sm leading-7 text-slate-300">
                {report}
              </div>
            ) : (
              <div className="space-y-4">

                {Object.entries(report)
                  .filter(
                    ([key]) =>
                      key !== "found"
                  )
                  .map(
                    ([key, value]) => (
                      <div
                        key={key}
                        className="rounded-2xl border border-white/[0.07] bg-black/10 p-5"
                      >
                        <div className="text-[9px] uppercase tracking-[0.16em] text-slate-600">
                          {key
                            .replaceAll(
                              "_",
                              " "
                            )
                            .replace(
                              /\b\w/g,
                              (c) =>
                                c.toUpperCase()
                            )}
                        </div>

                        <div className="mt-3">

                          {typeof value ===
                            "object" &&
                          value !== null ? (
                            <pre className="max-h-96 overflow-auto whitespace-pre-wrap text-xs leading-6 text-slate-400">
                              {JSON.stringify(
                                value,
                                null,
                                2
                              )}
                            </pre>
                          ) : (
                            <div className="whitespace-pre-wrap break-words text-sm leading-6 text-slate-300">
                              {String(
                                value ??
                                  "—"
                              )}
                            </div>
                          )}

                        </div>

                      </div>
                    )
                  )}

              </div>
            )}

          </div>

        </motion.div>
      )}

    </motion.div>
  );
}
/* ============================================================
   NETWORK VIEW
============================================================ */

function NetworkView({ token }) {
  const [customerId, setCustomerId] =
    useState("");

  const [network, setNetwork] =
    useState(null);

  const [
    relatedAccounts,
    setRelatedAccounts,
  ] = useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function analyzeNetwork() {
    const id =
      customerId.trim();

    if (!id) {
      setError(
        "Enter a customer ID."
      );
      return;
    }

    setLoading(true);
    setError("");
    setNetwork(null);
    setRelatedAccounts(null);

    try {
      const [
        networkResult,
        relatedResult,
      ] = await Promise.all([
        fetchJson(
          `http://127.0.0.1:8000/customers/${encodeURIComponent(
            id
          )}/network`,
          token
        ),
        fetchJson(
          `http://127.0.0.1:8000/customers/${encodeURIComponent(
            id
          )}/related-accounts`,
          token
        ),
      ]);

      setNetwork(
        unwrap(networkResult)
      );

      setRelatedAccounts(
        unwrap(relatedResult)
      );
    } catch (err) {
      setError(
        err.message ||
        "Unable to load network intelligence."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 12,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="space-y-6 px-5 py-7 lg:px-8"
    >

      <SectionHeader
        eyebrow="Relationship Intelligence"
        title="Network"
        subtitle="Examine customer relationships and connected accounts."
        icon={Network}
      />

      <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5">

        <div className="flex flex-col gap-3 sm:flex-row">

          <input
            value={customerId}
            onChange={(event) =>
              setCustomerId(
                event.target.value
              )
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter"
              ) {
                analyzeNetwork();
              }
            }}
            placeholder="Enter customer ID — e.g. C002"
            className="h-12 flex-1 rounded-xl border border-white/[0.08] bg-black/20 px-4 text-sm text-white outline-none placeholder:text-slate-700 focus:border-cyan-400/30"
          />

          <button
            onClick={analyzeNetwork}
            disabled={loading}
            className="h-12 rounded-xl border border-cyan-400/20 bg-cyan-400/[0.08] px-6 text-xs font-semibold uppercase tracking-[0.12em] text-cyan-300 transition hover:bg-cyan-400/[0.14] disabled:opacity-40"
          >
            {loading
              ? "Analyzing..."
              : "Analyze Network"}
          </button>

        </div>

        {error && (
          <div className="mt-4 rounded-xl border border-red-400/10 bg-red-400/[0.05] px-4 py-3 text-xs text-red-300">
            {error}
          </div>
        )}

      </div>

      {!network &&
        !relatedAccounts &&
        !loading &&
        !error && (
          <div className="rounded-2xl border border-dashed border-white/[0.08] bg-white/[0.015] p-12 text-center">

            <Network
              size={34}
              className="mx-auto text-slate-700"
            />

            <div className="mt-4 text-sm font-medium text-slate-400">
              No network selected
            </div>

            <p className="mx-auto mt-2 max-w-md text-xs text-slate-600">
              Enter a customer ID to inspect
              connected accounts and network data.
            </p>

          </div>
        )}

      {loading && (
        <div className="rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.025] p-10 text-center">

          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-cyan-300/20 border-t-cyan-300" />

          <div className="mt-4 text-sm text-slate-400">
            Analyzing customer network...
          </div>

          <div className="mt-1 text-xs text-slate-600">
            Mapping relationship signals.
          </div>

        </div>
      )}

      {(network ||
        relatedAccounts) &&
        !loading && (
          <motion.div
            initial={{
              opacity: 0,
              y: 12,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            className="space-y-5"
          >

            <div className="rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.025] p-6">

              <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">

                <div>
                  <div className="text-[10px] uppercase tracking-[0.22em] text-slate-600">
                    Network Intelligence
                  </div>

                  <h3 className="mt-2 text-2xl font-semibold text-white">
                    Customer {customerId}
                  </h3>

                  <p className="mt-2 text-xs text-slate-500">
                    Relationship and network analysis
                  </p>
                </div>

                <div className="rounded-full border border-cyan-400/15 bg-cyan-400/[0.06] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.15em] text-cyan-300">
                  Analysis Complete
                </div>

              </div>

            </div>

            {network && (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">

                {Object.entries(network)
                  .filter(
                    ([key]) =>
                      key !== "found"
                  )
                  .map(
                    ([key, value]) => {

                      const parsed =
                        safeJson(value);

                      return (
                        <div
                          key={key}
                          className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5"
                        >

                          <div className="text-[9px] uppercase tracking-[0.16em] text-slate-600">
                            {key
                              .replaceAll(
                                "_",
                                " "
                              )
                              .replace(
                                /\b\w/g,
                                (c) =>
                                  c.toUpperCase()
                              )}
                          </div>

                          <div className="mt-3">

                            {typeof parsed ===
                              "object" &&
                            parsed !==
                              null ? (
                              <pre className="max-h-64 overflow-auto whitespace-pre-wrap text-[11px] leading-5 text-slate-400">
                                {JSON.stringify(
                                  parsed,
                                  null,
                                  2
                                )}
                              </pre>
                            ) : (
                              <div className="break-words text-sm font-medium text-slate-200">
                                {String(
                                  parsed ??
                                    "—"
                                )}
                              </div>
                            )}

                          </div>

                        </div>
                      );
                    }
                  )}

              </div>
            )}

            <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-6">

              <div className="flex items-center justify-between gap-4">

                <div>
                  <div className="text-[10px] uppercase tracking-[0.18em] text-slate-600">
                    Relationship Intelligence
                  </div>

                  <h3 className="mt-2 text-lg font-semibold text-white">
                    Related Accounts
                  </h3>
                </div>

                <div className="rounded-full border border-white/[0.08] bg-white/[0.03] px-3 py-1.5 text-[10px] text-slate-400">
                  {Array.isArray(
                    relatedAccounts?.accounts
                  )
                    ? relatedAccounts
                        .accounts
                        .length
                    : relatedAccounts?.count ??
                      0}{" "}
                  connected
                </div>

              </div>

              <div className="mt-5 space-y-3">

                {Array.isArray(
                  relatedAccounts?.accounts
                ) &&
                relatedAccounts.accounts
                  .length > 0 ? (
                  relatedAccounts.accounts.map(
                    (
                      account,
                      index
                    ) => (
                      <div
                        key={index}
                        className="rounded-xl border border-white/[0.06] bg-black/10 p-4"
                      >

                        {typeof account ===
                          "object" &&
                        account !==
                          null ? (
                          <pre className="overflow-auto whitespace-pre-wrap text-xs leading-5 text-slate-400">
                            {JSON.stringify(
                              account,
                              null,
                              2
                            )}
                          </pre>
                        ) : (
                          <div className="text-sm text-slate-300">
                            {String(
                              account
                            )}
                          </div>
                        )}

                      </div>
                    )
                  )
                ) : (
                  <div className="rounded-xl border border-dashed border-white/[0.06] p-8 text-center text-xs text-slate-600">
                    No related accounts found.
                  </div>
                )}

              </div>

            </div>

          </motion.div>
        )}

    </motion.div>
  );
}


/* ============================================================
   SECURITY VIEW
============================================================ */

function SecurityView({
  metrics,
  posture,
  incidents,
  loading,
  onRefresh,
}) {
  const status =
    posture?.security_status ||
    "UNKNOWN";

  const score =
    status === "PASS"
      ? 100
      : status === "FAIL"
        ? 55
        : 0;

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 12,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="space-y-6 px-5 py-7 lg:px-8"
    >

      <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-end">

        <SectionHeader
          eyebrow="Platform Protection"
          title="Security"
          subtitle="Monitor security posture, incidents, and defensive activity."
          icon={ShieldCheck}
        />

        <button
          onClick={onRefresh}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-cyan-400/20 bg-cyan-400/[0.07] px-4 py-2.5 text-xs font-semibold text-cyan-300 transition hover:bg-cyan-400/[0.12] disabled:opacity-40"
        >
          <RefreshCw
            size={14}
            className={
              loading
                ? "animate-spin"
                : ""
            }
          />
          Refresh Security
        </button>

      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <StatCard
          icon={ShieldCheck}
          label="Security Posture"
          value={`${score}%`}
          meta={status}
          accent="text-emerald-300"
        />

        <StatCard
          icon={AlertTriangle}
          label="Total Incidents"
          value={
            metrics.security_incidents ||
            0
          }
          meta="recorded"
          accent="text-orange-300"
        />

        <StatCard
          icon={ShieldAlert}
          label="Critical"
          value={
            metrics.critical_incidents ||
            0
          }
          meta="attention"
          accent="text-red-300"
        />

        <StatCard
          icon={CheckCircle2}
          label="Resolved"
          value={
            metrics.resolved_incidents ||
            0
          }
          meta="closed"
          accent="text-emerald-300"
        />

      </div>

      <div className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">

        <section className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-6">

          <div className="flex items-center gap-2 text-xs font-medium">
            <ShieldCheck
              size={15}
              className="text-emerald-300"
            />
            Security posture
          </div>

          <div className="mt-7 flex items-center gap-6">

            <div className="relative flex h-28 w-28 items-center justify-center rounded-full border-4 border-emerald-400/20">

              <div className="text-2xl font-semibold">
                {score}%
              </div>

              <div className="absolute inset-[-4px] rounded-full border-4 border-transparent border-t-emerald-400/80" />

            </div>

            <div>
              <div className="text-lg font-medium text-white">
                {status}
              </div>

              <div className="mt-2 text-xs leading-5 text-slate-600">
                Live security assessment from FINAGENT.
              </div>
            </div>

          </div>

        </section>

        <section className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-6">

          <div className="flex items-center gap-2 text-xs font-medium">
            <AlertTriangle
              size={15}
              className="text-orange-300"
            />
            Recent security incidents
          </div>

          <div className="mt-5 space-y-2">

            {incidents
              .slice(0, 10)
              .map(
                (
                  incident,
                  index
                ) => (
                  <div
                    key={
                      incident.incident_id ||
                      incident.id ||
                      index
                    }
                    className="rounded-xl border border-white/[0.06] bg-black/10 p-4"
                  >

                    <div className="flex items-start justify-between gap-3">

                      <div>
                        <div className="text-xs font-medium text-slate-200">
                          {incident.event_type ||
                            incident.event ||
                            incident.title ||
                            "Security event"}
                        </div>

                        <div className="mt-1 text-[10px] text-slate-600">
                          {incident.source_ip ||
                            incident.ip_address ||
                            "unknown source"}
                        </div>
                      </div>

                      <RiskBadge
                        level={
                          incident.severity ||
                          "LOW"
                        }
                      />

                    </div>

                    {incident.message && (
                      <div className="mt-3 text-xs leading-5 text-slate-500">
                        {incident.message}
                      </div>
                    )}

                  </div>
                )
              )}

            {!loading &&
              incidents.length ===
                0 && (
                <div className="rounded-xl border border-dashed border-white/[0.06] p-8 text-center text-xs text-slate-600">
                  No security incidents found.
                </div>
              )}

          </div>

        </section>

      </div>

    </motion.div>
  );
}


/* ============================================================
   AUDIT VIEW
============================================================ */

function AuditView({
  auditEvents,
  loading,
}) {
  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 12,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="space-y-6 px-5 py-7 lg:px-8"
    >

      <SectionHeader
        eyebrow="Governance & Traceability"
        title="Audit"
        subtitle="Review the recent FINAGENT audit trail."
        icon={Fingerprint}
      />

      <section className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-6">

        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">

          <div>
            <div className="text-sm font-medium text-white">
              Audit trail
            </div>

            <div className="mt-1 text-xs text-slate-600">
              {auditEvents.length} recent audit events loaded
            </div>
          </div>

          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-400/15 bg-emerald-400/[0.05] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-emerald-300">
            <Fingerprint size={12} />
            Audit Feed
          </div>

        </div>

        <div className="mt-6 overflow-hidden rounded-xl border border-white/[0.06]">

          <div className="grid grid-cols-[1fr_1fr_1fr_auto] gap-4 border-b border-white/[0.06] bg-white/[0.02] px-4 py-3 text-[9px] uppercase tracking-[0.16em] text-slate-600">
            <div>Action</div>
            <div>Resource</div>
            <div>Result</div>
            <div>Time</div>
          </div>

          <div className="divide-y divide-white/[0.05]">

            {auditEvents
              .slice(0, 30)
              .map(
                (
                  event,
                  index
                ) => (
                  <div
                    key={
                      event.audit_id ||
                      event.id ||
                      index
                    }
                    className="grid grid-cols-[1fr_1fr_1fr_auto] gap-4 px-4 py-4 text-xs"
                  >
                    <div className="font-medium text-slate-200">
                      {event.action ||
                        "EVENT"}
                    </div>

                    <div className="text-slate-500">
                      {event.resource ||
                        "—"}
                    </div>

                    <div
                      className={
                        String(
                          event.result ||
                            ""
                        ).toUpperCase() ===
                        "SUCCESS"
                          ? "text-emerald-300"
                          : "text-slate-400"
                      }
                    >
                      {event.result ||
                        "—"}
                    </div>

                    <div className="text-slate-600">
                      {event.timestamp
                        ? new Date(
                            event.timestamp
                          ).toLocaleString()
                        : "—"}
                    </div>

                  </div>
                )
              )}

            {!loading &&
              auditEvents.length ===
                0 && (
                <div className="p-10 text-center text-xs text-slate-600">
                  No audit events found.
                </div>
              )}

          </div>

        </div>

      </section>

    </motion.div>
  );
}


/* ============================================================
   CASE DATA CARD
============================================================ */

function CaseDataCard({
  title,
  icon: Icon,
  data,
  empty,
}) {
  return (
    <section className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5">

      <div className="mb-4 flex items-center gap-2 text-sm font-medium">
        <Icon
          size={16}
          className="text-cyan-300"
        />

        {title}
      </div>

      {data ? (
        <pre className="max-h-[380px] overflow-auto whitespace-pre-wrap rounded-xl border border-white/[0.05] bg-black/20 p-4 text-xs leading-6 text-slate-400">
          {typeof data ===
          "string"
            ? data
            : JSON.stringify(
                data,
                null,
                2
              )}
        </pre>
      ) : (
        <div className="rounded-xl border border-dashed border-white/[0.06] p-6 text-center text-xs text-slate-600">
          {empty}
        </div>
      )}

    </section>
  );
}
/* ============================================================
   CASE DETAILS
============================================================ */

function CaseDetails({
  caseId,
  token,
  onBack,
  onRefresh,
}) {
  const [caseData, setCaseData] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [updating, setUpdating] =
    useState(false);

  async function loadCase() {
    try {
      setLoading(true);
      setError("");

      const result =
        await getCase(
          caseId,
          token
        );

      setCaseData(
        unwrap(result)
      );
    } catch (err) {
      setError(
        err.message ||
        "Unable to load case."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCase();
  }, [caseId]);

  async function changeStatus(
    status
  ) {
    setUpdating(true);
    setError("");

    try {
      const result =
        await updateCaseStatus(
          caseId,
          status,
          token
        );

      setCaseData(
        unwrap(result)?.case ||
        unwrap(result)
      );

      await onRefresh?.();
    } catch (err) {
      setError(
        err.message ||
        "Unable to update case."
      );
    } finally {
      setUpdating(false);
    }
  }

  if (loading) {
    return (
      <div className="px-5 py-7 lg:px-8">

        <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-10 text-center text-sm text-slate-500">
          Loading case intelligence...
        </div>

      </div>
    );
  }

  if (error && !caseData) {
    return (
      <div className="px-5 py-7 lg:px-8">

        <button
          onClick={onBack}
          className="mb-5 text-xs text-cyan-300"
        >
          ← Back to cases
        </button>

        <div className="rounded-xl border border-red-500/20 bg-red-500/[0.06] p-6 text-sm text-red-300">
          {error}
        </div>

      </div>
    );
  }

  const riskData =
    safeJson(
      caseData?.risk_data
    );

  const evidenceData =
    safeJson(
      caseData?.evidence_data
    );

  const investigationData =
    safeJson(
      caseData?.investigation_data
    );

  const reportData =
    safeJson(
      caseData?.report_data
    );

  const risk =
    caseData?.risk_level ||
    riskData?.final_risk_level ||
    "UNKNOWN";

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 12,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="space-y-5 px-5 py-7 lg:px-8"
    >

      <button
        onClick={onBack}
        className="text-xs text-cyan-300 hover:text-cyan-200"
      >
        ← Back to cases
      </button>

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/[0.06] px-4 py-3 text-xs text-red-300">
          {error}
        </div>
      )}

      <div className="rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.025] p-6">

        <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-start">

          <div>
            <div className="text-[10px] uppercase tracking-[0.22em] text-slate-600">
              Investigation Case
            </div>

            <h2 className="mt-2 text-3xl font-semibold text-white">
              {caseData.case_id}
            </h2>

            <p className="mt-2 text-sm text-slate-500">
              Customer {caseData.customer_id}
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <RiskBadge
              level={risk}
            />

            <span className="rounded-full border border-white/[0.08] bg-white/[0.03] px-3 py-1.5 text-[10px] uppercase tracking-[0.14em] text-slate-400">
              {caseData.status}
            </span>
          </div>

        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">

          <div className="rounded-xl border border-white/[0.06] bg-black/10 p-4">
            <div className="text-[9px] uppercase tracking-[0.14em] text-slate-600">
              Customer
            </div>

            <div className="mt-2 text-sm font-medium text-slate-200">
              {caseData.customer_id}
            </div>
          </div>

          <div className="rounded-xl border border-white/[0.06] bg-black/10 p-4">
            <div className="text-[9px] uppercase tracking-[0.14em] text-slate-600">
              Created By
            </div>

            <div className="mt-2 text-sm font-medium text-slate-200">
              {caseData.created_by}
            </div>
          </div>

          <div className="rounded-xl border border-white/[0.06] bg-black/10 p-4">
            <div className="text-[9px] uppercase tracking-[0.14em] text-slate-600">
              Created
            </div>

            <div className="mt-2 text-sm text-slate-300">
              {caseData.created_at
                ? new Date(
                    caseData.created_at
                  ).toLocaleString()
                : "—"}
            </div>
          </div>

          <div className="rounded-xl border border-white/[0.06] bg-black/10 p-4">
            <div className="text-[9px] uppercase tracking-[0.14em] text-slate-600">
              Updated
            </div>

            <div className="mt-2 text-sm text-slate-300">
              {caseData.updated_at
                ? new Date(
                    caseData.updated_at
                  ).toLocaleString()
                : "—"}
            </div>
          </div>

        </div>

      </div>

      <div className="flex flex-wrap gap-2">

        {caseData.status ===
          "OPEN" && (
          <button
            onClick={() =>
              changeStatus(
                "INVESTIGATING"
              )
            }
            disabled={updating}
            className="rounded-xl border border-cyan-400/20 bg-cyan-400/[0.08] px-4 py-2.5 text-xs font-semibold text-cyan-300 transition hover:bg-cyan-400/[0.14] disabled:opacity-40"
          >
            {updating
              ? "Updating..."
              : "Investigate"}
          </button>
        )}

        {caseData.status ===
          "INVESTIGATING" && (
          <button
            onClick={() =>
              changeStatus(
                "CONTAINED"
              )
            }
            disabled={updating}
            className="rounded-xl border border-orange-400/20 bg-orange-400/[0.07] px-4 py-2.5 text-xs font-semibold text-orange-300 disabled:opacity-40"
          >
            {updating
              ? "Updating..."
              : "Mark Contained"}
          </button>
        )}

        {(caseData.status ===
          "INVESTIGATING" ||
          caseData.status ===
            "CONTAINED") && (
          <button
            onClick={() =>
              changeStatus(
                "RESOLVED"
              )
            }
            disabled={updating}
            className="rounded-xl border border-emerald-400/20 bg-emerald-400/[0.07] px-4 py-2.5 text-xs font-semibold text-emerald-300 disabled:opacity-40"
          >
            {updating
              ? "Updating..."
              : "Resolve Case"}
          </button>
        )}

      </div>

      <div className="grid gap-5 lg:grid-cols-2">

        <CaseDataCard
          title="Risk Intelligence"
          icon={ShieldAlert}
          data={riskData}
          empty="Risk data is not available yet."
        />

        <CaseDataCard
          title="Evidence"
          icon={FileSearch}
          data={evidenceData}
          empty="Evidence is not available yet."
        />

        <CaseDataCard
          title="Investigation"
          icon={Activity}
          data={investigationData}
          empty="Investigation data is not available yet."
        />

        <CaseDataCard
          title="Report"
          icon={FileText}
          data={reportData}
          empty="Report is not available yet."
        />

      </div>

    </motion.div>
  );
}


/* ============================================================
   CASES VIEW
============================================================ */

function CasesView({
  cases,
  token,
  onRefresh,
  onSelectCase,
}) {
  const [
    showCreateCase,
    setShowCreateCase,
  ] = useState(false);

  const [
    customerId,
    setCustomerId,
  ] = useState("");

  const [creating, setCreating] =
    useState(false);

  const [createError, setCreateError] =
    useState("");

  const [updating, setUpdating] =
    useState("");

  const [message, setMessage] =
    useState("");

  async function handleCreateCase() {
    const id =
      customerId.trim();

    if (!id) {
      setCreateError(
        "Please enter a customer ID."
      );
      return;
    }

    setCreating(true);
    setCreateError("");

    try {
      await createCase(
        id,
        token
      );

      setCustomerId("");
      setShowCreateCase(false);

      await onRefresh();
    } catch (error) {
      setCreateError(
        error.message ||
        "Unable to create case."
      );
    } finally {
      setCreating(false);
    }
  }

  async function handleStatusChange(
    id,
    status
  ) {
    setUpdating(id);
    setMessage("");

    try {
      await updateCaseStatus(
        id,
        status,
        token
      );

      setMessage(
        `Case ${id} updated to ${status}.`
      );

      await onRefresh();
    } catch (error) {
      setMessage(
        error.message ||
        "Unable to update case."
      );
    } finally {
      setUpdating("");
    }
  }

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 12,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="space-y-5 px-5 py-7 lg:px-8"
    >

      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">

        <SectionHeader
          eyebrow="Investigation Operations"
          title="Case Intelligence"
          subtitle="Manage active investigations, case status, and risk."
          icon={BriefcaseBusiness}
        />

        <button
          onClick={() => {
            setShowCreateCase(
              true
            );
            setCreateError("");
          }}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-cyan-400/20 bg-cyan-400/[0.08] px-4 py-3 text-xs font-semibold text-cyan-300"
        >
          <span className="text-base">
            +
          </span>
          New Case
        </button>

      </div>

      {message && (
        <div className="rounded-xl border border-cyan-400/10 bg-cyan-400/[0.04] px-4 py-3 text-xs text-cyan-300">
          {message}
        </div>
      )}

      <div className="overflow-hidden rounded-2xl border border-white/[0.08] bg-white/[0.025]">

        <div className="overflow-x-auto">

          <table className="w-full min-w-[900px] text-left">

            <thead className="border-b border-white/[0.06] bg-white/[0.02]">

              <tr>

                <th className="px-5 py-4 text-[10px] uppercase tracking-[0.16em] text-slate-600">
                  Case
                </th>

                <th className="px-5 py-4 text-[10px] uppercase tracking-[0.16em] text-slate-600">
                  Customer
                </th>

                <th className="px-5 py-4 text-[10px] uppercase tracking-[0.16em] text-slate-600">
                  Status
                </th>

                <th className="px-5 py-4 text-[10px] uppercase tracking-[0.16em] text-slate-600">
                  Risk
                </th>

                <th className="px-5 py-4 text-[10px] uppercase tracking-[0.16em] text-slate-600">
                  Created
                </th>

                <th className="px-5 py-4 text-right text-[10px] uppercase tracking-[0.16em] text-slate-600">
                  Action
                </th>

              </tr>

            </thead>

            <tbody>

              {cases.map(
                (item) => {

                  const risk =
                    item.risk_level ||
                    safeJson(
                      item.risk_data
                    )
                      ?.final_risk_level ||
                    "UNKNOWN";

                  return (
                    <tr
                      key={
                        item.case_id
                      }
                      className="border-b border-white/[0.04] transition hover:bg-white/[0.025]"
                    >

                      <td className="px-5 py-4">
                        <button
                          onClick={() =>
                            onSelectCase(
                              item.case_id
                            )
                          }
                          className="font-medium text-cyan-300 hover:underline"
                        >
                          {item.case_id}
                        </button>
                      </td>

                      <td className="px-5 py-4 text-xs text-slate-400">
                        {item.customer_id}
                      </td>

                      <td className="px-5 py-4">
                        <span className="rounded-full border border-cyan-400/10 bg-cyan-400/[0.05] px-3 py-1 text-[10px] text-cyan-300">
                          {item.status}
                        </span>
                      </td>

                      <td className="px-5 py-4">
                        <RiskBadge
                          level={risk}
                        />
                      </td>

                      <td className="px-5 py-4 text-xs text-slate-500">
                        {item.created_at
                          ? new Date(
                              item.created_at
                            ).toLocaleString()
                          : "—"}
                      </td>

                      <td className="px-5 py-4 text-right">

                        {item.status ===
                          "OPEN" && (
                          <button
                            disabled={
                              updating ===
                              item.case_id
                            }
                            onClick={() =>
                              handleStatusChange(
                                item.case_id,
                                "INVESTIGATING"
                              )
                            }
                            className="rounded-lg border border-cyan-400/10 bg-cyan-400/[0.05] px-3 py-2 text-[10px] text-cyan-300 disabled:opacity-40"
                          >
                            {updating ===
                            item.case_id
                              ? "..."
                              : "Investigate"}
                          </button>
                        )}

                        {item.status ===
                          "INVESTIGATING" && (
                          <button
                            disabled={
                              updating ===
                              item.case_id
                            }
                            onClick={() =>
                              handleStatusChange(
                                item.case_id,
                                "CONTAINED"
                              )
                            }
                            className="rounded-lg border border-orange-400/10 bg-orange-400/[0.05] px-3 py-2 text-[10px] text-orange-300 disabled:opacity-40"
                          >
                            {updating ===
                            item.case_id
                              ? "..."
                              : "Contain"}
                          </button>
                        )}

                        {item.status ===
                          "CONTAINED" && (
                          <button
                            disabled={
                              updating ===
                              item.case_id
                            }
                            onClick={() =>
                              handleStatusChange(
                                item.case_id,
                                "RESOLVED"
                              )
                            }
                            className="rounded-lg border border-emerald-400/10 bg-emerald-400/[0.05] px-3 py-2 text-[10px] text-emerald-300 disabled:opacity-40"
                          >
                            {updating ===
                            item.case_id
                              ? "..."
                              : "Resolve"}
                          </button>
                        )}

                      </td>

                    </tr>
                  );
                }
              )}

            </tbody>

          </table>

        </div>

        {cases.length ===
          0 && (
          <div className="px-5 py-16 text-center text-sm text-slate-600">
            No investigation cases found.
          </div>
        )}

      </div>

      {showCreateCase && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4 backdrop-blur-md">

          <motion.div
            initial={{
              opacity: 0,
              scale: 0.96,
            }}
            animate={{
              opacity: 1,
              scale: 1,
            }}
            className="w-full max-w-md rounded-3xl border border-white/[0.10] bg-[#0b111b] p-6 shadow-2xl"
          >

            <div className="mb-6 flex items-start justify-between">

              <div>
                <div className="text-[10px] uppercase tracking-[0.22em] text-cyan-400/70">
                  Investigation Operations
                </div>

                <h3 className="mt-2 text-xl font-semibold text-white">
                  Create New Case
                </h3>
              </div>

              <button
                onClick={() =>
                  setShowCreateCase(
                    false
                  )
                }
                className="rounded-lg p-2 text-slate-500 hover:text-white"
              >
                <X size={16} />
              </button>

            </div>

            <div className="space-y-5">

              <div>

                <label className="mb-2 block text-[10px] uppercase tracking-[0.16em] text-slate-500">
                  Customer ID
                </label>

                <input
                  value={customerId}
                  onChange={(event) =>
                    setCustomerId(
                      event.target.value
                    )
                  }
                  placeholder="e.g. C002"
                  className="w-full rounded-xl border border-white/[0.08] bg-white/[0.03] px-4 py-3 text-sm text-white outline-none"
                />

              </div>

              {createError && (
                <div className="rounded-xl border border-red-400/10 bg-red-400/[0.05] px-4 py-3 text-xs text-red-300">
                  {createError}
                </div>
              )}

              <div className="flex gap-3">

                <button
                  onClick={() => {
                    setShowCreateCase(
                      false
                    );
                    setCustomerId("");
                    setCreateError(
                      ""
                    );
                  }}
                  className="flex-1 rounded-xl border border-white/[0.08] bg-white/[0.02] px-4 py-3 text-xs text-slate-400"
                >
                  Cancel
                </button>

                <button
                  onClick={
                    handleCreateCase
                  }
                  disabled={creating}
                  className="flex-1 rounded-xl border border-cyan-400/20 bg-cyan-400/[0.08] px-4 py-3 text-xs font-semibold text-cyan-300 disabled:opacity-40"
                >
                  {creating
                    ? "Creating..."
                    : "Create Case"}
                </button>

              </div>

            </div>

          </motion.div>

        </div>
      )}

    </motion.div>
  );
}
/* ============================================================
   DASHBOARD
============================================================ */

function Dashboard({
  onLogout,
}) {
  const token =
    localStorage.getItem(
      "finagent_token"
    );

  const [activeNav, setActiveNav] =
    useState("Dashboard");

  const [selectedCase, setSelectedCase] =
    useState(null);

  const [cases, setCases] =
    useState([]);

  const [metrics, setMetrics] =
    useState({
      audit_events: 0,
      security_incidents: 0,
      critical_incidents: 0,
      high_incidents: 0,
      resolved_incidents: 0,
    });

  const [posture, setPosture] =
    useState(null);

  const [incidents, setIncidents] =
    useState([]);

  const [auditEvents, setAuditEvents] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  async function loadDashboard() {
    if (!token) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const [
        casesResponse,
        metricsResponse,
        postureResponse,
        incidentsResponse,
        auditResponse,
      ] = await Promise.all([
        getCases(token),
        getSecurityMetrics(token),
        getSecurityPosture(token),
        getSecurityIncidents(token),
        getAuditEvents(token),
      ]);

      const caseData =
        unwrap(
          casesResponse
        );

      const metricsData =
        unwrap(
          metricsResponse
        );

      const postureData =
        unwrap(
          postureResponse
        );

      const incidentData =
        unwrap(
          incidentsResponse
        );

      const auditData =
        unwrap(
          auditResponse
        );

      setCases(
        caseData?.cases ||
        []
      );

      setMetrics(
        metricsData || {}
      );

      setPosture(
        postureData || null
      );

      setIncidents(
        incidentData?.incidents ||
        []
      );

      setAuditEvents(
        auditData?.audit_events ||
        []
      );
    } catch (err) {
      setError(
        err.message ||
        "Unable to load FINAGENT data."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const riskCounts =
    useMemo(() => {

      return {
        critical:
          cases.filter(
            (item) => {
              const data =
                safeJson(
                  item.risk_data
                );

              return (
                item.risk_level ===
                  "CRITICAL" ||
                data?.final_risk_level ===
                  "CRITICAL"
              );
            }
          ).length,

        high:
          cases.filter(
            (item) => {
              const data =
                safeJson(
                  item.risk_data
                );

              return (
                item.risk_level ===
                  "HIGH" ||
                data?.final_risk_level ===
                  "HIGH"
              );
            }
          ).length,

        medium:
          cases.filter(
            (item) => {
              const data =
                safeJson(
                  item.risk_data
                );

              return (
                item.risk_level ===
                  "MEDIUM" ||
                data?.final_risk_level ===
                  "MEDIUM"
              );
            }
          ).length,

        low:
          cases.filter(
            (item) => {
              const data =
                safeJson(
                  item.risk_data
                );

              return (
                item.risk_level ===
                  "LOW" ||
                data?.final_risk_level ===
                  "LOW"
              );
            }
          ).length,
      };

    }, [cases]);

  const securityStatus =
    posture?.security_status ||
    "UNKNOWN";

  const postureScore =
    securityStatus ===
    "PASS"
      ? 100
      : securityStatus ===
          "FAIL"
        ? 55
        : 0;

  const chartData = [
    {
      name: "Cases",
      value: cases.length,
    },
    {
      name: "High",
      value: riskCounts.high,
    },
    {
      name: "Medium",
      value: riskCounts.medium,
    },
    {
      name: "Critical",
      value:
        riskCounts.critical,
    },
    {
      name: "Incidents",
      value:
        metrics.security_incidents ||
        0,
    },
  ];

  return (
    <div className="min-h-screen bg-[#070b12] text-white">

      <div className="pointer-events-none fixed inset-0 overflow-hidden">

        <div className="absolute -left-40 top-[-10rem] h-[28rem] w-[28rem] rounded-full bg-cyan-500/[0.06] blur-[120px]" />

        <div className="absolute right-[-8rem] top-[10rem] h-[24rem] w-[24rem] rounded-full bg-violet-500/[0.05] blur-[120px]" />

      </div>

      <div className="relative flex min-h-screen">

        {/* SIDEBAR */}

        <aside className="hidden w-[245px] shrink-0 border-r border-white/[0.07] bg-[#090d15]/90 px-4 py-5 backdrop-blur-2xl lg:flex lg:flex-col">

          <div className="flex items-center gap-3 px-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/[0.08]">
              <ShieldAlert
                className="text-cyan-300"
                size={21}
              />
            </div>

            <div>
              <div className="text-sm font-semibold tracking-[0.16em]">
                FINAGENT
              </div>

              <div className="mt-0.5 text-[9px] uppercase tracking-[0.24em] text-slate-500">
                Crime Intelligence
              </div>
            </div>

          </div>

          <div className="mt-9 px-3 text-[9px] font-semibold uppercase tracking-[0.25em] text-slate-600">
            Command Center
          </div>

          <nav className="mt-3 space-y-1">

            {navItems.map(
              ({
                label,
                icon: Icon,
              }) => {

                const active =
                  activeNav ===
                  label;

                return (
                  <button
                    key={label}
                    onClick={() => {
                      setActiveNav(
                        label
                      );
                      setSelectedCase(
                        null
                      );
                    }}
                    className={`group flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm transition ${
                      active
                        ? "border border-cyan-400/10 bg-cyan-400/[0.08] text-cyan-300"
                        : "text-slate-500 hover:bg-white/[0.035] hover:text-slate-200"
                    }`}
                  >

                    <Icon size={17} />

                    <span>
                      {label}
                    </span>

                    {label ===
                      "Security" &&
                      incidents.length >
                        0 && (
                        <span className="ml-auto h-2 w-2 rounded-full bg-red-400" />
                      )}

                  </button>
                );
              }
            )}

          </nav>

          <div className="mt-auto">

            <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">

              <div className="flex items-center justify-between">

                <span className="text-[10px] uppercase tracking-[0.18em] text-slate-600">
                  System
                </span>

                <span className="flex items-center gap-1.5 text-[10px] text-emerald-400">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  ONLINE
                </span>

              </div>

              <div className="mt-3 text-sm text-slate-300">
                Security posture
              </div>

              <div className="mt-3 flex items-end justify-between">

                <span className="text-2xl font-semibold">
                  {securityStatus}
                </span>

                <ShieldCheck
                  size={18}
                  className="text-emerald-300"
                />

              </div>

            </div>

            <button
              onClick={onLogout}
              className="mt-3 flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-slate-600 transition hover:bg-white/[0.03] hover:text-red-300"
            >
              <LogOut size={16} />
              Logout
            </button>

          </div>

        </aside>


        {/* MAIN */}

        <main className="min-w-0 flex-1">

          <header className="sticky top-0 z-20 flex h-[72px] items-center justify-between border-b border-white/[0.07] bg-[#070b12]/80 px-5 backdrop-blur-xl lg:px-8">

            <div className="flex items-center gap-3">

              <div className="relative hidden md:block">

                <Search
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600"
                  size={16}
                />

                <input
                  placeholder="Search customers, cases..."
                  className="h-10 w-[320px] rounded-xl border border-white/[0.07] bg-white/[0.025] pl-10 pr-4 text-xs text-slate-300 outline-none placeholder:text-slate-700"
                />

              </div>

              <div className="flex items-center gap-2 rounded-full border border-cyan-400/10 bg-cyan-400/[0.05] px-3 py-1.5 text-[10px] uppercase tracking-[0.16em] text-cyan-300">
                <Activity size={12} />
                Live
              </div>

            </div>

            <div className="flex items-center gap-3">

              <button
                onClick={() =>
                  setActiveNav(
                    "Security"
                  )
                }
                className="relative rounded-xl border border-white/[0.07] bg-white/[0.025] p-2.5 text-slate-500 hover:text-white"
              >

                <Bell size={17} />

                {incidents.length >
                  0 && (
                  <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-red-400" />
                )}

              </button>

              <div className="hidden h-8 w-px bg-white/[0.07] sm:block" />

              <div className="flex items-center gap-2">

                <div className="flex h-9 w-9 items-center justify-center rounded-full border border-cyan-400/20 bg-cyan-400/[0.08] text-xs font-semibold text-cyan-300">
                  A
                </div>

                <div className="hidden sm:block">

                  <div className="text-xs font-medium">
                    Admin
                  </div>

                  <div className="text-[9px] uppercase tracking-[0.15em] text-slate-600">
                    Security Analyst
                  </div>

                </div>

                <ChevronDown
                  size={14}
                  className="text-slate-600"
                />

              </div>

            </div>

          </header>


          {error && (
            <div className="mx-5 mt-6 rounded-xl border border-red-500/20 bg-red-500/[0.06] px-4 py-3 text-xs text-red-300 lg:mx-8">
              {error}
            </div>
          )}


          {selectedCase ? (
            <CaseDetails
              caseId={selectedCase}
              token={token}
              onBack={() =>
                setSelectedCase(
                  null
                )
              }
              onRefresh={
                loadDashboard
              }
            />
          ) : activeNav ===
            "Cases" ? (

            <CasesView
              cases={cases}
              token={token}
              onRefresh={
                loadDashboard
              }
              onSelectCase={
                setSelectedCase
              }
            />

          ) : activeNav ===
            "Customers" ? (

            <CustomerView
              token={token}
            />

          ) : activeNav ===
            "Evidence" ? (

            <EvidenceView
              token={token}
            />

          ) : activeNav ===
            "Reports" ? (

            <ReportsView
              token={token}
            />

          ) : activeNav ===
            "Network" ? (

            <NetworkView
              token={token}
            />

          ) : activeNav ===
            "Security" ? (

            <SecurityView
              metrics={metrics}
              posture={posture}
              incidents={incidents}
              loading={loading}
              onRefresh={
                loadDashboard
              }
            />

          ) : activeNav ===
            "Audit" ? (

            <AuditView
              auditEvents={
                auditEvents
              }
              loading={loading}
            />

          ) : (

            /* ==================================================
               DASHBOARD HOME
            ================================================== */

            <div className="px-5 py-7 lg:px-8">

              <motion.div
                initial={{
                  opacity: 0,
                  y: 10,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                className="mb-8"
              >

                <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-end">

                  <div>

                    <div className="mb-3 flex items-center gap-2 text-[10px] uppercase tracking-[0.25em] text-slate-600">
                      <Sparkles
                        size={12}
                        className="text-cyan-300"
                      />
                      Intelligence Command Center
                    </div>

                    <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
                      Welcome,{" "}
                      <span className="text-slate-400">
                        Analyst.
                      </span>
                    </h1>

                    <p className="mt-2 max-w-2xl text-sm text-slate-500">
                      Real-time visibility into financial crime investigations,
                      case activity, and platform security.
                    </p>

                  </div>

                  <button
                    onClick={
                      loadDashboard
                    }
                    disabled={
                      loading
                    }
                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-cyan-300/20 bg-cyan-300/[0.08] px-4 py-2.5 text-xs font-medium text-cyan-200 disabled:opacity-40"
                  >
                    <RefreshCw
                      size={14}
                      className={
                        loading
                          ? "animate-spin"
                          : ""
                      }
                    />

                    Refresh Intelligence
                  </button>

                </div>

              </motion.div>


              {/* STATS */}

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

                <StatCard
                  icon={
                    BriefcaseBusiness
                  }
                  label="Total Cases"
                  value={
                    loading
                      ? "—"
                      : cases.length
                  }
                  meta="live"
                  accent="text-cyan-300"
                />

                <StatCard
                  icon={
                    AlertTriangle
                  }
                  label="High Risk"
                  value={
                    loading
                      ? "—"
                      : riskCounts.high
                  }
                  meta="cases"
                  accent="text-orange-300"
                />

                <StatCard
                  icon={
                    ShieldAlert
                  }
                  label="Critical"
                  value={
                    loading
                      ? "—"
                      : metrics.critical_incidents ||
                        riskCounts.critical
                  }
                  meta="attention"
                  accent="text-red-300"
                />

                <StatCard
                  icon={
                    ShieldCheck
                  }
                  label="Security"
                  value={
                    loading
                      ? "—"
                      : `${postureScore}%`
                  }
                  meta={
                    securityStatus
                  }
                  accent="text-emerald-300"
                />

              </div>


              {/* CHART + CASES */}

              <div className="mt-5 grid gap-5 xl:grid-cols-[1.45fr_1fr]">

                <section className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5">

                  <div className="flex items-center justify-between">

                    <div>
                      <div className="text-sm font-medium">
                        Intelligence activity
                      </div>

                      <div className="mt-1 text-xs text-slate-600">
                        Current platform activity
                      </div>
                    </div>

                    <BarChart3
                      size={16}
                      className="text-slate-600"
                    />

                  </div>

                  <div className="mt-6 h-[270px]">

                    <ResponsiveContainer
                      width="100%"
                      height="100%"
                    >

                      <AreaChart
                        data={
                          chartData
                        }
                      >

                        <defs>

                          <linearGradient
                            id="riskFill"
                            x1="0"
                            y1="0"
                            x2="0"
                            y2="1"
                          >

                            <stop
                              offset="0%"
                              stopColor="#22d3ee"
                              stopOpacity={
                                0.18
                              }
                            />

                            <stop
                              offset="100%"
                              stopColor="#22d3ee"
                              stopOpacity={
                                0
                              }
                            />

                          </linearGradient>

                        </defs>

                        <CartesianGrid
                          stroke="#ffffff"
                          strokeOpacity={
                            0.05
                          }
                          vertical={
                            false
                          }
                        />

                        <XAxis
                          dataKey="name"
                          axisLine={
                            false
                          }
                          tickLine={
                            false
                          }
                          tick={{
                            fill: "#475569",
                            fontSize: 10,
                          }}
                        />

                        <YAxis
                          axisLine={
                            false
                          }
                          tickLine={
                            false
                          }
                          tick={{
                            fill: "#475569",
                            fontSize: 10,
                          }}
                          width={28}
                        />

                        <Tooltip
                          contentStyle={{
                            background:
                              "#0c111b",
                            border:
                              "1px solid rgba(255,255,255,0.08)",
                            borderRadius:
                              "12px",
                            color:
                              "#fff",
                            fontSize:
                              "11px",
                          }}
                        />

                        <Area
                          type="monotone"
                          dataKey="value"
                          stroke="#22d3ee"
                          strokeWidth={
                            2
                          }
                          fill="url(#riskFill)"
                        />

                      </AreaChart>

                    </ResponsiveContainer>

                  </div>

                </section>


                <section className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5">

                  <div className="flex items-center justify-between">

                    <div>
                      <div className="text-sm font-medium">
                        Live cases
                      </div>

                      <div className="mt-1 text-xs text-slate-600">
                        Latest investigations
                      </div>
                    </div>

                    <BriefcaseBusiness
                      size={16}
                      className="text-slate-600"
                    />

                  </div>

                  <div className="mt-5 space-y-2">

                    {cases
                      .slice(
                        0,
                        5
                      )
                      .map(
                        (
                          item
                        ) => (
                          <button
                            key={
                              item.case_id
                            }
                            onClick={() =>
                              setSelectedCase(
                                item.case_id
                              )
                            }
                            className="w-full rounded-xl border border-white/[0.05] bg-white/[0.018] p-3.5 text-left"
                          >

                            <div className="flex items-start justify-between gap-3">

                              <div>

                                <div className="text-xs font-medium text-slate-200">
                                  {
                                    item.case_id
                                  }
                                </div>

                                <div className="mt-1 text-[10px] text-slate-600">
                                  {
                                    item.customer_id
                                  }
                                </div>

                              </div>

                              <RiskBadge
                                level={
                                  item.risk_level ||
                                  safeJson(
                                    item.risk_data
                                  )
                                    ?.final_risk_level
                                }
                              />

                            </div>

                            <div className="mt-3 flex items-center justify-between">

                              <span className="text-[10px] uppercase tracking-[0.16em] text-slate-600">
                                {
                                  item.status
                                }
                              </span>

                              <ArrowUpRight
                                size={
                                  14
                                }
                                className="text-slate-700"
                              />

                            </div>

                          </button>
                        )
                      )}

                    {!loading &&
                      cases.length ===
                        0 && (
                        <div className="rounded-xl border border-dashed border-white/[0.07] px-4 py-8 text-center text-xs text-slate-600">
                          No investigation cases found.
                        </div>
                      )}

                  </div>

                </section>

              </div>


              {/* LOWER CARDS */}

              <div className="mt-5 grid gap-5 lg:grid-cols-3">

                <section className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5">

                  <div className="flex items-center gap-2 text-xs font-medium">
                    <ShieldCheck
                      size={15}
                      className="text-emerald-300"
                    />
                    Security posture
                  </div>

                  <div className="mt-5 flex items-center gap-5">

                    <div className="relative flex h-20 w-20 items-center justify-center rounded-full border-4 border-emerald-400/20">

                      <div className="text-lg font-semibold">
                        {
                          postureScore
                        }
                        %
                      </div>

                      <div className="absolute inset-[-4px] rounded-full border-4 border-transparent border-t-emerald-400/80" />

                    </div>

                    <div>

                      <div className="text-sm text-white">
                        {
                          securityStatus
                        }
                      </div>

                      <div className="mt-1 text-xs text-slate-600">
                        Live security assessment
                      </div>

                    </div>

                  </div>

                </section>


                <section className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5">

                  <div className="flex items-center gap-2 text-xs font-medium">

                    <AlertTriangle
                      size={15}
                      className="text-orange-300"
                    />

                    Incident center

                  </div>

                  <div className="mt-5 grid grid-cols-2 gap-3">

                    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3">

                      <div className="text-xl font-semibold">
                        {
                          metrics.security_incidents ||
                          0
                        }
                      </div>

                      <div className="mt-1 text-[9px] uppercase tracking-[0.16em] text-slate-600">
                        Total incidents
                      </div>

                    </div>

                    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3">

                      <div className="text-xl font-semibold text-red-300">
                        {
                          metrics.critical_incidents ||
                          0
                        }
                      </div>

                      <div className="mt-1 text-[9px] uppercase tracking-[0.16em] text-slate-600">
                        Critical
                      </div>

                    </div>

                  </div>

                </section>


                <section className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5">

                  <div className="flex items-center gap-2 text-xs font-medium">

                    <Fingerprint
                      size={15}
                      className="text-cyan-300"
                    />

                    Audit integrity

                  </div>

                  <div className="mt-5 flex items-center justify-between">

                    <div>

                      <div className="text-lg font-semibold text-emerald-300">
                        VERIFIED
                      </div>

                      <div className="mt-1 text-xs text-slate-600">
                        {
                          auditEvents.length
                        } recent events loaded
                      </div>

                    </div>

                    <Fingerprint
                      size={21}
                      className="text-emerald-300"
                    />

                  </div>

                </section>

              </div>

            </div>
          )}

        </main>

      </div>

    </div>
  );
}


/* ============================================================
   APP
============================================================ */

function App() {
  const [
    authenticated,
    setAuthenticated,
  ] = useState(() =>
    Boolean(
      localStorage.getItem(
        "finagent_token"
      )
    )
  );

  function handleLogin() {
    setAuthenticated(true);
  }

  function handleLogout() {
    localStorage.removeItem(
      "finagent_token"
    );

    localStorage.removeItem(
      "finagent_role"
    );

    setAuthenticated(false);
  }

  if (!authenticated) {
    return (
      <LoginScreen
        onLogin={
          handleLogin
        }
      />
    );
  }

  return (
    <Dashboard
      onLogout={
        handleLogout
      }
    />
  );
}

export default App;