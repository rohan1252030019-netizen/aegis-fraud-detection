"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Shield,
  LayoutDashboard,
  AlertTriangle,
  Users,
  ArrowLeftRight,
  Share2,
  Upload,
  LogOut,
  Activity,
  CheckCircle2,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  onCloseMobile?: () => void;
}

export function Sidebar({ onCloseMobile }: SidebarProps) {
  const pathname = usePathname();

  const navGroups = [
    {
      group: "Overview",
      items: [
        { label: "Overview", href: "/dashboard", icon: LayoutDashboard },
        { label: "Security Alerts", href: "/alerts", icon: AlertTriangle, badge: "Live" },
      ],
    },
    {
      group: "Intelligence",
      items: [
        { label: "Monitored Accounts", href: "/accounts", icon: Users },
        { label: "Transaction Ledger", href: "/transactions", icon: ArrowLeftRight },
        { label: "Graph Network", href: "/graph", icon: Share2 },
      ],
    },
    {
      group: "Pipeline & Config",
      items: [
        { label: "Data Ingestion", href: "/data-import", icon: Upload },
      ],
    },
  ];

  return (
    <aside className="w-64 bg-card/90 border-r border-border/70 flex flex-col h-screen fixed left-0 top-0 z-40 backdrop-blur-md">
      {/* Brand Header */}
      <div className="flex items-center justify-between px-5 h-16 border-b border-border/60 shrink-0">
        <Link
          href="/dashboard"
          onClick={onCloseMobile}
          className="flex items-center gap-2.5 group cursor-pointer"
        >
          <div className="h-8 w-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary group-hover:border-primary/40 transition-colors">
            <Shield className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-semibold text-sm tracking-tight text-foreground">AEGIS</span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-muted/80 text-muted-foreground border border-border/40">
                PROD
              </span>
            </div>
            <p className="text-[11px] text-muted-foreground leading-none mt-0.5">
              Anti-Mule Platform
            </p>
          </div>
        </Link>

        {onCloseMobile && (
          <button
            onClick={onCloseMobile}
            className="md:hidden text-muted-foreground hover:text-foreground p-1 rounded-md hover:bg-muted"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-6 overflow-y-auto">
        {navGroups.map((group) => (
          <div key={group.group} className="space-y-1">
            <div className="px-3 text-[11px] font-medium tracking-wider text-muted-foreground/70 uppercase">
              {group.group}
            </div>
            <div className="mt-1 space-y-0.5">
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={onCloseMobile}
                    className={cn(
                      "flex items-center justify-between px-3 py-2 text-xs font-medium rounded-md transition-all duration-150 group",
                      isActive
                        ? "bg-accent text-accent-foreground shadow-xs font-semibold"
                        : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                    )}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <Icon
                        className={cn(
                          "w-4 h-4 shrink-0 transition-colors",
                          isActive
                            ? "text-foreground"
                            : "text-muted-foreground group-hover:text-foreground"
                        )}
                      />
                      <span className="truncate">{item.label}</span>
                    </div>

                    {item.badge && (
                      <span className="text-[10px] px-1.5 py-0.2 rounded-full font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20">
                        {item.badge}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* System Status Telemetry */}
      <div className="px-4 py-3 mx-3 mb-2 rounded-lg border border-border/50 bg-muted/20">
        <div className="flex items-center justify-between text-[11px]">
          <div className="flex items-center gap-1.5 text-muted-foreground">
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span>Multi-Layer Engine</span>
          </div>
          <span className="flex items-center gap-1 text-[10px] font-mono text-emerald-400 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            99.9%
          </span>
        </div>
        <div className="mt-1.5 text-[10px] text-muted-foreground/80 flex items-center justify-between font-mono">
          <span>Latency: 14ms</span>
          <span>Rules: Active</span>
        </div>
      </div>

      {/* User Footer / Logout */}
      <div className="p-3 border-t border-border/60 shrink-0">
        <div className="flex items-center justify-between p-2 rounded-md hover:bg-muted/40 transition-colors">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-7 h-7 rounded-full bg-muted border border-border flex items-center justify-center text-xs font-semibold text-foreground">
              SA
            </div>
            <div className="min-w-0">
              <p className="text-xs font-medium text-foreground truncate leading-tight">
                Security Admin
              </p>
              <p className="text-[10px] text-muted-foreground truncate font-mono">
                soc@aegis.io
              </p>
            </div>
          </div>
          <button
            type="button"
            title="Sign out"
            onClick={() => {
              if (typeof window !== "undefined") {
                localStorage.removeItem("aegis_token");
                window.location.href = "/dashboard";
              }
            }}
            className="p-1.5 text-muted-foreground hover:text-foreground rounded hover:bg-muted transition-colors cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
