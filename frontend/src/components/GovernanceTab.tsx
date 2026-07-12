import React, { useState } from "react";
import {
  Scale,
  ShieldAlert,
  Check,
  FileCheck,
  CheckCircle2,
} from "lucide-react";

import { ESGPolicy, ComplianceIssue, User } from "../types";

// --- POLICY TYPE DISPLAY HELPER ---
const POLICY_TYPE_META: Record<string, { label: string; color: string }> = {
  environmental:   { label: "Environmental",   color: "bg-emerald-950/50 text-emerald-400 border-emerald-500/20" },
  anti_bribery:    { label: "Anti-Bribery",    color: "bg-rose-950/50 text-rose-400 border-rose-500/20" },
  data_privacy:    { label: "Data Privacy",    color: "bg-sky-950/50 text-sky-400 border-sky-500/20" },
  code_of_conduct: { label: "Code of Conduct", color: "bg-violet-950/50 text-violet-400 border-violet-500/20" },
  health_safety:   { label: "Health & Safety", color: "bg-amber-950/50 text-amber-400 border-amber-500/20" },
  other:           { label: "General",          color: "bg-slate-800 text-gray-400 border-brand-border" },
};

interface GovernanceTabProps {
  user: User;
  policies: ESGPolicy[];
  issues: ComplianceIssue[];
  acknowledgedPolicies: Record<number, boolean>;
  onPolicyAck: (policyId: number) => void;
  onUserXpUpdate: (xp: number) => void;
}

