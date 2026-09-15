import React from "react";
import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";
import { Skeleton } from "./skeleton";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  trend?: {
    value: string;
    positive?: boolean;
    neutral?: boolean;
  };
  loading?: boolean;
  badge?: string;
  badgeVariant?: "default" | "destructive" | "warning" | "success" | "cyan";
  className?: string;
}

export function StatCard({
  title,
  value,
  icon: Icon,
  description,
  trend,
  loading = false,
  badge,
  badgeVariant = "default",
  className,
}: StatCardProps) {
  const badgeClasses = {
    default: "bg-muted text-muted-foreground border-border/40",
    destructive: "bg-red-500/10 text-red-400 border-red-500/20",
    warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    success: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    cyan: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  };

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-lg border border-border/70 bg-card/60 p-5 shadow-sm transition-all duration-200 hover:border-border hover:bg-card/80",
        className
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{title}</span>
        <div className="flex h-8 w-8 items-center justify-center rounded-md border border-border/60 bg-muted/40 text-foreground/80">
          <Icon className="h-4 w-4" />
        </div>
      </div>

      <div className="mt-4 flex items-baseline justify-between">
        {loading ? (
          <Skeleton className="h-8 w-24" />
        ) : (
          <div className="text-2xl font-bold font-mono tracking-tight text-foreground">
            {value}
          </div>
        )}

        {badge && (
          <span
            className={cn(
              "inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-medium tracking-wide",
              badgeClasses[badgeVariant]
            )}
          >
            {badge}
          </span>
        )}
      </div>

      {(description || trend) && (
        <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
          {trend && (
            <span
              className={cn(
                "font-medium",
                trend.neutral
                  ? "text-muted-foreground"
                  : trend.positive
                  ? "text-emerald-400"
                  : "text-rose-400"
              )}
            >
              {trend.value}
            </span>
          )}
          {description && <span>{description}</span>}
        </div>
      )}
    </div>
  );
}
