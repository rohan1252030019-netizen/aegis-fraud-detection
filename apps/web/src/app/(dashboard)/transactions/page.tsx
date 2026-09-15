"use client";

import React, { useEffect, useState, useCallback } from "react";
import { api, getErrorMessage } from "@/lib/api";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { formatCurrency } from "@/lib/utils";
import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
  ArrowLeftRight,
  Search,
  RefreshCw,
  Copy,
  Check,
  ChevronLeft,
  ChevronRight,
  ArrowRight,
  AlertTriangle,
  CheckCircle2,
  Filter,
} from "lucide-react";

interface TransactionItem {
  id: string;
  transaction_id: string;
  sender_account_id: string;
  receiver_account_id: string;
  amount: number;
  currency: string;
  timestamp: string;
  is_flagged: boolean;
  risk_level: string;
  risk_score: number;
}

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [accountFilter, setAccountFilter] = useState("");
  const [flaggedOnly, setFlaggedOnly] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  const loadTransactions = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params: Record<string, string | number | boolean> = {
        page,
        page_size: pageSize,
      };
      if (accountFilter.trim()) params.account_id = accountFilter.trim();
      if (flaggedOnly) params.is_flagged = true;

      const res = await api.get("/transactions", { params });
      setTransactions(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [page, accountFilter, flaggedOnly]);

  useEffect(() => {
    loadTransactions();
  }, [loadTransactions]);

  const handleCopy = (text: string, e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(text);
    setCopiedId(text);
    setTimeout(() => setCopiedId(null), 1500);
  };

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-6">
      <PageHeader
        title="Transaction Ledger"
        description="Immutable real-time audit ledger of monitored financial transfers with automated anomaly detection flags."
        badge={
          <span className="text-xs px-2 py-0.5 rounded-full font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            {total} Entries
          </span>
        }
      >
        <Button
          variant="outline"
          size="sm"
          onClick={loadTransactions}
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
          <Button variant="ghost" size="sm" onClick={loadTransactions} className="h-7 text-xs text-rose-300">
            Retry
          </Button>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
        <div className="flex items-center gap-2">
          <Button
            variant={flaggedOnly ? "destructive" : "outline"}
            size="sm"
            onClick={() => {
              setFlaggedOnly(!flaggedOnly);
              setPage(1);
            }}
            className="h-9 text-xs gap-1.5"
          >
            <Filter className="w-3.5 h-3.5" />
            <span>{flaggedOnly ? "Showing Flagged Only" : "Filter Flagged Anomalies"}</span>
          </Button>
        </div>

        <div className="w-full sm:w-72">
          <Input
            placeholder="Filter by Account ID..."
            value={accountFilter}
            onChange={(e) => {
              setAccountFilter(e.target.value);
              setPage(1);
            }}
            icon={<Search className="w-3.5 h-3.5" />}
            className="h-9 text-xs"
          />
        </div>
      </div>

      {/* Ledger Table Card */}
      <Card className="overflow-hidden border-border/70">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-40">Tx Identifier</TableHead>
              <TableHead className="w-72">Transfer Flow (Source ➔ Destination)</TableHead>
              <TableHead className="w-36 text-right">Amount</TableHead>
              <TableHead className="w-32 text-center">Status Flag</TableHead>
              <TableHead className="w-32">Risk Level</TableHead>
              <TableHead className="w-40 text-right">Timestamp</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-5 w-28" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-56" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-24 ml-auto" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-20 mx-auto" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-24 ml-auto" /></TableCell>
                </TableRow>
              ))
            ) : transactions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="p-0">
                  <EmptyState
                    icon={ArrowLeftRight}
                    title="No transactions found"
                    description={
                      accountFilter || flaggedOnly
                        ? "No transfers match the applied filter criteria."
                        : "No transaction logs have been ingested yet."
                    }
                    actionLabel={accountFilter || flaggedOnly ? "Reset Filters" : undefined}
                    onAction={() => {
                      setAccountFilter("");
                      setFlaggedOnly(false);
                    }}
                  />
                </TableCell>
              </TableRow>
            ) : (
              transactions.map((tx) => (
                <TableRow key={tx.id} className="hover:bg-muted/40 transition-colors">
                  <TableCell>
                    <div className="flex items-center gap-1 font-mono text-xs text-foreground/90">
                      <span>{tx.transaction_id}</span>
                      <button
                        type="button"
                        onClick={(e) => handleCopy(tx.transaction_id, e)}
                        className="text-muted-foreground hover:text-foreground p-0.5 rounded"
                        title="Copy Tx ID"
                      >
                        {copiedId === tx.transaction_id ? (
                          <Check className="w-3 h-3 text-emerald-400" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </button>
                    </div>
                  </TableCell>

                  <TableCell>
                    <div className="flex items-center gap-2 font-mono text-xs">
                      <span className="px-1.5 py-0.5 rounded bg-muted/60 text-foreground border border-border/40">
                        {tx.sender_account_id}
                      </span>
                      <ArrowRight className="w-3 h-3 text-muted-foreground shrink-0" />
                      <span className="px-1.5 py-0.5 rounded bg-muted/60 text-foreground border border-border/40">
                        {tx.receiver_account_id}
                      </span>
                    </div>
                  </TableCell>

                  <TableCell className="text-right font-mono text-xs font-semibold text-foreground">
                    {formatCurrency(tx.amount)}
                  </TableCell>

                  <TableCell className="text-center">
                    {tx.is_flagged ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20">
                        <AlertTriangle className="w-3 h-3" />
                        FLAGGED
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono bg-muted text-muted-foreground border border-border/40">
                        <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                        CLEAN
                      </span>
                    )}
                  </TableCell>

                  <TableCell>
                    <RiskBadge level={tx.risk_level} />
                  </TableCell>

                  <TableCell className="text-right font-mono text-xs text-muted-foreground">
                    {tx.timestamp ? new Date(tx.timestamp).toLocaleString() : "-"}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>

        {/* Pagination Footer */}
        {!loading && total > 0 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-border/60 bg-muted/10 text-xs text-muted-foreground">
            <div>
              Showing <span className="font-medium text-foreground">{(page - 1) * pageSize + 1}</span> to{" "}
              <span className="font-medium text-foreground">{Math.min(page * pageSize, total)}</span> of{" "}
              <span className="font-medium text-foreground">{total}</span> transfers
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
