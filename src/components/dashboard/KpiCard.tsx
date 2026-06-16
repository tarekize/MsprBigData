import { motion } from "framer-motion";
import type { ReactNode } from "react";

interface KpiCardProps {
  label: string;
  value: ReactNode;
  hint?: string;
  accent?: "primary" | "accent" | "success" | "warning";
  delay?: number;
}

const accentBorder: Record<string, string> = {
  primary: "border-l-primary",
  accent:  "border-l-accent",
  success: "border-l-emerald-500",
  warning: "border-l-amber-400",
};

export function KpiCard({ label, value, hint, accent = "primary", delay = 0 }: KpiCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay }}
      className={`bg-card rounded-2xl border border-border border-l-4 ${accentBorder[accent]} p-5 shadow-[var(--shadow-card)]`}
    >
      <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">{label}</p>
      <p className="mt-3 text-3xl font-bold tracking-tight text-foreground">{value}</p>
      {hint && <p className="mt-2 text-xs text-muted-foreground">{hint}</p>}
    </motion.div>
  );
}
