import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number | string | null | undefined): string {
  if (amount == null || amount === "") return "₹0.00";
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  if (isNaN(num)) return "₹0.00";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(num);
}

export function riskLevelToColor(level: string | null | undefined): string {
  switch (level?.toUpperCase()) {
    case "CRITICAL": return "#ef4444";
    case "HIGH":     return "#f97316";
    case "ELEVATED": return "#f59e0b";
    case "MODERATE": return "#84cc16";
    case "LOW":      return "#22c55e";
    default:         return "#6b7280";
  }
}
