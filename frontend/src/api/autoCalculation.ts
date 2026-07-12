import { EmissionFactorMapping, PendingAutoCalculation, SourceType } from "../types";

const API_BASE = "http://localhost:8000/api/v1";

async function fetchApi<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "API request failed");
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json();
}

export interface MappingPayload {
  source_type: SourceType;
  match_key: string;
  factor_code: string;
  is_active?: boolean;
}

export interface IngestOutcome {
  status: "created" | "updated" | "flagged" | "disabled";
  detail: string;
  carbon_transaction_id: number | null;
  pending_id: number | null;
}

export const autoCalculationApi = {
  // Settings toggle
  getEnabled: () => fetchApi<{ enabled: boolean }>("/settings/auto-calculation"),
  setEnabled: (enabled: boolean) =>
    fetchApi<{ enabled: boolean }>("/settings/auto-calculation", {
      method: "PUT",
      body: JSON.stringify({ enabled }),
    }),

  // Mapping configuration
  listMappings: () => fetchApi<EmissionFactorMapping[]>("/emission-factor-mappings"),
  createMapping: (payload: MappingPayload) =>
    fetchApi<EmissionFactorMapping>("/emission-factor-mappings", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  deleteMapping: (id: number) =>
    fetchApi<void>(`/emission-factor-mappings/${id}`, { method: "DELETE" }),

  // Pending review queue
  listPending: () =>
    fetchApi<PendingAutoCalculation[]>("/auto-calculation/pending?status=pending"),
  retryPending: (id: number) =>
    fetchApi<IngestOutcome>(`/auto-calculation/pending/${id}/retry`, { method: "POST" }),
};
