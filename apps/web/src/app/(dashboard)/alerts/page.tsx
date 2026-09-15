"use client";

import React, { useEffect, useState, useMemo } from "react";
import { api, getErrorMessage } from "@/lib/api";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from "@/components/ui/table";
import {
  AlertTriangle,
  Search,
  RefreshCw,
  Copy,
  Check,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  Info,
  X,
  ExternalLink,
} from "lucide-react";

interface AlertItem {
  id: string;
  title: string;
  severity: string;
  status: string;
  alert_type: string;
  entity_id: string;
  risk_score: number;
  risk_level: string;
  created_at: string;
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedAlert, setSelectedAlert] = useState<AlertItem | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const pageSize = 15;

  async function loadAlerts() {
    setLoading(true);
    setError("");
    try {
      const res = await api.get("/alerts", {
        params: { page: 1, page_size: 100 },
      });
      setAlerts(res.data.items || []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAlerts();
  }, []);

  const handleCopy = (text: string, e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(text);
    setCopiedId(text);
    setTimeout(() => setCopiedId(null), 1500);
  };

  const filteredAlerts = useMemo(() => {
    return alerts.filter((al) => {
      const matchesSeverity =
        severityFilter === "ALL" || al.severity.toUpperCase() === severityFilter;
      const matchesSearch =
        !searchQuery ||
        al.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        al.entity_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        al.alert_type.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesSeverity && matchesSearch;
    });
  }, [alerts, severityFilter, searchQuery]);

  const totalPages = Math.max(1, Math.ceil(filteredAlerts.length / pageSize));
  const paginatedAlerts = filteredAlerts.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Security Alerts"
        description="Continuous surveillance of suspicious account activity, rapid velocity bursts, and syndicate structuring."
        badge={
          <span className="text-xs px-2 py-0.5 rounded-full font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20">
            {alerts.length} Incidents
          </span>
        }
      >
        <Button
          variant="outline"
          size="sm"
          onClick={loadAlerts}
          disabled={loading}
          className="h-8 gap-1.5 text-xs"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </Button>
      </PageHeader>

      {error && (
        <div className="p-3.5 bg-destructive/15 border border-destructive/30 rounded-lg text-rose-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
          <Button variant="ghost" size="sm" onClick={loadAlerts} className="h-7 text-xs text-rose-300">
            Retry
          </Button>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
        <Tabs value={severityFilter} onValueChange={(val) => { setSeverityFilter(val); setPage(1); }}>
          <TabsList>
            <TabsTrigger value="ALL">All Severities</TabsTrigger>
            <TabsTrigger value="CRITICAL">Critical</TabsTrigger>
            <TabsTrigger value="HIGH">High</TabsTrigger>
            <TabsTrigger value="MODERATE">Moderate</TabsTrigger>
            <TabsTrigger value="LOW">Low</TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="w-full sm:w-72">
          <Input
            placeholder="Search entity, title or type..."
            value={searchQuery}
            onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
            icon={<Search className="w-3.5 h-3.5" />}
            className="h-9 text-xs"
          />
        </div>
      </div>

      {/* Data Table */}
      <Card className="overflow-hidden border-border/70">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-28">Severity</TableHead>
              <TableHead>Alert Event</TableHead>
              <TableHead className="w-36">Entity Target</TableHead>
              <TableHead className="w-40">Detection Layer</TableHead>
              <TableHead className="w-28">Risk Level</TableHead>
              <TableHead className="w-24">Status</TableHead>
              <TableHead className="w-36 text-right">Timestamp</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-5 w-16" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-48" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-28" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-16" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-24 ml-auto" /></TableCell>
                </TableRow>
              ))
            ) : paginatedAlerts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="p-0">
                  <EmptyState
                    icon={ShieldAlert}
                    title="No matching alerts found"
                    description={searchQuery ? "Try refining your search keyword or clearing the severity filter." : "The monitored ledger currently shows zero trigger conditions."}
                    actionLabel={searchQuery || severityFilter !== "ALL" ? "Reset Filters" : undefined}
                    onAction={() => { setSearchQuery(""); setSeverityFilter("ALL"); }}
                  />
                </TableCell>
              </TableRow>
            ) : (
              paginatedAlerts.map((al) => {
                const isSelected = selectedAlert?.id === al.id;
                return (
                  <TableRow
                    key={al.id}
                    onClick={() => setSelectedAlert(al)}
                    className={`cursor-pointer transition-colors ${isSelected ? "bg-accent/60" : "hover:bg-muted/40"}`}
                  >
                    <TableCell>
                      <span className="inline-flex items-center gap-1.5 font-semibold text-xs text-rose-400">
                        <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                        <span>{al.severity}</span>
                      </span>
                    </TableCell>

                    <TableCell>
                      <span className="font-medium text-foreground text-xs">{al.title}</span>
                    </TableCell>

                    <TableCell>
                      <div className="flex items-center gap-1 font-mono text-xs text-foreground/90">
                        <span>{al.entity_id}</span>
                        <button
                          type="button"
                          onClick={(e) => handleCopy(al.entity_id, e)}
                          className="text-muted-foreground hover:text-foreground p-0.5 rounded"
                          title="Copy Entity ID"
                        >
                          {copiedId === al.entity_id ? (
                            <Check className="w-3 h-3 text-emerald-400" />
                          ) : (
                            <Copy className="w-3 h-3" />
                          )}
                        </button>
                      </div>
                    </TableCell>

                    <TableCell>
                      <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-muted/70 text-muted-foreground border border-border/40">
                        {al.alert_type}
                      </span>
                    </TableCell>

                    <TableCell>
                      <RiskBadge level={al.risk_level} />
                    </TableCell>

                    <TableCell>
                      <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-muted/40 text-muted-foreground border border-border/40">
                        {al.status}
                      </span>
                    </TableCell>

                    <TableCell className="text-right text-xs text-muted-foreground font-mono">
                      {al.created_at ? new Date(al.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "-"}
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>

        {/* Pagination Footer */}
        {!loading && filteredAlerts.length > 0 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-border/60 bg-muted/10 text-xs text-muted-foreground">
            <div>
              Showing <span className="font-medium text-foreground">{(page - 1) * pageSize + 1}</span> to{" "}
              <span className="font-medium text-foreground">{Math.min(page * pageSize, filteredAlerts.length)}</span> of{" "}
              <span className="font-medium text-foreground">{filteredAlerts.length}</span> alerts
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="h-7 w-7 p-0"
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <span className="font-mono text-xs">
                {page} / {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="h-7 w-7 p-0"
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </Card>

      {/* Slide-over Inspection Sheet when an alert is selected */}
      {selectedAlert && (
        <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-card border-l border-border/80 shadow-2xl p-6 flex flex-col justify-between backdrop-blur-md">
          <div className="space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-border/60">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-rose-400" />
                <h3 className="font-semibold text-sm text-foreground">Incident Inspector</h3>
              </div>
              <button
                type="button"
                onClick={() => setSelectedAlert(null)}
                className="text-muted-foreground hover:text-foreground p-1 rounded-md hover:bg-muted"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div>
                <span className="text-muted-foreground uppercase text-[10px] tracking-wider font-semibold">Title</span>
                <p className="font-medium text-foreground text-sm mt-0.5">{selectedAlert.title}</p>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="p-3 rounded-md bg-muted/30 border border-border/50">
                  <span className="text-muted-foreground uppercase text-[10px]">Severity</span>
                  <p className="font-semibold text-rose-400 mt-1">{selectedAlert.severity}</p>
                </div>
                <div className="p-3 rounded-md bg-muted/30 border border-border/50">
                  <span className="text-muted-foreground uppercase text-[10px]">Risk Level</span>
                  <div className="mt-1">
                    <RiskBadge level={selectedAlert.risk_level} />
                  </div>
                </div>
              </div>

              <div className="p-3 rounded-md bg-muted/30 border border-border/50 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Entity Identifier:</span>
                  <span className="font-mono font-medium text-foreground">{selectedAlert.entity_id}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Detection Mechanism:</span>
                  <span className="font-mono text-foreground">{selectedAlert.alert_type}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Anomaly Risk Score:</span>
                  <span className="font-mono font-bold text-rose-400">{selectedAlert.risk_score}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Generated At:</span>
                  <span className="font-mono text-muted-foreground">{new Date(selectedAlert.created_at).toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-border/60 flex items-center gap-2">
            <Button
              className="flex-1 text-xs h-9"
              onClick={() => setSelectedAlert(null)}
            >
              Acknowledge Incident
            </Button>
            <Button
              variant="outline"
              className="text-xs h-9"
              onClick={() => setSelectedAlert(null)}
            >
              Dismiss
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
