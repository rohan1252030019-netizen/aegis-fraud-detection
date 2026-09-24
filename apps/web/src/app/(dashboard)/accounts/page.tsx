"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { api, getErrorMessage } from "@/lib/api";
import { MOCK_ACCOUNTS } from "@/lib/mockData";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { formatCurrency } from "@/lib/utils";
import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from "@/components/ui/table";
import {
  Users,
  Search,
  RefreshCw,
  Share2,
  Star,
  ChevronLeft,
  ChevronRight,
  ArrowUpRight,
  ArrowDownLeft,
  AlertTriangle,
  UserCheck,
} from "lucide-react";

interface AccountItem {
  id: string;
  account_id: string;
  classification: string;
  risk_level: string;
  composite_risk_score: number;
  total_transactions: number;
  total_sent: number;
  total_received: number;
  is_watchlisted: boolean;
}

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<AccountItem[]>(MOCK_ACCOUNTS as any);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(MOCK_ACCOUNTS.length);
  const pageSize = 20;

  const loadAccounts = useCallback(async () => {
    setError("");
    try {
      const params: Record<string, string | number> = {
        page,
        page_size: pageSize,
      };
      if (search.trim()) params.search = search.trim();
      if (riskFilter !== "ALL") params.risk_level = riskFilter;

      const res = await api.get("/accounts", { params });
      if (res.data?.items) {
        setAccounts(res.data.items);
        setTotal(res.data.total || res.data.items.length);
      } else {
        setAccounts(MOCK_ACCOUNTS as any);
        setTotal(MOCK_ACCOUNTS.length);
      }
    } catch (err) {
      console.warn("Using offline simulated accounts:", err);
      setAccounts(MOCK_ACCOUNTS as any);
      setTotal(MOCK_ACCOUNTS.length);
    } finally {
      setLoading(false);
    }
  }, [page, search, riskFilter]);

  useEffect(() => {
    loadAccounts();
  }, [loadAccounts]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-6">
      <PageHeader
        title="Monitored Accounts"
        description="Behavioral profiling, composite scoring, and syndicate classification for financial nodes."
        badge={
          <span className="text-xs px-2 py-0.5 rounded-full font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20">
            {total} Entities
          </span>
        }
      >
        <Button
          variant="outline"
          size="sm"
          onClick={loadAccounts}
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
          <Button variant="ghost" size="sm" onClick={loadAccounts} className="h-7 text-xs text-rose-300">
            Retry
          </Button>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
        <Tabs
          value={riskFilter}
          onValueChange={(val) => {
            setRiskFilter(val);
            setPage(1);
          }}
        >
          <TabsList>
            <TabsTrigger value="ALL">All Risk Levels</TabsTrigger>
            <TabsTrigger value="CRITICAL">Critical</TabsTrigger>
            <TabsTrigger value="HIGH">High</TabsTrigger>
            <TabsTrigger value="MODERATE">Moderate</TabsTrigger>
            <TabsTrigger value="LOW">Low</TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="w-full sm:w-72">
          <Input
            placeholder="Search Account ID..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            icon={<Search className="w-3.5 h-3.5" />}
            className="h-9 text-xs"
          />
        </div>
      </div>

      {/* Accounts Table Card */}
      <Card className="overflow-hidden border-border/70">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-44">Account ID</TableHead>
              <TableHead className="w-36">Classification</TableHead>
              <TableHead className="w-32">Risk Level</TableHead>
              <TableHead className="w-40">Composite Score</TableHead>
              <TableHead className="w-28 text-center">Transactions</TableHead>
              <TableHead className="w-36 text-right">Total Sent</TableHead>
              <TableHead className="w-36 text-right">Total Received</TableHead>
              <TableHead className="w-24 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-5 w-28" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-28" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-16 mx-auto" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-24 ml-auto" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-24 ml-auto" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-16 ml-auto" /></TableCell>
                </TableRow>
              ))
            ) : accounts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="p-0">
                  <EmptyState
                    icon={Users}
                    title="No accounts found"
                    description={search ? `No accounts match "${search}". Try checking your spelling or filters.` : "No accounts currently ingested into the ledger."}
                    actionLabel={search || riskFilter !== "ALL" ? "Clear Filters" : undefined}
                    onAction={() => { setSearch(""); setRiskFilter("ALL"); }}
                  />
                </TableCell>
              </TableRow>
            ) : (
              accounts.map((acc) => {
                const scorePercent = Math.min(100, Math.max(0, acc.composite_risk_score));
                const scoreColor =
                  scorePercent >= 75
                    ? "bg-rose-500"
                    : scorePercent >= 50
                    ? "bg-amber-500"
                    : "bg-emerald-500";

                return (
                  <TableRow key={acc.id} className="hover:bg-muted/40 transition-colors">
                    <TableCell>
                      <div className="flex items-center gap-2.5">
                        <div className="h-7 w-7 rounded-md bg-muted/60 border border-border/60 flex items-center justify-center font-mono text-[10px] font-semibold text-muted-foreground">
                          {acc.account_id.slice(-3)}
                        </div>
                        <div className="flex flex-col">
                          <span className="font-mono text-xs font-semibold text-foreground flex items-center gap-1.5">
                            {acc.account_id}
                            {acc.is_watchlisted && (
                              <span title="Watchlisted">
                                <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                              </span>
                            )}
                          </span>
                        </div>
                      </div>
                    </TableCell>

                    <TableCell>
                      <span className="text-xs font-medium px-2 py-0.5 rounded bg-muted/60 text-muted-foreground border border-border/40">
                        {acc.classification}
                      </span>
                    </TableCell>

                    <TableCell>
                      <RiskBadge level={acc.risk_level} />
                    </TableCell>

                    <TableCell>
                      <div className="flex items-center gap-2.5">
                        <div className="w-20 bg-muted/70 rounded-full h-1.5 overflow-hidden border border-border/30">
                          <div
                            className={`h-full rounded-full transition-all duration-300 ${scoreColor}`}
                            style={{ width: `${scorePercent}%` }}
                          />
                        </div>
                        <span className="font-mono text-xs font-semibold text-foreground/90">
                          {acc.composite_risk_score}
                        </span>
                      </div>
                    </TableCell>

                    <TableCell className="text-center font-mono text-xs text-muted-foreground">
                      {acc.total_transactions}
                    </TableCell>

                    <TableCell className="text-right font-mono text-xs text-rose-400 font-medium">
                      <span className="inline-flex items-center gap-0.5">
                        <ArrowUpRight className="w-3 h-3 text-rose-400/80" />
                        {formatCurrency(acc.total_sent)}
                      </span>
                    </TableCell>

                    <TableCell className="text-right font-mono text-xs text-emerald-400 font-medium">
                      <span className="inline-flex items-center gap-0.5">
                        <ArrowDownLeft className="w-3 h-3 text-emerald-400/80" />
                        {formatCurrency(acc.total_received)}
                      </span>
                    </TableCell>

                    <TableCell className="text-right">
                      <Link href={`/graph?account=${acc.account_id}`}>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 px-2 text-xs gap-1 text-muted-foreground hover:text-foreground"
                          title="View in Graph Network"
                        >
                          <Share2 className="w-3.5 h-3.5 text-blue-400" />
                          <span className="hidden sm:inline">Graph</span>
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>

        {/* Pagination Footer */}
        {!loading && total > 0 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-border/60 bg-muted/10 text-xs text-muted-foreground">
            <div>
              Showing <span className="font-medium text-foreground">{(page - 1) * pageSize + 1}</span> to{" "}
              <span className="font-medium text-foreground">{Math.min(page * pageSize, total)}</span> of{" "}
              <span className="font-medium text-foreground">{total}</span> accounts
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
    </div>
  );
}
