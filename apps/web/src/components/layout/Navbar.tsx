"use client";

import React, { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import {
  Menu,
  Search,
  Bell,
  CheckCircle2,
  Terminal,
  Clock,
  Sparkles,
  Command,
} from "lucide-react";
import { Button } from "@/components/ui/button";

interface NavbarProps {
  onOpenMobileMenu: () => void;
}

export function Navbar({ onOpenMobileMenu }: NavbarProps) {
  const pathname = usePathname();
  const [time, setTime] = useState<string>("");

  useEffect(() => {
    const update = () => {
      const now = new Date();
      setTime(
        now.toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: false,
        }) + " UTC"
      );
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  const routeTitles: Record<string, string> = {
    "/dashboard": "Security & Fraud Overview",
    "/alerts": "Real-time Security Alerts",
    "/accounts": "Monitored Accounts & Mules",
    "/transactions": "Real-time Transaction Ledger",
    "/graph": "Network Topology & Correlation",
    "/data-import": "Data Ingestion & Ingestion Pipeline",
  };

  const currentTitle = routeTitles[pathname] || "Fraud Detection Console";

  return (
    <header className="sticky top-0 z-30 flex h-14 w-full items-center justify-between border-b border-border/60 bg-background/80 px-6 backdrop-blur-md">
      {/* Left: Mobile trigger & Breadcrumb */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onOpenMobileMenu}
          className="md:hidden text-muted-foreground hover:text-foreground p-1.5 rounded-md hover:bg-muted"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 text-xs font-medium">
          <span className="text-muted-foreground/80 hidden sm:inline">AEGIS Console</span>
          <span className="text-muted-foreground/40 hidden sm:inline">/</span>
          <span className="text-foreground font-semibold">{currentTitle}</span>
        </div>
      </div>

      {/* Right: Telemetry & Shortcuts */}
      <div className="flex items-center gap-3">
        {/* Quick Search Shortcut Pill */}
        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 text-xs text-muted-foreground bg-muted/40 border border-border/60 rounded-md">
          <Search className="w-3.5 h-3.5" />
          <span>Quick Find...</span>
          <kbd className="ml-2 font-mono text-[10px] bg-background px-1.5 py-0.5 rounded border border-border/70 text-foreground">
            ⌘K
          </kbd>
        </div>

        {/* Live Clock / SOC Time */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-muted/30 border border-border/40 text-[11px] font-mono text-muted-foreground">
          <Clock className="w-3 h-3 text-cyan-400" />
          <span>{time || "12:00:00 UTC"}</span>
        </div>

        {/* System Online Status */}
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[11px] text-emerald-400 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          <span className="hidden sm:inline">Live Stream Active</span>
          <span className="sm:hidden">Live</span>
        </div>
      </div>
    </header>
  );
}
