import { motion } from "framer-motion";
import type { PredictionEntity } from "@/lib/predictions";
import { Check, X } from "lucide-react";

interface Props {
  data: PredictionEntity[];
  levelLabel: string;
}

export function PredictionTable({ data, levelLabel }: Props) {
  return (
    <section className="rounded-2xl border border-border bg-card shadow-[var(--shadow-card)] overflow-hidden">
      <div className="px-6 py-4 border-b border-border">
        <p className="text-[10px] font-bold uppercase tracking-widest text-primary mb-0.5">Prédictions XGBoost</p>
        <h2 className="text-xl font-bold text-foreground tracking-tight">Détail {levelLabel}</h2>
      </div>

      {data.length === 0 ? (
        <p className="px-6 py-8 text-sm text-muted-foreground">Aucune donnée à ce niveau.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-secondary text-left text-[10px] uppercase tracking-widest text-muted-foreground border-b border-border">
                <th className="px-5 py-3 font-bold">Entité</th>
                <th className="px-5 py-3 font-bold">Bord & Gagnant</th>
                <th className="px-5 py-3 font-bold">État Éco.</th>
                <th className="px-5 py-3 font-bold">Réel</th>
                <th className="px-5 py-3 font-bold w-[28%]">Probabilités</th>
                <th className="px-5 py-3 font-bold text-center">Correct</th>
              </tr>
            </thead>
            <tbody>
              {data.map((r, i) => (
                <motion.tr
                  key={r.entity}
                  initial={{ opacity: 0, x: -6 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.022 }}
                  className="border-t border-border/50 hover:bg-secondary/50 transition-colors cursor-default"
                >
                  <td className="px-5 py-3 font-semibold text-foreground">{r.entity}</td>
                  <td className="px-5 py-3">
                    <Pill candidate={r.predicted_candidate} side={r.political_side} />
                  </td>
                  <td className="px-5 py-3">
                    <span className="text-[11px] uppercase font-semibold tracking-wider text-muted-foreground">
                      {r.economic_state}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <Pill candidate={r.real} side="unknown" />
                  </td>
                  <td className="px-5 py-3">
                    <ProbBar macron={r.proba?.MACRON ?? 0} lepen={r.proba?.['LE PEN'] ?? 0} />
                  </td>
                  <td className="px-5 py-3 text-center">
                    {r.is_correct ? (
                      <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
                        <Check className="h-3.5 w-3.5" />
                      </span>
                    ) : (
                      <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-red-100 text-red-500">
                        <X className="h-3.5 w-3.5" />
                      </span>
                    )}
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function Pill({ candidate, side }: { candidate: string; side: string }) {
  const isMacron = candidate === "MACRON";
  const color = isMacron
    ? "var(--color-primary)"
    : candidate === "LE PEN"
    ? "var(--pol-far-right)"
    : "var(--pol-left)";

  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[9px] uppercase tracking-tight text-muted-foreground font-semibold">
        {side?.replace('-', ' ')}
      </span>
      <span
        className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-semibold w-fit"
        style={{
          background: `color-mix(in oklab, ${color} 12%, transparent)`,
          color: color,
        }}
      >
        <span className="h-1.5 w-1.5 rounded-full" style={{ background: color }} />
        {candidate}
      </span>
    </div>
  );
}

function ProbBar({ macron, lepen }: { macron: number; lepen: number }) {
  return (
    <div className="space-y-1.5">
      <div className="flex h-2 w-full overflow-hidden rounded-full bg-secondary">
        <div className="h-full" style={{ width: `${macron}%`, background: "var(--color-primary)" }} />
        <div className="h-full" style={{ width: `${lepen}%`, background: "var(--pol-far-right)" }} />
      </div>
      <div className="flex justify-between text-[10px] text-muted-foreground">
        <span>M {macron.toFixed(1)}%</span>
        <span>LP {lepen.toFixed(1)}%</span>
      </div>
    </div>
  );
}
