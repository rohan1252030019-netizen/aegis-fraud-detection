import React from "react";
import { cn } from "@/lib/utils";

interface RiskBadgeProps {
  level: string | null | undefined;
  className?: string;
  showDot?: boolean;
}

export function RiskBadge({ level, className, showDot = true }: RiskBadgeProps) {
  const norm = (level || "UNKNOWN").toUpperCase();

  const config: Record<
    string,
    { bg: string; text: string; border: string; dot: string; label: string }
  > = {
    CRITICAL: {
      bg: "bg-rose-500/10",
      text: "text-rose-400",
      border: "border-rose-500/20",
      dot: "bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.6)]",
      label: "CRITICAL",
    },
    HIGH: {
      bg: "bg-orange-500/10",
      text: "text-orange-400",
      border: "border-orange-500/20",
      dot: "bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.6)]",
      label: "HIGH",
    },
    ELEVATED: {
      bg: "bg-amber-500/10",
      text: "text-amber-400",
      border: "border-amber-500/20",
      dot: "bg-amber-500",
      label: "ELEVATED",
    },
    MODERATE: {
      bg: "bg-yellow-500/10",
      text: "text-yellow-400",
      border: "border-yellow-500/20",
      dot: "bg-yellow-400",
      label: "MODERATE",
    },
    LOW: {
      bg: "bg-emerald-500/10",
      text: "text-emerald-400",
      border: "border-emerald-500/20",
      dot: "bg-emerald-400",
      label: "LOW",
    },
    UNKNOWN: {
      bg: "bg-zinc-500/10",
      text: "text-zinc-400",
      border: "border-zinc-500/20",
      dot: "bg-zinc-400",
      label: "UNKNOWN",
    },
  };

  const style = config[norm] || config.UNKNOWN;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium tracking-tight border select-none transition-colors",
        style.bg,
        style.text,
        style.border,
        className
      )}
    >
      {showDot && <span className={cn("w-1.5 h-1.5 rounded-full shrink-0", style.dot)} />}
      <span>{style.label}</span>
    </span>
  );
}
