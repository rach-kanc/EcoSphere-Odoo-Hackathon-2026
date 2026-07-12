import React, { useEffect, useState } from "react";
import { Building2 } from "lucide-react";
import { carbonTransactionsApi } from "../api/carbonTransactions";
import { CarbonTransaction, DepartmentCarbonSummary, SourceType } from "../types";

const SOURCE_TYPES: SourceType[] = ["fleet", "manufacturing", "purchase", "expense"];

export default function DepartmentCarbonTrackingTab() {
  const [summary, setSummary] = useState<DepartmentCarbonSummary[]>([]);
  const [sourceType, setSourceType] = useState<SourceType | "">("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [loading, setLoading] = useState(true);

  const [drillDownDept, setDrillDownDept] = useState<DepartmentCarbonSummary | null>(null);
  const [drillDownTxns, setDrillDownTxns] = useState<CarbonTransaction[]>([]);

  const filters = {
    source_type: sourceType || undefined,
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
  };

  const load = () => {
    setLoading(true);
    carbonTransactionsApi
      .summaryByDepartment(filters)
      .then(setSummary)
      .catch((err) => console.error("Failed to load department summary", err))
      .finally(() => setLoading(false));
  };

  useEffect(load, [sourceType, dateFrom, dateTo]);

  const openDrillDown = (dept: DepartmentCarbonSummary) => {
    setDrillDownDept(dept);
    carbonTransactionsApi
      .list({ department_id: dept.department_id ?? undefined, ...filters })
      .then(setDrillDownTxns)
      .catch((err) => console.error("Failed to load transactions", err));
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Department Carbon Tracking</h2>
        <p className="text-gray-400 text-sm mt-0.5">
          Carbon transaction totals aggregated by department.
        </p>
      </div>

      <div className="glass-card p-4 rounded-2xl flex flex-wrap gap-4 items-center">
        <select
          value={sourceType}
          onChange={(e) => setSourceType(e.target.value as SourceType | "")}
          className="bg-slate-900 border border-brand-border px-3 py-1.5 rounded-lg text-sm"
        >
          <option value="">All Source Types</option>
          {SOURCE_TYPES.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
        <input
          type="date"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
          className="bg-slate-900 border border-brand-border px-3 py-1.5 rounded-lg text-sm"
        />
        <span className="text-gray-500 text-sm">to</span>
        <input
          type="date"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
          className="bg-slate-900 border border-brand-border px-3 py-1.5 rounded-lg text-sm"
        />
      </div>

      <div className="glass-card rounded-2xl overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-950 text-gray-400 text-xs font-bold uppercase">
            <tr>
              <th className="p-4">Department</th>
              <th className="p-4">Transactions</th>
              <th className="p-4">Total CO2e (kg)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-brand-border">
            {loading && (
              <tr>
                <td colSpan={3} className="p-6 text-center text-gray-500">
                  Loading...
                </td>
              </tr>
            )}
            {!loading && summary.length === 0 && (
              <tr>
                <td colSpan={3} className="p-6 text-center text-gray-500">
                  No carbon transactions found.
                </td>
              </tr>
            )}
            {summary.map((row) => (
              <tr
                key={row.department_id ?? "unassigned"}
                onClick={() => openDrillDown(row)}
                className="hover:bg-slate-900/30 transition-colors cursor-pointer"
              >
                <td className="p-4 font-semibold flex items-center gap-2">
                  <Building2 className="w-3.5 h-3.5 text-emerald-400" />
                  {row.department_name ?? "Unassigned"}
                </td>
                <td className="p-4 text-gray-300">{row.transaction_count}</td>
                <td className="p-4 font-bold text-emerald-400">
                  {row.total_co2e.toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {drillDownDept && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card w-full max-w-2xl rounded-2xl overflow-hidden shadow-2xl max-h-[80vh] flex flex-col">
            <div className="p-6 border-b border-brand-border flex justify-between items-center bg-slate-950/60">
              <h3 className="font-bold text-lg">
                {drillDownDept.department_name ?? "Unassigned"} — Transactions
              </h3>
              <button
                onClick={() => setDrillDownDept(null)}
                className="text-gray-400 hover:text-white text-lg font-bold"
              >
                &times;
              </button>
            </div>
            <div className="overflow-y-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-950 text-gray-400 text-xs font-bold uppercase sticky top-0">
                  <tr>
                    <th className="p-3">Date</th>
                    <th className="p-3">Source</th>
                    <th className="p-3">Quantity</th>
                    <th className="p-3">CO2e</th>
                    <th className="p-3">Created By</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-brand-border">
                  {drillDownTxns.map((t) => (
                    <tr key={t.id}>
                      <td className="p-3 text-gray-400">{t.transaction_date}</td>
                      <td className="p-3 capitalize">{t.source_type}</td>
                      <td className="p-3">{t.quantity}</td>
                      <td className="p-3 font-semibold text-emerald-400">{t.co2e}</td>
                      <td className="p-3 text-gray-400">{t.created_by}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
