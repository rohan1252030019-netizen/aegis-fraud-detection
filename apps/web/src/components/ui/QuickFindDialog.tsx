"use client";

import React, { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  LayoutDashboard,
  AlertTriangle,
  Users,
  ArrowLeftRight,
  Share2,
  Upload,
  X,
  ExternalLink,
  ShieldAlert,
} from "lucide-react";

interface QuickFindDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

interface NavItem {
  id: string;
  title: string;
  description: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  category: "Navigation" | "Quick Action";
}

const NAV_ITEMS: NavItem[] = [
  {
    id: "nav-dashboard",
    title: "Security & Fraud Dashboard",
    description: "Real-time KPI metrics, behavioral anomaly scores, risk trends",
    href: "/dashboard",
    icon: LayoutDashboard,
    category: "Navigation",
  },
  {
    id: "nav-alerts",
    title: "Security Alerts & Triggers",
    description: "Active high-risk detections, burst activity, and mule warnings",
    href: "/alerts",
    icon: AlertTriangle,
    category: "Navigation",
  },
  {
    id: "nav-accounts",
    title: "Monitored Accounts",
    description: "Behavioral profiling, composite risk scores, mule flags",
    href: "/accounts",
    icon: Users,
    category: "Navigation",
  },
  {
    id: "nav-transactions",
    title: "Transaction Ledger",
    description: "Full auditable transaction records and real-time anomaly scores",
    href: "/transactions",
    icon: ArrowLeftRight,
    category: "Navigation",
  },
  {
    id: "nav-graph",
    title: "Graph Correlation Network",
    description: "D3 interactive force graph of mule rings and transaction clusters",
    href: "/graph",
    icon: Share2,
    category: "Navigation",
  },
  {
    id: "nav-import",
    title: "Data Ingestion & Pipeline",
    description: "Upload financial CSV/JSON logs to run multi-layer detection",
    href: "/data-import",
    icon: Upload,
    category: "Navigation",
  },
];

export function QuickFindDialog({ open, onOpenChange }: QuickFindDialogProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Filter items
  const filteredItems = NAV_ITEMS.filter((item) => {
    const q = query.trim().toLowerCase();
    if (!q) return true;
    return (
      item.title.toLowerCase().includes(q) ||
      item.description.toLowerCase().includes(q) ||
      item.category.toLowerCase().includes(q)
    );
  });

  // Focus input when opened
  useEffect(() => {
    if (open) {
      setQuery("");
      setSelectedIndex(0);
      setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
    }
  }, [open]);

  // Reset selected index when filtered items change
  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  // Handle keyboard navigation inside the modal
  useEffect(() => {
    if (!open) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev + 1 < filteredItems.length ? prev + 1 : 0
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev - 1 >= 0 ? prev - 1 : Math.max(0, filteredItems.length - 1)
        );
      } else if (e.key === "Enter") {
        e.preventDefault();
        const selected = filteredItems[selectedIndex];
        if (selected) {
          onOpenChange(false);
          router.push(selected.href);
        } else if (query.trim()) {
          // If query looks like an account ID, navigate to it or accounts search
          onOpenChange(false);
          if (query.trim().toUpperCase().startsWith("ACC_")) {
            router.push(`/graph?account=${encodeURIComponent(query.trim().toUpperCase())}`);
          } else {
            router.push(`/accounts`);
          }
        }
      } else if (e.key === "Escape") {
        e.preventDefault();
        onOpenChange(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, filteredItems, selectedIndex, query, onOpenChange, router]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-16 sm:pt-24 px-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-background/80 backdrop-blur-sm transition-opacity"
        onClick={() => onOpenChange(false)}
      />

      {/* Modal Dialog */}
      <div className="relative w-full max-w-xl overflow-hidden rounded-xl border border-border bg-card shadow-2xl transition-all z-50">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 border-b border-border/80">
          <Search className="w-5 h-5 text-muted-foreground shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a page, feature, or account ID..."
            className="w-full bg-transparent px-3 py-4 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
          />
          {query ? (
            <button
              type="button"
              onClick={() => setQuery("")}
              className="text-muted-foreground hover:text-foreground p-1 rounded"
            >
              <X className="w-4 h-4" />
            </button>
          ) : (
            <kbd className="hidden sm:inline-block rounded bg-muted/60 border border-border px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground">
              ESC
            </kbd>
          )}
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filteredItems.length === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">
              <ShieldAlert className="w-8 h-8 text-muted-foreground/60 mx-auto mb-2" />
              <p>No results found for &ldquo;{query}&rdquo;</p>
              <p className="text-xs text-muted-foreground/80 mt-1">
                Press <span className="font-semibold text-foreground">Enter</span> to search Accounts directory
              </p>
            </div>
          ) : (
            filteredItems.map((item, index) => {
              const Icon = item.icon;
              const isSelected = index === selectedIndex;
              return (
                <div
                  key={item.id}
                  onClick={() => {
                    onOpenChange(false);
                    router.push(item.href);
                  }}
                  onMouseEnter={() => setSelectedIndex(index)}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
                    isSelected
                      ? "bg-accent text-accent-foreground"
                      : "hover:bg-muted/50 text-foreground"
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={`p-1.5 rounded-md ${
                        isSelected
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="truncate">
                      <p className="text-sm font-medium truncate">{item.title}</p>
                      <p className="text-xs text-muted-foreground truncate">
                        {item.description}
                      </p>
                    </div>
                  </div>
                  <ExternalLink className="w-3.5 h-3.5 text-muted-foreground shrink-0 opacity-60 ml-2" />
                </div>
              );
            })
          )}
        </div>

        {/* Footer shortcuts helper */}
        <div className="flex items-center justify-between border-t border-border/60 bg-muted/20 px-4 py-2 text-[11px] text-muted-foreground">
          <div className="flex items-center gap-3">
            <span>
              <kbd className="font-mono bg-background px-1 py-0.5 rounded border border-border">↑</kbd>{" "}
              <kbd className="font-mono bg-background px-1 py-0.5 rounded border border-border">↓</kbd> to navigate
            </span>
            <span>
              <kbd className="font-mono bg-background px-1 py-0.5 rounded border border-border">↵</kbd> to select
            </span>
          </div>
          <span>
            <kbd className="font-mono bg-background px-1 py-0.5 rounded border border-border">ESC</kbd> to close
          </span>
        </div>
      </div>
    </div>
  );
}
