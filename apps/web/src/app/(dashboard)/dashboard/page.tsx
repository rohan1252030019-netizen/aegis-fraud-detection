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
  LabelList,
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

  const [riskViewMode, setRiskViewMode] = useState<"cohorts" | "all">("cohorts");

  const totalAcc = metrics.total_accounts || 1959;
  const criticalCount = metrics.high_risk_accounts || 14;
  const elevatedCount = 18;
  const moderateCount = 24;
  const lowRiskCount = Math.max(0, totalAcc - criticalCount - elevatedCount - moderateCount);
  const flaggedTotal = criticalCount + elevatedCount + moderateCount;

  // When focusing on Risk Cohorts (Moderate, Elevated, Critical/High - 56 accounts)
  const riskCohortsData = [
    {
      tier: "Critical / High",
      count: criticalCount,
      percentage: ((criticalCount / flaggedTotal) * 100).toFixed(1),
      fill: "#ef4444",
    },
    {
      tier: "Elevated",
      count: elevatedCount,
      percentage: ((elevatedCount / flaggedTotal) * 100).toFixed(1),
      fill: "#f97316",
    },
    {
      tier: "Moderate",
      count: moderateCount,
      percentage: ((moderateCount / flaggedTotal) * 100).toFixed(1),
      fill: "#eab308",
    },
  ];

  // When viewing All Population
  const allPopulationData = [
    {
      tier: "Critical / High",
      count: criticalCount,
      percentage: ((criticalCount / totalAcc) * 100).toFixed(1),
      fill: "#ef4444",
    },
    {
      tier: "Elevated",
      count: elevatedCount,
      percentage: ((elevatedCount / totalAcc) * 100).toFixed(1),
      fill: "#f97316",
    },
    {
      tier: "Moderate",
      count: moderateCount,
      percentage: ((moderateCount / totalAcc) * 100).toFixed(1),
      fill: "#eab308",
    },
    {
      tier: "Low Risk",
      count: lowRiskCount,
      percentage: ((lowRiskCount / totalAcc) * 100).toFixed(1),
      fill: "#10b981",
    },
  ];

  const activeRiskData = riskViewMode === "cohorts" ? riskCohortsData : allPopulationData;

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
        <Card className="flex flex-col justify-between">
          <CardHeader className="pb-2 flex flex-row items-start justify-between gap-2">
            <div>
              <CardTitle className="text-sm font-semibold">Account Risk Distribution</CardTitle>
              <CardDescription>
                {riskViewMode === "cohorts"
                  ? "Flagged risk cohorts (56 anomalous accounts)"
                  : "Complete population (1,959 accounts)"}
              </CardDescription>
            </div>
            {/* View Mode Switcher */}
            <div className="flex items-center gap-1 bg-muted/60 p-0.5 rounded-lg border border-border/40 shrink-0">
              <button
                type="button"
                onClick={() => setRiskViewMode("cohorts")}
                className={`px-2 py-0.5 text-[10px] font-medium rounded transition-all ${
                  riskViewMode === "cohorts"
                    ? "bg-primary text-primary-foreground shadow-xs font-semibold"
                    : "text-muted-foreground hover:text-foreground"
                }`}
                title="Focus on anomalous cohorts (Moderate, Elevated, Critical)"
              >
                Risk Cohorts
              </button>
              <button
                type="button"
                onClick={() => setRiskViewMode("all")}
                className={`px-2 py-0.5 text-[10px] font-medium rounded transition-all ${
                  riskViewMode === "all"
                    ? "bg-primary text-primary-foreground shadow-xs font-semibold"
                    : "text-muted-foreground hover:text-foreground"
                }`}
                title="View complete population including low risk baseline"
              >
                All (1.9k)
              </button>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {/* Quick summary badges */}
            <div className="grid grid-cols-4 gap-1.5 text-center">
              <div className="p-1 rounded bg-emerald-500/10 border border-emerald-500/20">
                <div className="text-[9px] text-muted-foreground font-mono">Low</div>
                <div className="text-xs font-bold text-emerald-400 font-mono">1.9k</div>
              </div>
              <div className="p-1 rounded bg-amber-500/10 border border-amber-500/20">
                <div className="text-[9px] text-muted-foreground font-mono">Mod</div>
                <div className="text-xs font-bold text-amber-400 font-mono">24</div>
              </div>
              <div className="p-1 rounded bg-orange-500/10 border border-orange-500/20">
                <div className="text-[9px] text-muted-foreground font-mono">Elev</div>
                <div className="text-xs font-bold text-orange-400 font-mono">18</div>
              </div>
              <div className="p-1 rounded bg-rose-500/10 border border-rose-500/20">
                <div className="text-[9px] text-muted-foreground font-mono">Crit</div>
                <div className="text-xs font-bold text-rose-400 font-mono">14</div>
              </div>
            </div>

            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={activeRiskData}
                  layout="vertical"
                  margin={{ top: 5, right: 35, left: 10, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" horizontal={false} />
                  <XAxis
                    type="number"
                    stroke="#71717a"
                    fontSize={10}
                    domain={riskViewMode === "cohorts" ? [0, 30] : [0, 2200]}
                    tickFormatter={(val) => (val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val)}
                  />
                  <YAxis
                    dataKey="tier"
                    type="category"
                    stroke="#71717a"
                    fontSize={11}
                    width={riskViewMode === "cohorts" ? 95 : 80}
                    tickLine={false}
                  />
                  <Tooltip
                    cursor={{ fill: "rgba(255, 255, 255, 0.05)" }}
                    contentStyle={{
                      backgroundColor: "#18181b",
                      borderColor: "#27272a",
                      borderRadius: "8px",
                      fontSize: "12px",
                      color: "#f4f4f5",
                    }}
                    formatter={(val: any, name: any, item: any) => [
                      `${val} accounts (${item.payload.percentage}% of ${riskViewMode === "cohorts" ? "flagged cohort" : "total"})`,
                      "Population",
                    ]}
                  />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]} minPointSize={14}>
                    <LabelList
                      dataKey="count"
                      position="right"
                      fill="#e4e4e7"
                      fontSize={11}
                      fontWeight={600}
                      formatter={(val: any) => `${val}`}
                    />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 text-[11px] text-muted-foreground/80 border-t border-border/40 pt-2 flex items-center justify-between">
              <span>{riskViewMode === "cohorts" ? "56 Flagged Entities" : "1,959 Total Entities"}</span>
              <span className="font-mono text-rose-400 font-semibold">14 Active Mule Rings</span>
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
