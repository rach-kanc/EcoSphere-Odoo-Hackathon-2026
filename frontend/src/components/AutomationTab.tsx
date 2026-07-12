import React, { useEffect, useState } from "react";
import { Plus, Trash2, RefreshCw, Zap, AlertTriangle, Cpu } from "lucide-react";
import { autoCalculationApi, MappingPayload } from "../api/autoCalculation";
import { EmissionFactorMapping, PendingAutoCalculation, SourceType } from "../types";

const SOURCE_TYPES: SourceType[] = ["purchase", "manufacturing", "expense", "fleet"];

const EMPTY_MAPPING: MappingPayload = {
  source_type: "fleet",
  match_key: "",
  factor_code: "",
};

export default function AutomationTab() {
  const [enabled, setEnabled] = useState(false);
  const [mappings, setMappings] = useState<EmissionFactorMapping[]>([]);
  const [pending, setPending] = useState<PendingAutoCalculation[]>([]);
  const [loading, setLoading] = useState(true);
  const [toggleBusy, setToggleBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<MappingPayload>(EMPTY_MAPPING);
  const [formError, setFormError] = useState<string | null>(null);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [enabledData, mappingsData, pendingData] = await Promise.all([
        autoCalculationApi.getEnabled(),
        autoCalculationApi.listMappings(),
        autoCalculationApi.listPending(),
      ]);
      setEnabled(enabledData.enabled);
      setMappings(mappingsData);
      setPending(pendingData);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to load automation settings");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  const handleToggle = async () => {
    setToggleBusy(true);
    try {
      const result = await autoCalculationApi.setEnabled(!enabled);
      setEnabled(result.enabled);
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    } finally {
      setToggleBusy(false);
    }
  };

  const handleCreateMapping = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    try {
      await autoCalculationApi.createMapping(form);
      setForm(EMPTY_MAPPING);
      loadAll();
    } catch (err: any) {
      setFormError(err.message || "Failed to create mapping");
    }
  };

  const handleDeleteMapping = async (mapping: EmissionFactorMapping) => {
    if (!window.confirm(`Delete mapping ${mapping.source_type}/${mapping.match_key}?`)) return;
    try {
      await autoCalculationApi.deleteMapping(mapping.id);
      loadAll();
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleRetry = async (item: PendingAutoCalculation) => {
    try {
      const outcome = await autoCalculationApi.retryPending(item.id);
      if (outcome.status === "flagged" || outcome.status === "disabled") {
        alert(outcome.detail);
      }
      loadAll();
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="text-gray-400 p-8 flex items-center justify-center animate-pulse">
        Loading automation engine...
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Auto Emission Calculation</h2>
        <p className="text-gray-400 text-sm mt-0.5">
          Automatically generate carbon transactions from source records using mapped emission factors.
        </p>
      </div>

      {error && (
        <div className="text-xs text-rose-400 bg-rose-950/30 border border-rose-500/30 rounded-lg px-3 py-2">
          {error}
        </div>
      )}

      {/* Toggle */}
      <div className="glass-card p-6 rounded-2xl flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="bg-emerald-950 p-3 rounded-xl border border-emerald-500/30">
            <Cpu className="w-6 h-6 text-emerald-400" />
          </div>
          <div>
            <h3 className="font-bold text-base">Auto-calculation engine</h3>
            <p className="text-sm text-gray-400">
              {enabled
                ? "Active — new source records are converted automatically."
                : "Disabled — ingested source records are ignored."}
            </p>
          </div>
        </div>
        <button
          onClick={handleToggle}
          disabled={toggleBusy}
          className={`relative inline-flex h-7 w-12 items-center rounded-full transition-colors disabled:opacity-50 ${
            enabled ? "bg-emerald-500" : "bg-slate-700"
          }`}
          aria-pressed={enabled}
        >
          <span
            className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform ${
              enabled ? "translate-x-6" : "translate-x-1"
            }`}
          />
        </button>
      </div>

      {/* Pending review queue */}
      <div className="glass-card rounded-2xl overflow-hidden">
        <div className="p-6 border-b border-brand-border flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">
            Flagged for Review ({pending.length})
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950 text-gray-400 text-xs font-bold uppercase">
              <tr>
                <th className="p-4">Source</th>
                <th className="p-4">Match Key</th>
                <th className="p-4">Quantity</th>
                <th className="p-4">Date</th>
                <th className="p-4">Reason</th>
                <th className="p-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-brand-border">
              {pending.length === 0 && (
                <tr>
                  <td colSpan={6} className="p-6 text-center text-gray-500">
                    No records awaiting review.
                  </td>
                </tr>
              )}
              {pending.map((item) => (
                <tr key={item.id} className="hover:bg-slate-900/30 transition-colors">
                  <td className="p-4 capitalize font-semibold">
                    {item.source_type}
                    <span className="text-gray-500 font-normal"> #{item.source_record_id}</span>
                  </td>
                  <td className="p-4 font-mono text-xs text-gray-400">{item.match_key}</td>
                  <td className="p-4 text-gray-300">{item.quantity}</td>
                  <td className="p-4 text-gray-400">{item.transaction_date}</td>
                  <td className="p-4 text-xs text-amber-400/80 max-w-xs">{item.reason}</td>
                  <td className="p-4 text-right">
                    <button
                      onClick={() => handleRetry(item)}
                      title="Retry"
                      className="inline-flex items-center gap-1.5 text-xs bg-emerald-950 text-emerald-400 border border-emerald-500/20 px-3 py-1.5 rounded-lg font-bold hover:bg-emerald-900 transition-colors"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                      Retry
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Mapping configuration */}
      <div className="glass-card rounded-2xl overflow-hidden">
        <div className="p-6 border-b border-brand-border flex items-center gap-2">
          <Zap className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">
            Emission Factor Mappings
          </h3>
        </div>

        {/* Create form */}
        <form onSubmit={handleCreateMapping} className="p-6 border-b border-brand-border space-y-4">
          {formError && (
            <div className="text-xs text-rose-400 bg-rose-950/30 border border-rose-500/30 rounded-lg px-3 py-2">
              {formError}
            </div>
          )}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-400 uppercase tracking-widest">
                Source Type
              </label>
              <select
                value={form.source_type}
                onChange={(e) => setForm({ ...form, source_type: e.target.value as SourceType })}
                className="w-full bg-slate-900 border border-brand-border px-3 py-2 rounded-xl text-sm focus:outline-none focus:border-emerald-500/50"
              >
                {SOURCE_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-400 uppercase tracking-widest">
                Match Key
              </label>
              <input
                type="text"
                value={form.match_key}
                onChange={(e) => setForm({ ...form, match_key: e.target.value })}
                placeholder="e.g. TRUCK-01, SKU-42"
                className="w-full bg-slate-900 border border-brand-border px-3 py-2 rounded-xl text-sm focus:outline-none focus:border-emerald-500/50"
                required
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-400 uppercase tracking-widest">
                Factor Code
              </label>
              <input
                type="text"
                value={form.factor_code}
                onChange={(e) => setForm({ ...form, factor_code: e.target.value })}
                placeholder="e.g. fuel.diesel"
                className="w-full bg-slate-900 border border-brand-border px-3 py-2 rounded-xl text-sm focus:outline-none focus:border-emerald-500/50"
                required
              />
            </div>
            <div className="flex items-end">
              <button
                type="submit"
                className="w-full bg-gradient-emerald text-white py-2 rounded-xl text-sm font-semibold hover:shadow-emerald-950/20 hover:shadow-lg transition-all flex items-center justify-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add Mapping
              </button>
            </div>
          </div>
        </form>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950 text-gray-400 text-xs font-bold uppercase">
              <tr>
                <th className="p-4">Source Type</th>
                <th className="p-4">Match Key</th>
                <th className="p-4">Factor Code</th>
                <th className="p-4">Status</th>
                <th className="p-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-brand-border">
              {mappings.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-6 text-center text-gray-500">
                    No mappings configured yet.
                  </td>
                </tr>
              )}
              {mappings.map((m) => (
                <tr key={m.id} className="hover:bg-slate-900/30 transition-colors">
                  <td className="p-4 capitalize font-semibold">{m.source_type}</td>
                  <td className="p-4 font-mono text-xs text-gray-400">{m.match_key}</td>
                  <td className="p-4 font-mono text-xs text-emerald-400">{m.factor_code}</td>
                  <td className="p-4">
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${
                        m.is_active
                          ? "bg-emerald-950/40 text-emerald-400 border-emerald-500/20"
                          : "bg-slate-900 text-gray-500 border-brand-border"
                      }`}
                    >
                      {m.is_active ? "ACTIVE" : "INACTIVE"}
                    </span>
                  </td>
                  <td className="p-4 text-right">
                    <button
                      onClick={() => handleDeleteMapping(m)}
                      title="Delete"
                      className="p-1.5 rounded-lg text-gray-400 hover:text-rose-400 hover:bg-slate-800 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
