import { motion } from "framer-motion";
import type { ReactNode } from "react";

interface KpiCardProps {
  label: string;
  value: ReactNode;
  hint?: string;
  accent?: "primary" | "accent" | "success" | "warning";
  delay?: number;
}

const accentMap = {
  primary: "from-primary/30 to-primary/0",
  accent: "from-accent/30 to-accent/0",
  success: "from-emerald-400/30 to-transparent",
  warning: "from-amber-400/30 to-transparent",
};

export function KpiCard({ label, value, hint, accent = "primary", delay = 0 }: KpiCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="relative overflow-hidden rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-xl shadow-[var(--shadow-card)]"
    >
      <div className={`pointer-events-none absolute -top-16 -right-16 h-40 w-40 rounded-full bg-gradient-to-br ${accentMap[accent]} blur-2xl`} />
      <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">{label}</p>
      <p className="mt-3 text-3xl font-semibold tracking-tight text-foreground">{value}</p>
      {hint && <p className="mt-2 text-xs text-muted-foreground">{hint}</p>}
    </motion.div>
  );
}