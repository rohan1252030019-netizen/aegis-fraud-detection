"use client";

import React, { useEffect, useState } from "react";
import { api, getErrorMessage } from "@/lib/api";
import {
  FolderKanban,
  ShieldCheck,
  ShieldAlert,
  Clock,
  ExternalLink,
  ChevronRight,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCcw,
  Sparkles,
} from "lucide-react";

interface CaseItem {
  id: string;
  case_number: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  final_decision: string | null;
  created_at: string;
}

export default function CasesPage() {
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [selectedCase, setSelectedCase] = useState<CaseItem | null>(null);
  const [investigating, setInvestigating] = useState(false);
  const [investigationData, setInvestigationData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [feedbackSuccess, setFeedbackSuccess] = useState("");

  useEffect(() => {
    loadCases();
  }, []);

  async function loadCases() {
    try {
      const res = await api.get("/cases");
      setCases(res.data.items || []);
      if (res.data.items?.length > 0) {
        setSelectedCase(res.data.items[0]);
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  async function triggerInvestigation(caseId: string, accountId: string = "ACC_1025") {
    setInvestigating(true);
    setError("");
    setFeedbackSuccess("");
    try {
      const res = await api.get(`/cases/${caseId}/investigate/${accountId}`);
      setInvestigationData(res.data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setInvestigating(false);
    }
  }

  async function submitDecision(caseId: string, decision: string) {
    try {
      await api.post(`/cases/${caseId}/feedback`, {
        decision: decision,
        notes: `Investigator marked as ${decision} after reviewing formal verification and SHAP drivers.`,
      });
      setFeedbackSuccess(`Case decision recorded: ${decision}. Threat Memory updated.`);
      loadCases();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Case Management & Investigation</h1>
          <p className="text-sm text-slate-400 mt-1">
            Auditable compliance dossiers, formal verification checks, SHAP feature attribution, and Threat Memory.
          </p>
        </div>
        {selectedCase && (
          <button
            onClick={() => triggerInvestigation(selectedCase.case_number, "ACC_1025")}
            disabled={investigating}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors shadow-sm"
          >
            {investigating ? (
              <>
                <RotateCcw className="w-4 h-4 animate-spin" />
                <span>Running Pipeline...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Run Full AEGIS Investigation</span>
              </>
            )}
          </button>
        )}
      </div>

      {error && (
        <div className="p-4 bg-red-950/40 border border-red-800/50 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}

      {feedbackSuccess && (
        <div className="p-4 bg-emerald-950/40 border border-emerald-800/50 rounded-lg text-emerald-300 text-sm flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <span>{feedbackSuccess}</span>
        </div>
      )}

      {/* Main Grid: Cases list on left, Investigation details on right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Active Cases */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden p-4 space-y-3">
          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-2">
            Active AML Cases ({cases.length})
          </h2>
          <div className="space-y-2">
            {cases.map((c) => {
              const isSelected = selectedCase?.id === c.id;
              return (
                <div
                  key={c.id}
                  onClick={() => {
                    setSelectedCase(c);
                    setInvestigationData(null);
                  }}
                  className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                    isSelected
                      ? "bg-slate-800 border-blue-500/50 shadow-sm"
                      : "bg-slate-950/60 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-semibold text-blue-400">{c.case_number}</span>
                    <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-medium">
                      {c.status}
                    </span>
                  </div>
                  <h3 className="text-sm font-medium text-white mt-1.5 truncate">{c.title}</h3>
                  <div className="flex items-center justify-between text-xs text-slate-400 mt-2 pt-2 border-t border-slate-800/60">
                    <span>Priority: {c.priority}</span>
                    <span>{c.final_decision || "Pending"}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right 2 Columns: Deep Investigation Dossier */}
        <div className="lg:col-span-2 space-y-6">
          {investigationData ? (
            <div className="space-y-6">
              {/* Risk Banner */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-slate-400">Target Account:</span>
                    <span className="font-mono font-bold text-white text-base">
                      {investigationData.account_id}
                    </span>
                    <span className="ml-2 px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                      {investigationData.risk_profile?.risk_level}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    {investigationData.risk_profile?.classification} • Confidence:{" "}
                    {Math.round(investigationData.risk_profile?.confidence * 100)}%
                  </p>
                </div>
                <div className="text-right sm:border-l sm:border-slate-800 sm:pl-6">
                  <div className="text-3xl font-extrabold text-white">
                    {investigationData.risk_profile?.composite_score}
                    <span className="text-sm font-normal text-slate-400">/100</span>
                  </div>
                  <span className="text-[11px] text-slate-400">Composite Risk Score</span>
                </div>
              </div>

              {/* Pipeline Execution Trace */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-white">Pipeline Execution Trace</h3>
                  <span className="text-xs font-mono text-emerald-400">
                    Total: {investigationData.total_execution_ms}ms
                  </span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {investigationData.pipeline_trace?.map((stage: any) => (
                    <div key={stage.stage} className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                      <div className="text-[10px] text-slate-400 font-mono truncate">{stage.stage}</div>
                      <div className="text-xs font-bold text-slate-200 mt-1 flex items-center justify-between">
                        <span>{stage.status}</span>
                        <span className="text-[10px] text-slate-500 font-mono">{stage.duration_ms}ms</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Formal Verification & SHAP Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Formal Verification */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4 text-emerald-400" />
                      Formal Verification
                    </h3>
                    <span className="text-xs font-bold text-emerald-400">
                      {investigationData.formal_verification?.overall_status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">{investigationData.formal_verification?.summary}</p>
                  <div className="space-y-1.5 text-xs">
                    {investigationData.formal_verification?.checks?.slice(0, 3).map((chk: any) => (
                      <div key={chk.check_name} className="flex items-center justify-between py-1 border-b border-slate-800/50">
                        <span className="text-slate-300 truncate">{chk.check_name}</span>
                        <span className="text-emerald-400 font-mono font-bold text-[10px]">{chk.status}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* SHAP Explainability */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-cyan-400" />
                      SHAP Explainability
                    </h3>
                    <span className="text-[10px] text-slate-400 font-mono">TreeExplainer</span>
                  </div>
                  <p className="text-xs text-slate-400 truncate">{investigationData.explainability?.narrative}</p>
                  <div className="space-y-1.5 text-xs">
                    {investigationData.explainability?.contributions?.slice(0, 3).map((c: any) => (
                      <div key={c.feature} className="flex items-center justify-between py-1 border-b border-slate-800/50">
                        <span className="text-slate-300 font-mono truncate">{c.feature}</span>
                        <span className="text-cyan-400 font-mono font-bold">
                          {c.contribution > 0 ? `+${c.contribution}` : c.contribution}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Local Ollama Investigation Brief */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-purple-400" />
                    Investigation Intelligence Brief ({investigationData.investigation_brief?.provider})
                  </h3>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 font-mono">
                    {investigationData.investigation_brief?.model}
                  </span>
                </div>
                <div className="p-3.5 bg-slate-950 rounded-lg text-xs text-slate-300 leading-relaxed font-sans border border-slate-800/60">
                  {investigationData.investigation_brief?.narrative}
                </div>
                <p className="text-[10px] text-slate-500 italic">
                  {investigationData.investigation_brief?.disclaimer}
                </p>
              </div>

              {/* Investigator Action Bar */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-3">
                <span className="text-xs text-slate-400 font-medium">Record Compliance Resolution:</span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => selectedCase && submitDecision(selectedCase.case_number, "TRUE_POSITIVE")}
                    className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-md text-xs font-semibold transition-colors"
                  >
                    Confirm Mule (True Positive)
                  </button>
                  <button
                    onClick={() => selectedCase && submitDecision(selectedCase.case_number, "FALSE_POSITIVE")}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-md text-xs font-semibold transition-colors"
                  >
                    Mark False Positive
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center space-y-4">
              <FolderKanban className="w-12 h-12 text-slate-600 mx-auto" />
              <div>
                <h3 className="text-base font-semibold text-white">Investigation Ready</h3>
                <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1">
                  Click &ldquo;Run Full AEGIS Investigation&rdquo; above to execute the complete multi-layer pipeline:
                  Transformer sequence analysis, Isolation Forest, Graph correlation, SHAP explainability, and Formal Verification.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
