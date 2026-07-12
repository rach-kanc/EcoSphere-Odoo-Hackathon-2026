import { CarbonTransaction, DepartmentCarbonSummary, SourceType, TransactionStatus } from "../types";

const API_BASE = "http://localhost:8000/api/v1/carbon-transactions";

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
  return response.json();
}

export interface CarbonTransactionManualPayload {
  department_id?: number;
  source_type: SourceType;
  emission_factor_id: number;
  quantity: number;
  transaction_date: string;
  source_reference?: string;
  notes?: string;
}

export const carbonTransactionsApi = {
  list: (filters?: {
    department_id?: number;
    source_type?: SourceType;
    status?: TransactionStatus;
    date_from?: string;
    date_to?: string;
  }) => {
    const params = new URLSearchParams();
    if (filters?.department_id) params.set("department_id", String(filters.department_id));
    if (filters?.source_type) params.set("source_type", filters.source_type);
    if (filters?.status) params.set("status", filters.status);
    if (filters?.date_from) params.set("date_from", filters.date_from);
    if (filters?.date_to) params.set("date_to", filters.date_to);
    const query = params.toString();
    return fetchApi<CarbonTransaction[]>(query ? `?${query}` : "");
  },
  createManual: (payload: CarbonTransactionManualPayload) =>
    fetchApi<CarbonTransaction>("", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  summaryByDepartment: (filters?: {
    source_type?: SourceType;
    date_from?: string;
    date_to?: string;
  }) => {
    const params = new URLSearchParams();
    if (filters?.source_type) params.set("source_type", filters.source_type);
    if (filters?.date_from) params.set("date_from", filters.date_from);
    if (filters?.date_to) params.set("date_to", filters.date_to);
    const query = params.toString();
    return fetchApi<DepartmentCarbonSummary[]>(
      `/summary/by-department${query ? `?${query}` : ""}`
    );
  },
};
