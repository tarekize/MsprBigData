import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  // eslint-disable-next-line @typescript-eslint/no-deprecated
  CartesianGrid, Cell, PieChart, Pie, Legend,
} from "recharts";
import {
  BarChart3, Brain, MapPin, CheckCircle2, XCircle,
  TrendingUp, Activity, Home,
} from "lucide-react";

export const Route = createFileRoute("/dashboard")({
  component: DashboardPage,
});

const MODELS = [
  { id: "xgboost",             name: "XGBoost",             key: "XGBoost" },
  { id: "random_forest",       name: "Random Forest",       key: "RandomForest" },
  { id: "gradient_boosting",   name: "Gradient Boosting",   key: "GradientBoosting" },
  { id: "logistic_regression", name: "Logistic Regression", key: "LogisticRegression" },
  { id: "svm_(linear)",        name: "SVM (Linear)",        key: "SVM" },
];

const DEPT_COLORS = [
  "#6366f1", "#8b5cf6", "#a78bfa", "#06b6d4", "#10b981",
  "#22c55e", "#84cc16", "#eab308", "#f97316", "#ef4444", "#ec4899", "#14b8a6",
];

type Entity = {
  entity: string;
  real: string;
  predicted: string;
  is_correct: boolean;
  economic_state?: string;
  economic_score?: number;
  proba_macron?: number;
  proba_lepen?: number;
  confidence?: string;
  parent?: string;
};

function FrenchFlag() {
  return (
    <div className="flex shrink-0">
      <div className="h-[18px] w-[8px] rounded-l-sm" style={{ background: "#002395" }} />
      <div className="h-[18px] w-[8px] bg-white" />
      <div className="h-[18px] w-[8px] rounded-r-sm" style={{ background: "#ED2939" }} />
    </div>
  );
}

