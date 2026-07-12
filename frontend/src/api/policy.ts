/**
 * Policy API client.
 *
 * Mirrors the FastAPI routes in backend/app/api/v1/policies.py.
 * All endpoints require a user_id query param until JWT auth is wired up.
 */
import { ESGPolicy, PolicyAcknowledgement, PolicyStatus, PolicyType } from "../types";

const API_BASE = "http://localhost:8000/api/v1/policies";

// ── shared fetch helper ────────────────────────────────────────────────────
async function fetchApi<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed: ${response.status}`);
  }

  return response.json();
}

// ── filter types ───────────────────────────────────────────────────────────
export interface ListPoliciesParams {
  type?: PolicyType;
  status?: PolicyStatus;
}

// ── policy API ─────────────────────────────────────────────────────────────
export const policyApi = {
  /**
   * GET /policies
   * Returns all policies, optionally filtered by type and/or status.
   */
  listPolicies: (params: ListPoliciesParams = {}): Promise<ESGPolicy[]> => {
    const query = new URLSearchParams();
    if (params.type)   query.set("type", params.type);
    if (params.status) query.set("status", params.status);
    const qs = query.toString();
    return fetchApi<ESGPolicy[]>(`${API_BASE}${qs ? `?${qs}` : ""}`);
  },

  /**
   * GET /policies/pending?user_id=...
   * Returns active policies not yet acknowledged by the given user.
   */
  getPendingPolicies: (userId: number): Promise<ESGPolicy[]> =>
    fetchApi<ESGPolicy[]>(`${API_BASE}/pending?user_id=${userId}`),

  /**
   * GET /policies/:id
   */
  getPolicy: (policyId: number): Promise<ESGPolicy> =>
    fetchApi<ESGPolicy>(`${API_BASE}/${policyId}`),

  /**
   * POST /policies/:id/acknowledge?user_id=...
   * Records a digital signature and awards +100 XP on the backend.
   */
  acknowledgePolicy: (
    policyId: number,
    userId: number,
    signatureText: string,
  ): Promise<PolicyAcknowledgement> =>
    fetchApi<PolicyAcknowledgement>(
      `${API_BASE}/${policyId}/acknowledge?user_id=${userId}`,
      {
        method: "POST",
        body: JSON.stringify({ signature_text: signatureText }),
      },
    ),
};
