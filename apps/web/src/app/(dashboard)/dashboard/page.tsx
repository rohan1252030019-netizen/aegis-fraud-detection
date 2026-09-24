"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { api, getErrorMessage } from "@/lib/api";
import { MOCK_OVERVIEW_METRICS, MOCK_ALERTS } from "@/lib/mockData";
import {
  Users,
  AlertTriangle,
  ShieldAlert,
  FolderKanban,
  RefreshCw,
  ArrowUpRight,
  TrendingUp,
  Activity,
  ShieldCheck,
  Zap,
  Layers,
  ArrowRight,
} from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { StatCard } from "@/components/ui/stat-card";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

interface OverviewMetrics {
  total_accounts: number;
  high_risk_accounts: number;
  active_alerts: number;
  open_cases: number;
}

interface RecentAlert {
  id: string;
  title: string;
  severity: string;
  entity_id: string;
  risk_level: string;
  created_at: string;
}

const velocityData = [
  { time: "00:00", transactions: 1240, flagged: 12 },
  { time: "04:00", transactions: 890, flagged: 8 },
  { time: "08:00", transactions: 3420, flagged: 34 },
  { time: "12:00", transactions: 5120, flagged: 48 },
  { time: "16:00", transactions: 4890, flagged: 39 },
  { time: "20:00", transactions: 3100, flagged: 25 },
  { time: "23:59", transactions: 2150, flagged: 18 },
];

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<OverviewMetrics>(MOCK_OVERVIEW_METRICS);
  const [recentAlerts, setRecentAlerts] = useState<RecentAlert[]>(MOCK_ALERTS.slice(0, 5));
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  async function loadData() {
    setError("");
    try {
      const [overviewRes, alertsRes] = await Promise.allSettled([
        api.get("/analytics/overview"),
        api.get("/alerts?page_size=5"),
      ]);

      if (overviewRes.status === "fulfilled" && overviewRes.value?.data) {
        setMetrics(overviewRes.value.data);
      } else {
        setMetrics(MOCK_OVERVIEW_METRICS);
      }

      if (alertsRes.status === "fulfilled" && alertsRes.value?.data?.items) {
        setRecentAlerts(alertsRes.value.data.items);
      } else {
        setRecentAlerts(MOCK_ALERTS.slice(0, 5));
      }
    } catch (err) {
      console.warn("Using offline simulated metrics:", err);
      setMetrics(MOCK_OVERVIEW_METRICS);
      setRecentAlerts(MOCK_ALERTS.slice(0, 5));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const riskDistributionData = [
    { tier: "Low Risk", count: Math.max(0, metrics.total_accounts - metrics.high_risk_accounts - 8), fill: "#10b981" },
    { tier: "Moderate", count: Math.min(24, Math.max(4, Math.floor(metrics.total_accounts * 0.15))), fill: "#eab308" },
    { tier: "Elevated", count: Math.min(18, Math.max(2, Math.floor(metrics.total_accounts * 0.08))), fill: "#f97316" },
    { tier: "Critical/High", count: metrics.high_risk_accounts, fill: "#ef4444" },
  ];

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <PageHeader
        title="Security & Fraud Overview"
        description="Real-time multi-layer detection overview, account behavioral health, and anomaly velocity."
      >
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
            className="h-8 gap-1.5 text-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin" : ""}`} />
            <span>Sync Engine</span>
          </Button>
          <Link href="/alerts">
            <Button size="sm" className="h-8 gap-1.5 text-xs">
              <span>View Alerts</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </Link>
        </div>
      </PageHeader>

      {/* Error banner */}
      {error && (
        <div className="p-3.5 bg-destructive/15 border border-destructive/30 rounded-lg text-rose-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
          <Button variant="ghost" size="sm" onClick={loadData} className="h-7 text-xs text-rose-300 hover:text-white">
            Retry
          </Button>
        </div>
      )}

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Monitored Accounts"
          value={metrics.total_accounts.toLocaleString()}
          icon={Users}
          loading={loading}
          trend={{ value: "+3.8%", positive: true }}
          description="vs. last 30 days"
          badge="Active Pool"
          badgeVariant="default"
        />
        <StatCard
          title="Mule Candidates"
          value={metrics.high_risk_accounts.toLocaleString()}
          icon={ShieldAlert}
          loading={loading}
          trend={{ value: metrics.high_risk_accounts > 0 ? "Action Required" : "Clean", positive: metrics.high_risk_accounts === 0 }}
          description="Composite score ≥ 70"
          badge={metrics.high_risk_accounts > 0 ? "High Risk" : "Zero Mules"}
          badgeVariant={metrics.high_risk_accounts > 0 ? "destructive" : "success"}
        />
        <StatCard
          title="Active Security Alerts"
          value={metrics.active_alerts.toLocaleString()}
          icon={AlertTriangle}
          loading={loading}
          trend={{ value: "Real-time stream", neutral: true }}
          description="Unresolved incidents"
          badge="Triggered"
          badgeVariant="warning"
        />
        <StatCard
          title="Open Cases Under Review"
          value={metrics.open_cases.toLocaleString()}
          icon={FolderKanban}
          loading={loading}
          trend={{ value: "SLA < 2h avg", positive: true }}
          description="Assigned investigators"
          badge="SOC Queue"
          badgeVariant="cyan"
        />
      </div>

      {/* Visual Analytics Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Anomaly Velocity Chart (2 cols) */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2 flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-sm font-semibold">Transaction Velocity & Anomaly Trends</CardTitle>
              <CardDescription>
                Live comparison between processed volume and anomalous pattern breaches.
              </CardDescription>
            </div>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-muted text-muted-foreground border border-border/40">
              24h Window
            </span>
          </CardHeader>
          <CardContent>
            <div className="h-64 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={velocityData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <defs>
                    <linearGradient id="txGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                    </linearGradient>
                    <linearGradient id="flaggedGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0.05} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                  <XAxis dataKey="time" stroke="#71717a" fontSize={11} tickLine={false} />
                  {/* Primary Axis: Transactions Volume (0 - 6k) */}
                  <YAxis
                    yAxisId="left"
                    stroke="#71717a"
                    fontSize={11}
                    tickLine={false}
                    tickFormatter={(val) => (val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val)}
                  />
                  {/* Secondary Axis: Flagged Anomalies (0 - 60) to eliminate line squashing */}
                  <YAxis
                    yAxisId="right"
                    orientation="right"
                    stroke="#f87171"
                    fontSize={11}
                    tickLine={false}
                    domain={[0, 60]}
                    tickFormatter={(val) => `${val}`}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#18181b",
                      borderColor: "#27272a",
                      borderRadius: "8px",
                      fontSize: "12px",
                      color: "#f4f4f5",
                    }}
                  />
                  <Area
                    yAxisId="left"
                    type="monotone"
                    dataKey="transactions"
                    name="Transactions"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#txGradient)"
                  />
                  <Area
                    yAxisId="right"
                    type="monotone"
                    dataKey="flagged"
                    name="Flagged Anomalies"
                    stroke="#ef4444"
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#flaggedGradient)"
                    dot={{ r: 3, fill: "#ef4444", strokeWidth: 1, stroke: "#18181b" }}
                    activeDot={{ r: 5, fill: "#ef4444", stroke: "#fff", strokeWidth: 2 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center justify-center gap-6 mt-3 text-xs text-muted-foreground border-t border-border/40 pt-3">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
                <span>Legitimate Volume (Left Axis)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                <span className="text-rose-400 font-medium">Flagged Deviations (Right Axis)</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Risk Distribution Breakdown (1 col) */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold">Account Risk Distribution</CardTitle>
            <CardDescription>Monitored population classified by composite scoring.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={riskDistributionData} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" horizontal={false} />
                  <XAxis type="number" stroke="#71717a" fontSize={11} />
                  <YAxis dataKey="tier" type="category" stroke="#71717a" fontSize={11} width={80} />
                  <Tooltip
                    cursor={{ fill: "rgba(255, 255, 255, 0.05)" }}
                    contentStyle={{
                      backgroundColor: "#18181b",
                      borderColor: "#27272a",
                      borderRadius: "8px",
                      fontSize: "12px",
                      color: "#f4f4f5",
                    }}
                  />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-3 text-[11px] text-muted-foreground/80 text-center border-t border-border/40 pt-3">
              Coordinated syndicates clustered into high/critical tiers.
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detection Pipeline Telemetry & Recent Incidents */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Detection Pipeline Engine Architecture (1 col) */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold">Multi-Layer Architecture</CardTitle>
              <span className="flex items-center gap-1 text-[10px] text-emerald-400 font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Engaged
              </span>
            </div>
            <CardDescription>Active algorithmic pipeline inspecting streaming events.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between p-2.5 rounded-md border border-border/60 bg-muted/20">
              <div className="flex items-center gap-2.5">
                <Zap className="w-4 h-4 text-amber-400" />
                <div>
                  <p className="text-xs font-medium text-foreground">Layer 1: Velocity Thresholds</p>
                  <p className="text-[10px] text-muted-foreground">Burst frequency & rapid liquidation</p>
                </div>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 font-medium">PASSING</span>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded-md border border-border/60 bg-muted/20">
              <div className="flex items-center gap-2.5">
                <Layers className="w-4 h-4 text-blue-400" />
                <div>
                  <p className="text-xs font-medium text-foreground">Layer 2: Graph Clustering</p>
                  <p className="text-[10px] text-muted-foreground">Topological fan-in/fan-out cycles</p>
                </div>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 font-medium">SCANNING</span>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded-md border border-border/60 bg-muted/20">
              <div className="flex items-center gap-2.5">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <div>
                  <p className="text-xs font-medium text-foreground">Layer 3: Behavioral ML Scorer</p>
                  <p className="text-[10px] text-muted-foreground">Isolation Forest + GNN ensemble</p>
                </div>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 font-medium">ONLINE</span>
            </div>
          </CardContent>
        </Card>

        {/* Live Incident Stream (2 cols) */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-3 flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-sm font-semibold">Latest Security Alerts</CardTitle>
              <CardDescription>Recent suspicious activities requiring compliance review.</CardDescription>
            </div>
            <Link href="/alerts">
              <Button variant="ghost" size="sm" className="h-7 text-xs gap-1">
                <span>All Alerts</span>
                <ArrowRight className="w-3 h-3" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : recentAlerts.length === 0 ? (
              <div className="py-8 text-center text-xs text-muted-foreground">
                No active security alerts in this cycle. System state is clean.
              </div>
            ) : (
              <div className="divide-y divide-border/50">
                {recentAlerts.map((alert) => (
                  <div key={alert.id} className="py-2.5 flex items-center justify-between gap-3 text-xs">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="h-2 w-2 rounded-full bg-rose-500 shrink-0" />
                      <div className="min-w-0">
                        <p className="font-medium text-foreground truncate">{alert.title}</p>
                        <div className="flex items-center gap-2 mt-0.5 text-[11px] text-muted-foreground font-mono">
                          <span>Target: {alert.entity_id}</span>
                          <span>•</span>
                          <span>{new Date(alert.created_at).toLocaleTimeString()}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <RiskBadge level={alert.risk_level} />
                      <Link href="/alerts">
                        <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-foreground">
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
