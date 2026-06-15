import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import type { PoliticalCount } from "@/lib/predictions";

export function PartyDonut({ title, data }: { title: string; data: PoliticalCount[] }) {
  const total = data.reduce((s, d) => s + d.count, 0);
  const safeData = data.filter((d) => d.count > 0);
  return (
    <div className="rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-xl shadow-[var(--shadow-card)]">
      <div className="flex items-center justify-between">
        <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">{title}</p>
        <span className="text-xs text-muted-foreground">{total} départements</span>
      </div>
      <div className="relative h-56">
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={safeData}
              dataKey="count"
              nameKey="party"
              innerRadius={56}
              outerRadius={84}
              paddingAngle={3}
              stroke="none"
            >
              {safeData.map((d) => (
                <Cell key={d.party} fill={d.color ?? "var(--color-accent)"} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: "var(--color-card)",
                border: "1px solid var(--color-border)",
                borderRadius: 12,
                color: "var(--color-foreground)",
                fontSize: 12,
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-semibold text-foreground">{safeData[0]?.count ?? 0}</span>
          <span className="text-[11px] uppercase tracking-widest text-muted-foreground">{safeData[0]?.party}</span>
        </div>
      </div>
      <div className="mt-2 flex flex-wrap gap-3">
        {data.map((d) => (
          <div key={d.party} className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="h-2.5 w-2.5 rounded-sm" style={{ background: d.color ?? "var(--color-accent)" }} />
            {d.party} <span className="text-foreground">{d.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}