function Card({ title, children, className = "" }: { title?: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-card rounded-2xl border border-border shadow-[var(--shadow-card)] ${className}`}>
      {title && (
        <div className="px-5 pt-5 pb-0">
          <p className="text-[13px] font-semibold text-foreground">{title}</p>
        </div>
      )}
      <div className={title ? "p-5 pt-4" : "p-5"}>{children}</div>
    </div>
  );
}

function NavItem({
  icon: Icon,
  label,
  sub,
  active = false,
  href,
  onClick,
}: {
  icon: React.ElementType;
  label: string;
  sub: string;
  active?: boolean;
  href?: string;
  onClick?: () => void;
}) {
  const content = (
    <div
      onClick={onClick}
      className={`flex items-center gap-3 px-3 py-2.5 rounded-xl mb-1 cursor-pointer transition-all ${
        active
          ? "bg-primary/10 border border-primary/20"
          : "hover:bg-secondary border border-transparent"
      }`}
    >
      <Icon className={`w-4 h-4 shrink-0 ${active ? "text-primary" : "text-muted-foreground"}`} />
      <div>
        <p className={`text-[13px] font-semibold leading-tight ${active ? "text-primary" : "text-foreground/75"}`}>
          {label}
        </p>
        <p className={`text-[10px] ${active ? "text-primary/60" : "text-muted-foreground"}`}>{sub}</p>
      </div>
    </div>
  );

  if (href) {
    return (
      <Link to={href} className="block no-underline">
        {content}
      </Link>
    );
  }
  return content;
}

function DashboardPage() {
  const [selectedModel, setSelectedModel] = useState("logistic_regression");
  const [selectedDept, setSelectedDept] = useState("ALL");
  const [selectedCanton, setSelectedCanton] = useState("ALL");

  const { data: baseData } = useQuery({
    queryKey: ["base_predictions"],
    queryFn: async () => {
      const r = await fetch("/data/predictions.json");
      if (!r.ok) throw new Error("predictions.json manquant");
      return r.json();
    },
    staleTime: Infinity,
  });

  const { data, isLoading } = useQuery({
    queryKey: ["predictions", selectedModel],
    queryFn: async () => {
      const r = await fetch(`/data/predictions_${selectedModel}.json`, { cache: "no-store" });
      if (!r.ok) throw new Error(`predictions_${selectedModel}.json manquant`);
      return r.json();
    },
    staleTime: 30_000,
  });

  const activeEntity = useMemo<Entity | null>(() => {
    if (!data) return null;
    if (selectedDept === "ALL") return data.levels?.region?.[0] ?? null;
    const dept = data.levels?.departement?.find((d: Entity) => d.entity === selectedDept) ?? null;
    if (!dept || selectedCanton === "ALL") return dept;
    return data.levels?.canton?.find((c: Entity) => c.entity === selectedCanton) ?? dept;
  }, [data, selectedDept, selectedCanton]);

  const tableData = useMemo<Entity[]>(() => {
    if (!data) return [];
    if (selectedDept === "ALL") return data.levels?.departement ?? [];
    const cantons = (data.levels?.canton ?? []).filter((c: Entity) => c.parent === selectedDept);
    if (selectedCanton === "ALL") return cantons;
    return cantons.filter((c: Entity) => c.entity === selectedCanton);
  }, [data, selectedDept, selectedCanton]);

  const selectedModelDef = MODELS.find(m => m.id === selectedModel)!;
  const metrics = baseData?.models_metrics ?? {};

  const activeAcc: number | null =
    metrics[selectedModelDef.key]?.test_accuracy ??
    data?.summary?.model_accuracy ??
    null;

  const ecoState = activeEntity?.economic_state?.toUpperCase() ?? "—";
  const ecoScore = activeEntity?.economic_score?.toFixed(1) ?? "—";

  const barData = MODELS.map(m => ({
    name: m.name,
    accuracy: metrics[m.key]?.test_accuracy ?? 0,
    active: m.id === selectedModel,
    fill: m.id === selectedModel ? "#4f46e5" : "#a5b4fc",
  }));

  const donutData = activeEntity
    ? [
        { name: "Macron", value: +(activeEntity.proba_macron ?? 0).toFixed(1), fill: "#3b82f6" },
        { name: "Le Pen",  value: +(activeEntity.proba_lepen  ?? 0).toFixed(1), fill: "#ef4444" },
      ]
    : [];

  return (
    <div className="flex h-screen overflow-hidden">

      {/* Sidebar */}
      <aside className="w-60 shrink-0 flex flex-col bg-card border-r border-border overflow-y-auto">

        {/* Brand */}
        <div className="px-5 py-5 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-primary flex items-center justify-center">
              <FrenchFlag />
            </div>
            <div>
              <p className="text-foreground font-bold text-[14px] leading-tight">GouvData</p>
              <p className="text-muted-foreground text-[10px] uppercase tracking-widest">ML Analytics</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <div className="px-3 pt-5 flex-1">
          <p className="text-muted-foreground text-[9px] font-bold uppercase tracking-[0.18em] mb-2 px-2">
            Navigation
          </p>
          <NavItem icon={BarChart3} label="Dashboard" sub="Prédictions géographiques" active />
          <NavItem icon={Brain}     label="Visualisation ML" sub="Graphiques & métriques"       href="/visualisation" />
          <NavItem icon={Home}      label="Accueil"          sub="Vue d'ensemble"                href="/" />
        </div>

        {/* Context */}
        <div className="px-5 py-4 border-t border-border space-y-3">
          <p className="text-muted-foreground text-[9px] font-bold uppercase tracking-[0.18em]">Périmètre</p>
          <div className="flex items-start gap-2.5">
            <Activity className="text-muted-foreground w-3.5 h-3.5 mt-0.5 shrink-0" />
            <div>
              <p className="text-muted-foreground text-[10px]">Élection</p>
              <p className="text-foreground font-semibold text-[12px]">Présidentielle 2022</p>
            </div>
          </div>
          <div className="flex items-start gap-2.5">
            <MapPin className="text-muted-foreground w-3.5 h-3.5 mt-0.5 shrink-0" />
            <div>
              <p className="text-muted-foreground text-[10px]">Région</p>
              <p className="text-foreground font-semibold text-[12px]">Nouvelle-Aquitaine</p>
            </div>
          </div>
        </div>

        {/* Active model */}
        <div className="px-5 pb-4">
          <p className="text-muted-foreground text-[9px] font-bold uppercase tracking-[0.18em] mb-2">Modèle actif</p>
          <motion.div
            key={selectedModel}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-secondary rounded-xl p-3 border border-border"
          >
            <div className="flex items-center gap-2 mb-2">
              <Brain className="text-primary w-3.5 h-3.5 shrink-0" />
              <p className="text-foreground font-semibold text-[12px] leading-tight">{selectedModelDef.name}</p>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground text-[11px]">Accuracy</span>
              <span className="text-foreground font-bold text-[13px]">
                {activeAcc != null ? `${activeAcc.toFixed(1)}%` : "—"}
              </span>
            </div>
          </motion.div>
        </div>

        {/* Active filter summary */}
        {selectedDept !== "ALL" && (
          <div className="px-5 pb-5 border-t border-border pt-4">
            <p className="text-muted-foreground text-[9px] font-bold uppercase tracking-[0.18em] mb-1.5">Vue active</p>
            <p className="text-foreground font-semibold text-[12px]">{selectedDept}</p>
            {selectedCanton !== "ALL" && (
              <p className="text-muted-foreground text-[11px] mt-0.5">Canton : {selectedCanton}</p>
            )}
            <button
              onClick={() => { setSelectedDept("ALL"); setSelectedCanton("ALL"); }}
              className="mt-2 text-primary text-[11px] hover:underline bg-transparent border-none cursor-pointer p-0"
            >
              Réinitialiser →
            </button>
          </div>
        )}
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto bg-background">

        {/* Top header */}
        <div className="px-8 py-5 bg-card border-b border-border">
          <div className="flex items-center justify-between">
            <div>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-widest px-3 py-1 border border-primary/20 mb-2">
                Présidentielle 2022 · Nouvelle-Aquitaine
              </span>
              <h1 className="text-foreground font-bold text-[22px] tracking-tight leading-tight">
                Tableau de Bord Prédictif
              </h1>
              <p className="text-muted-foreground text-[13px] mt-0.5">
                Prédiction du vote par indicateurs socio-économiques · Région · Département · Canton
              </p>
            </div>
            <Link
              to="/visualisation"
              className="inline-flex items-center gap-2 bg-primary text-primary-foreground rounded-xl px-5 py-2.5 text-[13px] font-semibold shadow-md shadow-primary/20 hover:bg-primary/90 hover:shadow-lg transition-all no-underline"
            >
              <BarChart3 className="w-4 h-4" />
              Visualisation ML
            </Link>
          </div>
        </div>

        {/* Content */}
        <div className="px-8 py-6 space-y-5 max-w-[1280px]">

          {/* Model selector */}
          <Card title="Modèle d'Intelligence Artificielle">
            <div className="grid grid-cols-5 gap-3 mt-1">
              {MODELS.map(m => {
                const acc = metrics[m.key]?.test_accuracy ?? null;
                const active = m.id === selectedModel;
                return (
                  <motion.button
                    key={m.id}
                    onClick={() => { setSelectedModel(m.id); setSelectedDept("ALL"); setSelectedCanton("ALL"); }}
                    whileHover={{ scale: 1.03, y: -1 }}
                    whileTap={{ scale: 0.97 }}
                    className={`rounded-xl p-4 text-center border cursor-pointer transition-all ${
                      active
                        ? "bg-primary border-primary/0 shadow-lg shadow-primary/20 text-primary-foreground"
                        : "bg-card border-border hover:border-primary/30 hover:shadow-sm"
                    }`}
                  >
                    <p className={`text-[9px] font-bold uppercase tracking-widest mb-1.5 ${
                      active ? "text-primary-foreground/70" : "text-muted-foreground"
                    }`}>
                      Modèle
                    </p>
                    <p className={`font-semibold text-[12px] mb-3 leading-tight ${
                      active ? "text-primary-foreground" : "text-foreground"
                    }`}>
                      {m.name}
                    </p>
                    <p className={`font-bold text-[22px] tracking-tight ${
                      active ? "text-primary-foreground" : "text-primary"
                    }`}>
                      {acc != null ? `${acc.toFixed(1)}%` : "—"}
                    </p>
                  </motion.button>
                );
              })}
            </div>
          </Card>

          {/* KPI cards */}
          <AnimatePresence mode="wait">
            <motion.div
              key={`${selectedModel}-${selectedDept}-${selectedCanton}`}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-3 gap-4"
            >
              {[
                {
                  label: `Vainqueur Prédit — ${activeEntity?.entity ?? "Nouvelle-Aquitaine"}`,
                  value: activeEntity?.predicted ?? (isLoading ? "…" : "—"),
                  sub:   `Résultat réel : ${activeEntity?.real ?? "—"}`,
                  correct: activeEntity ? activeEntity.is_correct : null,
                  accent: "border-l-primary",
                  bg: "bg-card",
                },
                {
                  label: "État Économique",
                  value: isLoading ? "…" : ecoState,
                  sub:   `Score : ${ecoScore}`,
                  correct: null,
                  accent: "border-l-amber-400",
                  bg: "bg-card",
                },
                {
                  label: `Accuracy — ${selectedModelDef.name}`,
                  value: activeAcc != null ? `${activeAcc.toFixed(1)}%` : (isLoading ? "…" : "—"),
                  sub:   "Sur l'ensemble d'entraînement socio-éco",
                  correct: null,
                  accent: "border-l-emerald-500",
                  bg: "bg-card",
                },
              ].map((kpi, i) => (
                <motion.div
                  key={i}
                  transition={{ delay: i * 0.06 }}
                  className={`${kpi.bg} rounded-2xl border border-border border-l-4 ${kpi.accent} p-5 shadow-[var(--shadow-card)]`}
                >
                  <div className="flex items-start justify-between mb-3 gap-2">
                    <p className="text-muted-foreground text-[10px] font-bold uppercase tracking-widest leading-snug">
                      {kpi.label}
                    </p>
                    {kpi.correct === true  && <CheckCircle2 className="text-emerald-500 w-4 h-4 shrink-0 mt-0.5" />}
                    {kpi.correct === false && <XCircle      className="text-destructive w-4 h-4 shrink-0 mt-0.5" />}
                  </div>
                  <p className="text-foreground font-bold text-[32px] tracking-tight leading-none mb-2">
                    {kpi.value}
                  </p>
                  <p className="text-muted-foreground text-[12px]">{kpi.sub}</p>
                </motion.div>
              ))}
            </motion.div>
          </AnimatePresence>

          {/* Geographic filters */}
          <Card title="Filtres géographiques">
            <div className="grid grid-cols-3 gap-4 mt-1">
              <div>
                <label className="text-muted-foreground text-[10px] font-bold uppercase tracking-widest block mb-2">
                  Région
                </label>
                <div className="bg-secondary border border-border rounded-lg px-3 py-2.5 text-foreground/50 text-[13px] flex justify-between items-center select-none">
                  Nouvelle-Aquitaine
                </div>
              </div>

              <div>
                <label className="text-muted-foreground text-[10px] font-bold uppercase tracking-widest block mb-2">
                  Département
                </label>
                <select
                  value={selectedDept}
                  onChange={e => { setSelectedDept(e.target.value); setSelectedCanton("ALL"); }}
                  className="w-full bg-card border border-border rounded-lg px-3 py-2.5 text-foreground text-[13px] cursor-pointer outline-none focus:border-primary transition-colors appearance-auto"
                >
                  <option value="ALL">Tous les départements</option>
                  {data?.levels?.departement?.map((d: Entity) => (
                    <option key={d.entity} value={d.entity}>{d.entity}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-muted-foreground text-[10px] font-bold uppercase tracking-widest block mb-2">
                  Canton
                </label>
                <select
                  value={selectedCanton}
                  onChange={e => setSelectedCanton(e.target.value)}
                  disabled={selectedDept === "ALL"}
                  className="w-full bg-card border border-border rounded-lg px-3 py-2.5 text-foreground text-[13px] cursor-pointer outline-none focus:border-primary transition-colors appearance-auto disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <option value="ALL">Tous les cantons</option>
                  {data?.levels?.canton
                    ?.filter((c: Entity) => c.parent === selectedDept)
                    .map((c: Entity) => (
                      <option key={c.entity} value={c.entity}>{c.entity}</option>
                    ))}
                </select>
              </div>
            </div>
          </Card>

          {/* Charts row */}
          <div className="grid grid-cols-[2fr_1fr] gap-5">

            {/* Bar chart */}
            <div className="bg-card rounded-2xl border border-border p-5 shadow-[var(--shadow-card)]">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="w-4 h-4 text-primary shrink-0" />
                <p className="text-foreground font-semibold text-[14px]">Comparaison Accuracy — 5 Modèles</p>
              </div>
              <p className="text-muted-foreground text-[11px] mb-4">Cliquez sur un modèle ci-dessus pour changer la vue</p>
              {barData.some(d => d.accuracy > 0) ? (
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={barData} barSize={34}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                    <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis domain={[50, 100]} tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} unit="%" />
                    <Tooltip
                      formatter={(v: unknown) => [`${Number(v).toFixed(2)}%`, "Accuracy"] as [string, string]}
                      contentStyle={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 10, fontSize: 12, boxShadow: "0 4px 12px rgba(0,0,0,0.06)" }}
                      cursor={{ fill: "#f8fafc" }}
                    />
                    <Bar dataKey="accuracy" radius={[5, 5, 0, 0]}>
                      {barData.map((entry, i) => (
                        // eslint-disable-next-line @typescript-eslint/no-deprecated
                        <Cell key={i} fill={entry.fill} opacity={entry.active ? 1 : 0.6} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[220px] flex items-center justify-center text-muted-foreground text-[13px]">
                  Chargement des métriques…
                </div>
              )}
            </div>

            {/* Donut chart */}
            <div className="bg-card rounded-2xl border border-border p-5 shadow-[var(--shadow-card)]">
              <p className="text-foreground font-semibold text-[14px] mb-1">Probabilités prédites</p>
              <p className="text-muted-foreground text-[11px] mb-2">
                {activeEntity?.entity ?? "Nouvelle-Aquitaine"}
              </p>
              {donutData.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={donutData}
                      cx="50%" cy="50%"
                      innerRadius={58} outerRadius={86}
                      paddingAngle={3}
                      dataKey="value"
                      label={({ name, value }) => `${name} ${value}%`}
                      labelLine={false}
                    >
                      {donutData.map((entry, i) => (
                        // eslint-disable-next-line @typescript-eslint/no-deprecated
                        <Cell key={i} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Legend formatter={(v) => <span style={{ color: "#64748b", fontSize: 12 }}>{v}</span>} />
                    <Tooltip
                      formatter={(v: unknown) => [`${Number(v)}%`] as [string]}
                      contentStyle={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 10, fontSize: 12 }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[220px] flex items-center justify-center text-muted-foreground text-[13px]">
                  {isLoading ? "Chargement…" : "Sélectionnez un département"}
                </div>
              )}
            </div>
          </div>

          {/* Results table */}
          {tableData.length > 0 && (
            <div className="bg-card rounded-2xl border border-border shadow-[var(--shadow-card)] overflow-hidden">
              <div className="px-5 py-4 border-b border-border">
                <p className="text-[13px] font-semibold text-foreground">
                  Résultats —{" "}
                  {selectedDept === "ALL"
                    ? "Départements"
                    : selectedCanton === "ALL"
                    ? `Cantons de ${selectedDept}`
                    : selectedCanton}
                </p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-[13px] border-collapse">
                  <thead>
                    <tr className="bg-secondary">
                      {["Entité", "Prédit", "Réel", "Correct", "Macron %", "Le Pen %", "Conf."].map(h => (
                        <th key={h} className="px-4 py-3 text-left text-muted-foreground font-bold text-[10px] uppercase tracking-widest border-b border-border">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {tableData.slice(0, 30).map((row: Entity, i: number) => (
                      <motion.tr
                        key={i}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: i * 0.018 }}
                        className="border-b border-border/50 hover:bg-secondary/60 transition-colors cursor-default"
                      >
                        <td className="px-4 py-3 font-semibold text-foreground">{row.entity}</td>
                        <td className="px-4 py-3">
                          <span className={`rounded-md px-2.5 py-0.5 text-[11px] font-bold ${
                            row.predicted === "MACRON"
                              ? "bg-primary/10 text-primary"
                              : "bg-destructive/10 text-destructive"
                          }`}>
                            {row.predicted}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-foreground/60">{row.real}</td>
                        <td className="px-4 py-3">
                          {row.is_correct
                            ? <CheckCircle2 className="text-emerald-500 w-4 h-4" />
                            : <XCircle      className="text-destructive w-4 h-4" />}
                        </td>
                        <td className="px-4 py-3 text-foreground/60">
                          {row.proba_macron != null ? `${row.proba_macron.toFixed(1)}%` : "—"}
                        </td>
                        <td className="px-4 py-3 text-foreground/60">
                          {row.proba_lepen != null ? `${row.proba_lepen.toFixed(1)}%` : "—"}
                        </td>
                        <td className="px-4 py-3 text-muted-foreground">{row.confidence ?? "—"}</td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {tableData.length > 30 && (
                <p className="text-muted-foreground text-[12px] py-3 text-center border-t border-border">
                  {tableData.length - 30} lignes supplémentaires — affinez le filtre canton pour en voir plus
                </p>
              )}
            </div>
          )}

          {/* Department color palette */}
          <div className="flex flex-col items-center gap-2 pb-6">
            <div className="flex gap-2 flex-wrap justify-center">
              {DEPT_COLORS.map((c, i) => (
                <motion.div
                  key={i}
                  whileHover={{ scale: 1.25 }}
                  className="w-5 h-5 rounded-md"
                  style={{ background: c }}
                />
              ))}
            </div>
            <p className="text-muted-foreground text-[12px]">12 départements · Nouvelle-Aquitaine</p>
          </div>

          {isLoading && (
            <div className="flex flex-col items-center gap-3 py-10 text-muted-foreground text-[13px]">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                className="w-5 h-5 border-2 border-border border-t-primary rounded-full"
              />
              Chargement des prédictions…
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
