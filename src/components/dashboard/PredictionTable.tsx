import { motion } from "framer-motion";
import type { PredictionEntity } from "@/lib/predictions";
import { Check, X } from "lucide-react";

interface Props {
  data: PredictionEntity[];
  levelLabel: string;
}

const ORIENTATION_COLORS: Record<string, string> = {
  "extreme-gauche": "#800000",
  "gauche":         "#CC0000",
  "centre":         "#D4A017",
  "droite":         "#0066CC",
  "extreme-droite": "#1C3B8A",
  "unknown":        "#888888",
};

const CANDIDATE_COLORS: Record<string, string> = {
  "Macron (LREM)":       "#D4A017",
  "Le Pen (RN)":         "#1C3B8A",
  "Melenchon (LFI)":     "#CC0000",
  "Pecresse (LR)":       "#0066CC",
  "Jadot (EELV)":        "#2D7D2D",
  "Lassalle (Resist)":   "#8B4513",
  "Roussel (PCF)":       "#990000",
  "Hidalgo (PS)":        "#FF69B4",
  "Poutou (NPA)":        "#800000",
  "Arthaud (LO)":        "#660000",
  "Zemmour (Reconv)":    "#003399",
  "Dupont-Aignan (DLF)": "#001F7A",
};

function candidateColor(name: string, side?: string): string {
  return CANDIDATE_COLORS[name] ?? ORIENTATION_COLORS[side ?? "unknown"] ?? "#888888";
}

export function PredictionTable({ data, levelLabel }: Props) {
  return (
    <section className="rounded-3xl border border-border bg-card/50 p-6 md:p-8 backdrop-blur-xl shadow-[var(--shadow-card)]">
      <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-accent">Prédictions — 12 candidats 2022</p>
          <h2 className="mt-1 text-2xl md:text-3xl font-semibold text-foreground">Détail {levelLabel}</h2>
        </div>
      </header>

      {data.length === 0 ? (
        <p className="mt-8 text-sm text-muted-foreground">Aucune donnée à ce niveau.</p>
      ) : (
        <div className="mt-6 overflow-hidden rounded-2xl border border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-secondary/60 text-left text-[11px] uppercase tracking-widest text-muted-foreground">
                <th className="px-4 py-3">Entité</th>
                <th className="px-4 py-3">Prédit (gagnant)</th>
                <th className="px-4 py-3">État Éco</th>
                <th className="px-4 py-3">Réel 2022</th>
                <th className="px-4 py-3 w-[32%]">Top candidats</th>
                <th className="px-4 py-3 text-center">✓</th>
              </tr>
            </thead>
            <tbody>
              {data.map((r, i) => (
                <motion.tr
                  key={r.entity}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.025 }}
                  className="border-t border-border/60 hover:bg-secondary/30"
                >
                  <td className="px-4 py-3 font-medium text-foreground">{r.entity}</td>
                  <td className="px-4 py-3">
                    <Pill candidate={r.predicted} side={r.political_side} />
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs uppercase font-medium tracking-wider text-muted-foreground">
                      {r.economic_state}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Pill candidate={r.real} side="unknown" />
                  </td>
                  <td className="px-4 py-3">
                    <TopBar top5={r.top5} side={r.political_side} />
                  </td>
                  <td className="px-4 py-3 text-center">
                    {r.is_correct ? (
                      <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400">
                        <Check className="h-3.5 w-3.5" />
                      </span>
                    ) : (
                      <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-rose-500/20 text-rose-400">
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
  const color = candidateColor(candidate, side);
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[10px] uppercase tracking-tighter text-muted-foreground font-semibold">
        {side?.replace(/-/g, " ")}
      </span>
      <span
        className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium w-fit"
        style={{
          background: `color-mix(in oklab, ${color} 18%, transparent)`,
          color: color,
        }}
      >
        <span className="h-1.5 w-1.5 rounded-full" style={{ background: color }} />
        {candidate}
      </span>
    </div>
  );
}

function TopBar({ top5, side }: { top5: [string, number][]; side: string }) {
  if (!top5 || top5.length === 0) return null;

  const top3 = top5.slice(0, 3);
  const total = top3.reduce((s, [, v]) => s + v, 0);
  const rest = Math.max(0, 100 - total);

  return (
    <div className="space-y-1.5">
      <div className="flex h-2.5 w-full overflow-hidden rounded-full bg-secondary">
        {top3.map(([name, score]) => (
          <div
            key={name}
            className="h-full"
            style={{ width: `${score}%`, background: candidateColor(name, side) }}
          />
        ))}
        {rest > 0 && (
          <div className="h-full bg-muted/40" style={{ width: `${rest}%` }} />
        )}
      </div>
      <div className="flex flex-wrap gap-x-2 gap-y-0.5">
        {top3.map(([name, score]) => (
          <span key={name} className="text-[10px] text-muted-foreground whitespace-nowrap">
            <span style={{ color: candidateColor(name, side) }}>■</span>{" "}
            {name.split(" ")[0]} {score.toFixed(1)}%
          </span>
        ))}
      </div>
    </div>
  );
}
