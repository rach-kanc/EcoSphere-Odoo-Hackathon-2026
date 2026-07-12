import { EnvironmentalGoal } from "../types";

const API_BASE = "http://localhost:8000/api/v1/environmental-goals";

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

export const environmentalGoalsApi = {
  list: (filters?: { department_id?: number; refresh_actuals?: boolean }) => {
    const params = new URLSearchParams();
    if (filters?.department_id) params.set("department_id", String(filters.department_id));
    if (filters?.refresh_actuals !== undefined) {
      params.set("refresh_actuals", String(filters.refresh_actuals));
    }
    const query = params.toString();
    return fetchApi<EnvironmentalGoal[]>(query ? `?${query}` : "");
  },
  refresh: (goalId: number) => fetchApi<EnvironmentalGoal>(`/${goalId}/refresh`, { method: "POST" }),
};