export default function GovernanceTab({
  user,
  policies,
  issues,
  acknowledgedPolicies,
  onPolicyAck,
  onUserXpUpdate,
}: GovernanceTabProps) {
  // --- Local modal state (self-contained) ---
  const [selectedPolicy, setSelectedPolicy] = useState<ESGPolicy | null>(null);
  const [signatureName, setSignatureName] = useState("");
  const [signatureChecked, setSignatureChecked] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");

  const openModal = (policy: ESGPolicy) => {
    setSelectedPolicy(policy);
    setSignatureName("");
    setSignatureChecked(false);
  };

  const closeModal = () => setSelectedPolicy(null);

  const handleSign = () => {
    if (!selectedPolicy) return;
    if (!signatureChecked) return;
    if (signatureName.trim().toLowerCase() !== user.full_name.toLowerCase()) return;

    onPolicyAck(selectedPolicy.id);
    onUserXpUpdate(100);

    const title = selectedPolicy.title;
    closeModal();

    setToastMessage(`Policy "${title}" successfully acknowledged! +100 XP awarded.`);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 4000);
  };

  const isSignBtnDisabled =
    !signatureChecked ||
    signatureName.trim().toLowerCase() !== user.full_name.toLowerCase();

  return (
    <>
      {/* ── TAB CONTENT ── */}
      <div className="space-y-8 animate-fade-in">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Corporate Governance &amp; Audits</h2>
          <p className="text-gray-400 text-sm mt-0.5">
            Policy compliance tracking, mandatory sign-offs, and audit resolution ledgers.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* ── Policy Sign-Off List ── */}
          <div className="space-y-6 lg:col-span-2">
            <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">
              Awaiting Sign-Offs
            </h3>
            <div className="space-y-4">
              {policies.map((p) => {
                const isAcked = !!acknowledgedPolicies[p.id];
                const typeMeta = POLICY_TYPE_META[p.type] || POLICY_TYPE_META.other;
                return (
                  <div
                    key={p.id}
                    className="glass-card p-6 rounded-2xl flex justify-between items-start gap-4"
                  >
                    <div className="space-y-3">
                      <div className="flex items-center flex-wrap gap-2">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${typeMeta.color}`}>
                          {typeMeta.label}
                        </span>
                        <span className="text-[10px] bg-slate-800 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded-full font-bold">
                          v{p.version}
                        </span>
                        <span className="text-xs text-gray-500 font-medium">
                          Effective: {p.effective_date}
                        </span>
                      </div>
                      <h4 className="font-bold text-base">{p.title}</h4>
                      <p className="text-sm text-gray-400 leading-relaxed">{p.content}</p>
                    </div>

                    <button
                      disabled={isAcked}
                      onClick={() => openModal(p)}
                      className={`shrink-0 flex items-center gap-1.5 px-4 py-2.5 rounded-xl border text-sm font-semibold transition-all duration-300 ${
                        isAcked
                          ? "bg-emerald-950/40 text-emerald-400 border-emerald-500/30 cursor-not-allowed opacity-80"
                          : "bg-gradient-indigo text-white border-transparent shadow-md hover:shadow-indigo-950/20 hover:-translate-y-0.5 active:translate-y-0"
                      }`}
                    >
                      {isAcked ? (
                        <>
                          <Check className="w-4 h-4" />
                          <span>Signed Off</span>
                        </>
                      ) : (
                        <>
                          <FileCheck className="w-4 h-4" />
                          <span>Sign Policy</span>
                        </>
                      )}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>

          {/* ── Compliance Audit Issues ── */}
          <div className="glass-card p-6 rounded-2xl space-y-6 h-fit">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">
                Compliance Audits
              </h3>
              <ShieldAlert className="w-5 h-5 text-indigo-400" />
            </div>

            <div className="space-y-4 divide-y divide-brand-border">
              {issues.map((issue) => (
                <div key={issue.id} className="pt-4 first:pt-0 space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span
                      className={`px-2 py-0.5 rounded-full font-bold text-[9px] uppercase border ${
                        issue.severity === "critical"
                          ? "bg-rose-950/40 text-rose-400 border-rose-500/20 animate-pulse"
                          : issue.severity === "high"
                          ? "bg-amber-950/40 text-amber-400 border-amber-500/20"
                          : "bg-slate-800 text-gray-400 border-brand-border"
                      }`}
                    >
                      {issue.severity}
                    </span>
                    <span className="text-gray-500 font-semibold">Due: {issue.due_date}</span>
                  </div>
                  <h4 className="font-semibold text-sm leading-snug">{issue.title}</h4>
                  <div className="flex justify-between items-center pt-1 text-[10px]">
                    <span className="text-gray-500">ID: {issue.audit_id}</span>
                    <span
                      className={`font-bold capitalize ${
                        issue.status === "resolved"
                          ? "text-emerald-400"
                          : issue.status === "in_progress"
                          ? "text-amber-400"
                          : "text-rose-400"
                      }`}
                    >
                      {issue.status.replace("_", " ")}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── SIGNATURE MODAL ── */}
      {selectedPolicy && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-card w-full max-w-lg rounded-2xl overflow-hidden shadow-2xl animate-scale-up border border-indigo-500/20">
            {/* Header */}
            <div className="p-6 border-b border-brand-border flex justify-between items-center bg-slate-950/60">
              <h3 className="font-bold text-lg flex items-center gap-2">
                <Scale className="w-5 h-5 text-indigo-400" />
                <span>Governance Sign-Off</span>
              </h3>
              <button
                onClick={closeModal}
                className="text-gray-400 hover:text-white text-lg font-bold"
              >
                &times;
              </button>
            </div>

            {/* Body */}
            <div className="p-6 space-y-6">
              {/* Policy meta */}
              <div className="space-y-2">
                <div className="flex items-center flex-wrap gap-2">
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${
                      (POLICY_TYPE_META[selectedPolicy.type] || POLICY_TYPE_META.other).color
                    }`}
                  >
                    {(POLICY_TYPE_META[selectedPolicy.type] || POLICY_TYPE_META.other).label}
                  </span>
                  <span className="text-[10px] bg-indigo-950/60 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full font-bold">
                    v{selectedPolicy.version}
                  </span>
                  <span className="text-xs text-gray-500 font-semibold">
                    Effective: {selectedPolicy.effective_date}
                  </span>
                </div>
                <h4 className="font-bold text-xl text-white">{selectedPolicy.title}</h4>
              </div>

              {/* Scrollable content */}
              <div className="bg-slate-950/60 border border-brand-border px-4 py-4 rounded-xl text-sm text-gray-300 leading-relaxed max-h-48 overflow-y-auto">
                <p className="font-semibold text-gray-200 mb-2">Policy Guidelines:</p>
                {selectedPolicy.content || "No policy content available."}
                <p className="mt-4 text-xs text-gray-500 italic">
                  Note: Acknowledging this policy serves as a legally binding digital signature
                  recorded on the corporate sustainability ledger.
                </p>
              </div>

              {/* Affirmation checkbox */}
              <label className="flex items-start gap-3 cursor-pointer group">
                <input
                  type="checkbox"
                  checked={signatureChecked}
                  onChange={(e) => setSignatureChecked(e.target.checked)}
                  className="mt-1 rounded bg-slate-900 text-indigo-600 w-4 h-4 cursor-pointer"
                />
                <span className="text-xs text-gray-400 group-hover:text-gray-300 transition-colors">
                  I confirm that I have read, understood, and agree to abide by these policy
                  guidelines.
                </span>
              </label>

              {/* Signature name input */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-widest block">
                  Digital Signature (Type your full name to sign)
                </label>
                <input
                  type="text"
                  placeholder={user.full_name}
                  value={signatureName}
                  onChange={(e) => setSignatureName(e.target.value)}
                  className="w-full bg-slate-900 border border-brand-border px-3.5 py-2.5 rounded-xl text-sm focus:outline-none focus:border-indigo-500/50 text-white font-medium"
                />
                <p className="text-[10px] text-gray-500">
                  Please type{" "}
                  <span className="font-semibold text-gray-300">{user.full_name}</span> exactly
                  as shown.
                </p>
              </div>

              {/* Actions */}
              <div className="pt-2 flex gap-4">
                <button
                  type="button"
                  onClick={closeModal}
                  className="flex-1 bg-slate-900 border border-brand-border text-gray-400 py-2.5 rounded-xl text-sm font-semibold hover:text-white hover:bg-slate-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSign}
                  disabled={isSignBtnDisabled}
                  className="flex-1 bg-gradient-indigo disabled:opacity-40 disabled:pointer-events-none text-white py-2.5 rounded-xl text-sm font-semibold hover:shadow-indigo-950/20 hover:shadow-lg transition-all"
                >
                  Sign &amp; Accept
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── SUCCESS TOAST ── */}
      {showToast && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-950/90 border border-emerald-500/30 text-white px-5 py-4 rounded-2xl shadow-2xl flex items-center gap-3 animate-fade-in backdrop-blur-md max-w-sm">
          <div className="bg-emerald-950 p-2 rounded-xl border border-emerald-500/30 shrink-0">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <p className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Success</p>
            <p className="text-xs text-gray-300 mt-0.5">{toastMessage}</p>
          </div>
        </div>
      )}
    </>
  );
}
