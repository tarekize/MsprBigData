import { createFileRoute, Link } from "@tanstack/react-router";
import { useQueries } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { useState, useMemo, useEffect } from "react";
import { type PredictionEntity } from "@/lib/predictions";
import { PoliticalSpectrum } from "@/components/dashboard/PoliticalSpectrum";
import { PartyDonut } from "@/components/dashboard/PartyDonut";
import { PredictionTable } from "@/components/dashboard/PredictionTable";
import { Activity, Brain, MapPin, Filter, BarChart3, Home, Vote } from "lucide-react";

export const Route = createFileRoute("/")({
  component: Index,
});

const SUPERVISED_MODELS = [
  { id: "logistic_regression", name: "Logistic Regression" },
  { id: "xgboost", name: "XGBoost" },
  { id: "hist_gradient_boosting", name: "HistGradient Boosting" },
  { id: "random_forest", name: "Random Forest" },
  { id: "linear_svm", name: "Linear SVM" },
];

const itemVariant = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

interface TendancePrediction {
  annee: string;
  year: number;
  is_base: boolean;
  exg: number;
  gauche: number;
  centre: number;
  droite: number;
  exd: number;
  confidence?: number;
}
interface TendancesJSON {
  metadata: { model: string; model_accuracy: number; base_year: number; forecast_years: number[] };
  deltas: Record<string, number>;
  predictions: TendancePrediction[];
}

const BLOCS_PREVIEW = [
  { key: "exg", label: "Extrême G.", color: "#b91c1c" },
  { key: "gauche", label: "Gauche", color: "#ef4444" },
  { key: "centre", label: "Centre", color: "#eab308" },
  { key: "droite", label: "Droite", color: "#3b82f6" },
  { key: "exd", label: "Extrême D.", color: "#1d4ed8" },
] as const;

function Index() {
  const [selectedModel, setSelectedModel] = useState<string>("logistic_regression");
  const [tendances, setTendances] = useState<TendancesJSON | null>(null);
  const [selectedTendanceYear, setSelectedTendanceYear] = useState<number>(2020);

  useEffect(() => {
    fetch("/data/predictions_tendances.json")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d: TendancesJSON) => setTendances(d))
      .catch(() => {});
  }, []);

  const MODELS = SUPERVISED_MODELS;

  // Charge les prédictions réelles de chaque modèle (JSON générés depuis les CSV).
  const results = useQueries({
    queries: MODELS.map((m) => ({
      queryKey: ["predictions", m.id],
      queryFn: async () => {
        const res = await fetch(`/data/predictions_${m.id}.json`, { cache: "no-store" });
        if (!res.ok) throw new Error("Les prédictions de ce modèle ne sont pas disponibles.");
        return res.json();
      },
      staleTime: Infinity,
    })),
  });

  const activeIndex = MODELS.findIndex((m) => m.id === selectedModel);
  const data = results[activeIndex]?.data;
  const isLoading = results[activeIndex]?.isLoading;
  const error = results[activeIndex]?.error;

  const [selectedDept, setSelectedDept] = useState<string>("ALL");
  const [selectedCanton, setSelectedCanton] = useState<string>("ALL");

  const { activeEntity, tableLevel, tableData } = useMemo(() => {
    if (!data) return { activeEntity: null, tableLevel: "Région", tableData: [] };

    let active = data.levels.region[0];
    let tLevel = "Départements";
    let tData = data.levels.departement || [];

    if (selectedDept !== "ALL") {
      active =
        data.levels.departement.find((d: PredictionEntity) => d.entity === selectedDept) || active;
      tLevel = "Cantons";
      tData = (data.levels.canton || []).filter((c: PredictionEntity) => c.parent === selectedDept);

      if (selectedCanton !== "ALL") {
        active =
          data.levels.canton.find((c: PredictionEntity) => c.entity === selectedCanton) || active;
        tLevel = "Canton Sélectionné";
        tData = [active];
      }
    }

    return { activeEntity: active, tableLevel: tLevel, tableData: tData };
  }, [data, selectedDept, selectedCanton]);

  const activeModelName = data?.summary.model_name ?? MODELS[activeIndex]?.name ?? "—";
  const activeAccuracy = data ? `${data.summary.model_accuracy}%` : "—";
  const winnerShort = (activeEntity?.predicted ?? "").split(" ")[0].toUpperCase() || "—";
  const realShort = (activeEntity?.real ?? "").split(" ")[0].toUpperCase() || "—";

  return (
    <div className="theme-light-violet flex min-h-screen w-full bg-background text-foreground">
      {/* Sidebar */}
      <aside className="sticky top-0 hidden h-screen w-72 shrink-0 flex-col border-r border-border bg-card lg:flex">
        <div className="flex items-center gap-3 border-b border-border px-6 py-5">
          <FlagFR className="h-7 w-10" />
          <div className="leading-tight">
            <p className="text-sm font-bold tracking-wide text-foreground">GouvData</p>
            <p className="text-[10px] font-medium uppercase tracking-[0.18em] text-muted-foreground">
              ML Analytics
            </p>
          </div>
        </div>

        <nav className="flex-1 space-y-7 overflow-y-auto px-4 py-6">
          <SideSection title="Navigation">
            <SideLink
              to="/"
              active
              icon={<Home className="h-4 w-4" />}
              label="Dashboard"
              sub="Prédictions géographiques"
            />
            <SideLink
              to="/visualisation"
              icon={<BarChart3 className="h-4 w-4" />}
              label="Visualisation ML"
              sub="Graphiques & métriques"
            />
          </SideSection>

          <SideSection title="Périmètre">
            <SideInfo
              icon={<Vote className="h-4 w-4" />}
              label="Élection"
              value="Présidentielle 2022"
            />
            <SideInfo
              icon={<MapPin className="h-4 w-4" />}
              label="Région"
              value="Nouvelle-Aquitaine"
            />
          </SideSection>

          <SideSection title="Modèle actif">
            <div
              className="rounded-xl border border-primary/20 px-4 py-3"
              style={{ backgroundColor: "var(--primary-light)" }}
            >
              <div className="flex items-center gap-2 font-semibold text-primary">
                <Activity className="h-4 w-4" />
                <span className="truncate">{activeModelName}</span>
              </div>
              <div className="mt-2 flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Accuracy</span>
                <span className="font-bold text-primary">{activeAccuracy}</span>
              </div>
            </div>
          </SideSection>
        </nav>

        <div className="flex flex-col items-center gap-1.5 border-t border-border px-6 py-5">
          <FlagFR className="h-6 w-9" />
          <span className="text-[10px] font-medium uppercase tracking-[0.22em] text-muted-foreground">
            France
          </span>
        </div>
      </aside>

      {/* Main content */}
      <main className="min-w-0 flex-1">
        <div className="mx-auto max-w-6xl space-y-8 px-6 py-10 md:py-12">
          {/* Header */}
          <motion.header
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-3 text-center"
          >
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-accent">
              Présidentielle 2022 · Nouvelle-Aquitaine
            </p>
            <h1 className="text-4xl font-bold tracking-tight text-foreground md:text-5xl">
              Tableau de Bord Prédictif
            </h1>
            <p className="mx-auto max-w-2xl text-sm text-muted-foreground md:text-base">
              Prédiction du vote par indicateurs socio-économiques · Région · Département · Canton
            </p>
            <div className="pt-2">
              <Link
                to="/visualisation"
                className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/25 transition-all hover:scale-[1.03] hover:bg-primary-dark"
              >
                <BarChart3 className="h-4 w-4" />
                Visualisation ML
              </Link>
            </div>
          </motion.header>

          {error && (
            <div className="rounded-2xl border border-destructive/40 bg-destructive/10 p-5 text-sm text-destructive">
              Impossible de charger les prédictions de ce modèle. Lance le notebook ML pour les
              générer dans <code>/public/data/</code>.
            </div>
          )}

          {/* Modèles d'IA */}
          <motion.section
            variants={itemVariant}
            initial="hidden"
            animate="show"
            className="rounded-3xl border border-border bg-card p-5 shadow-[var(--shadow-card)] md:p-6"
          >
            <div className="mb-4 flex items-center gap-2">
              <Brain className="h-4 w-4 text-primary" />
              <span className="text-sm font-semibold text-foreground">
                Modèle d'Intelligence Artificielle
              </span>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
              {MODELS.map((m, i) => {
                const acc = results[i]?.data?.summary?.model_accuracy;
                const isActive = m.id === selectedModel;
                return (
                  <button
                    key={m.id}
                    onClick={() => setSelectedModel(m.id)}
                    className={`rounded-2xl border p-4 text-left transition-all ${
                      isActive
                        ? "border-primary bg-primary text-primary-foreground shadow-lg shadow-primary/30"
                        : "border-border bg-secondary/40 hover:border-primary/40 hover:bg-secondary"
                    }`}
                  >
                    <p
                      className={`text-[10px] font-medium uppercase tracking-wider ${
                        isActive ? "text-primary-foreground/70" : "text-muted-foreground"
                      }`}
                    >
                      Modèle
                    </p>
                    <p
                      className={`mt-1 text-sm font-semibold ${
                        isActive ? "text-primary-foreground" : "text-foreground"
                      }`}
                    >
                      {m.name}
                    </p>
                    <p
                      className={`mt-1 text-lg font-bold ${
                        isActive ? "text-primary-foreground" : "text-primary"
                      }`}
                    >
                      {acc != null ? `${acc}%` : "…"}
                    </p>
                  </button>
                );
              })}
            </div>
          </motion.section>

          {/* Cartes de résultats */}
          <section className="grid gap-4 md:grid-cols-3">
            <ResultCard
              label={`Vainqueur prédit — ${activeEntity?.entity || "—"}`}
              value={winnerShort}
              hint={`Résultat réel : ${realShort}`}
              delay={0}
            />
            <ResultCard
              label="État économique"
              value={activeEntity?.economic_state?.toUpperCase() ?? "—"}
              hint={`Score : ${activeEntity?.economic_score?.toFixed(1) ?? "—"}`}
              delay={0.05}
            />
            <ResultCard
              label={`Accuracy — ${activeModelName}`}
              value={activeAccuracy}
              hint="Sur l'ensemble d'entraînement socio-éco"
              delay={0.1}
            />
          </section>

          {/* Filtres géographiques */}
          {data && (
            <section className="rounded-3xl border border-border bg-card p-6 shadow-[var(--shadow-card)]">
              <div className="mb-4 flex items-center gap-2">
                <Filter className="h-4 w-4 text-primary" />
                <span className="text-sm font-semibold text-foreground">Filtres géographiques</span>
              </div>
              <div className="flex flex-wrap gap-4">
                <div className="flex min-w-[200px] flex-1 flex-col gap-2">
                  <label className="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">
                    Région
                  </label>
                  <select
                    disabled
                    aria-label="Région"
                    title="Sélectionnez une région"
                    className="rounded-xl border border-border bg-secondary/50 px-4 py-3 text-sm text-foreground opacity-70"
                  >
                    <option>Nouvelle-Aquitaine</option>
                  </select>
                </div>

                <div className="flex min-w-[200px] flex-1 flex-col gap-2">
                  <label className="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">
                    Département
                  </label>
                  <select
                    value={selectedDept}
                    onChange={(e) => {
                      setSelectedDept(e.target.value);
                      setSelectedCanton("ALL");
                    }}
                    className="rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground outline-none transition-colors focus:border-primary"
                  >
                    <option value="ALL">Tous les départements</option>
                    {data.levels.departement?.map((d: PredictionEntity) => (
                      <option key={d.entity} value={d.entity}>
                        {d.entity}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex min-w-[200px] flex-1 flex-col gap-2">
                  <label className="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">
                    Canton
                  </label>
                  <select
                    value={selectedCanton}
                    onChange={(e) => setSelectedCanton(e.target.value)}
                    disabled={selectedDept === "ALL"}
                    aria-label="Canton"
                    className="rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground outline-none transition-colors focus:border-primary disabled:opacity-50"
                  >
                    <option value="ALL">Tous les cantons</option>
                    {selectedDept !== "ALL" &&
                      data.levels.canton
                        ?.filter((c: PredictionEntity) => c.parent === selectedDept)
                        .map((c: PredictionEntity) => (
                          <option key={c.entity} value={c.entity}>
                            {c.entity}
                          </option>
                        ))}
                  </select>
                </div>
              </div>
            </section>
          )}

          {/* Spectre politique de l'entité active */}
          {activeEntity && (
            <PoliticalSpectrum
              entityName={activeEntity.entity}
              ecoState={activeEntity.economic_state}
            />
          )}

          {/* Tables */}
          {data && <PredictionTable data={tableData} levelLabel={tableLevel} />}

          {/* Prévision tendances 5 blocs */}
          {tendances && (
            <motion.section
              variants={itemVariant}
              initial="hidden"
              animate="show"
              className="rounded-3xl border border-border bg-card p-6 shadow-[var(--shadow-card)]"
            >
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-accent">
                    Prévision électorale à moyen terme · {tendances.metadata.model}
                  </p>
                  <h2 className="mt-1 text-lg font-semibold tracking-tight text-foreground">
                    Tendances {tendances.metadata.forecast_years.join(" · ")} — 5 Blocs Politiques
                  </h2>
                </div>
                <Link
                  to="/visualisation"
                  className="shrink-0 rounded-full border border-border bg-secondary/60 px-4 py-2 text-xs text-muted-foreground transition-all hover:border-primary/50 hover:text-foreground"
                >
                  Voir les graphiques →
                </Link>
              </div>
              <p className="mb-4 text-xs text-muted-foreground">
                % de territoires projetés par orientation politique — prédictions{" "}
                {tendances.metadata.model} ({tendances.metadata.model_accuracy}% acc.) sur
                indicateurs delta socio-économiques. Base {tendances.metadata.base_year}.
              </p>

              {/* Sélecteur d'année */}
              <div className="mb-4 flex flex-wrap gap-2">
                {tendances.predictions.map((p) => (
                  <button
                    key={p.year}
                    onClick={() => setSelectedTendanceYear(p.year)}
                    className={`rounded-full border px-3 py-1 text-xs font-semibold transition-all ${
                      selectedTendanceYear === p.year
                        ? "border-primary bg-primary/15 text-primary"
                        : "border-border bg-secondary/40 text-muted-foreground hover:border-primary/50 hover:text-foreground"
                    }`}
                  >
                    {p.year}
                    {p.is_base ? " (base)" : ""}
                    {p.confidence != null && !p.is_base && (
                      <span className="ml-1 opacity-60">· {p.confidence}%</span>
                    )}
                  </button>
                ))}
              </div>

              {/* Cartes 5 blocs pour l'année sélectionnée */}
              {(() => {
                const basePred =
                  tendances.predictions.find((p) => p.is_base) ?? tendances.predictions[0];
                const yearPred =
                  tendances.predictions.find((p) => p.year === selectedTendanceYear) ?? basePred;
                return (
                  <>
                    <div className="grid gap-3 sm:grid-cols-5">
                      {BLOCS_PREVIEW.map((bloc) => {
                        const val = yearPred?.[bloc.key] ?? 0;
                        const base = basePred?.[bloc.key] ?? 0;
                        const delta = +(val - base).toFixed(2);
                        const isUp = delta > 0;
                        const deltaColor =
                          bloc.key === "centre"
                            ? isUp
                              ? "text-emerald-500"
                              : "text-rose-500"
                            : isUp
                              ? "text-amber-500"
                              : "text-emerald-500";
                        return (
                          <div
                            key={bloc.key}
                            className="rounded-2xl border border-border bg-secondary/30 p-3 text-center"
                          >
                            <p className="text-[10px] font-medium uppercase leading-tight tracking-wider text-muted-foreground">
                              {bloc.label}
                            </p>
                            <p className="mt-2 text-xl font-bold" style={{ color: bloc.color }}>
                              {val.toFixed(1)}%
                            </p>
                            {yearPred?.is_base ? (
                              <p className="mt-1 text-xs text-muted-foreground">base</p>
                            ) : (
                              <p className={`mt-1 text-xs font-semibold ${deltaColor}`}>
                                {isUp ? "+" : ""}
                                {delta}pp vs {basePred?.year}
                              </p>
                            )}
                            <div className="mt-2 h-1 rounded-full bg-border">
                              <div
                                className="h-1 rounded-full"
                                style={{
                                  width: `${Math.min(val, 100)}%`,
                                  backgroundColor: bloc.color,
                                  opacity: 0.7,
                                }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                    {!yearPred?.is_base && (
                      <div className="mt-4 rounded-xl border border-rose-500/20 bg-rose-500/5 px-4 py-2.5 text-xs text-rose-600">
                        <strong>
                          {yearPred?.year} vs {basePred?.year} :
                        </strong>{" "}
                        Centre {(yearPred?.centre ?? 0) - (basePred?.centre ?? 0) >= 0 ? "+" : ""}
                        {+((yearPred?.centre ?? 0) - (basePred?.centre ?? 0)).toFixed(2)}pp — EXD{" "}
                        {(yearPred?.exd ?? 0) - (basePred?.exd ?? 0) >= 0 ? "+" : ""}
                        {+((yearPred?.exd ?? 0) - (basePred?.exd ?? 0)).toFixed(2)}pp — EXG{" "}
                        {(yearPred?.exg ?? 0) - (basePred?.exg ?? 0) >= 0 ? "+" : ""}
                        {+((yearPred?.exg ?? 0) - (basePred?.exg ?? 0)).toFixed(2)}pp
                        {yearPred?.confidence != null && (
                          <span className="ml-2 opacity-70">
                            · confiance modèle : {yearPred.confidence}%
                          </span>
                        )}
                      </div>
                    )}
                  </>
                );
              })()}
            </motion.section>
          )}

          {/* Donuts */}
          {data && selectedDept === "ALL" && (
            <section className="grid gap-5 md:grid-cols-2">
              <PartyDonut title="Réel · Départements" data={data.political_real} />
              <PartyDonut title="Prédit · Départements" data={data.political_predicted} />
            </section>
          )}

          {isLoading && (
            <div className="text-center text-sm text-muted-foreground">Chargement…</div>
          )}
        </div>
      </main>
    </div>
  );
}

/* ---------- Sidebar building blocks ---------- */

function SideSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
        {title}
      </p>
      <div className="space-y-1.5">{children}</div>
    </div>
  );
}

function SideLink({
  to,
  icon,
  label,
  sub,
  active,
}: {
  to: string;
  icon: React.ReactNode;
  label: string;
  sub: string;
  active?: boolean;
}) {
  return (
    <Link
      to={to}
      className={`flex items-center gap-3 rounded-xl px-3 py-2.5 transition-all ${
        active
          ? "bg-primary text-primary-foreground shadow-md shadow-primary/25"
          : "text-foreground hover:bg-secondary"
      }`}
    >
      <span className={active ? "text-primary-foreground" : "text-primary"}>{icon}</span>
      <span className="leading-tight">
        <span className="block text-sm font-semibold">{label}</span>
        <span
          className={`block text-[11px] ${active ? "text-primary-foreground/75" : "text-muted-foreground"}`}
        >
          {sub}
        </span>
      </span>
    </Link>
  );
}

function SideInfo({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-border bg-secondary/30 px-3 py-2.5">
      <span className="text-primary">{icon}</span>
      <span className="leading-tight">
        <span className="block text-[11px] text-muted-foreground">{label}</span>
        <span className="block text-sm font-semibold text-foreground">{value}</span>
      </span>
    </div>
  );
}

function ResultCard({
  label,
  value,
  hint,
  delay = 0,
}: {
  label: string;
  value: React.ReactNode;
  hint?: string;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="rounded-2xl border border-border bg-card p-5 shadow-[var(--shadow-card)]"
    >
      <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">
        {label}
      </p>
      <p className="mt-3 text-3xl font-bold tracking-tight text-primary">{value}</p>
      {hint && <p className="mt-2 text-xs text-muted-foreground">{hint}</p>}
    </motion.div>
  );
}

/* French flag — national symbol, kept in its real colours */
function FlagFR({ className = "" }: { className?: string }) {
  return (
    <span
      className={`inline-flex overflow-hidden rounded-[3px] border border-border shadow-sm ${className}`}
    >
      <span className="h-full w-1/3" style={{ backgroundColor: "#0055A4" }} />
      <span className="h-full w-1/3 bg-white" />
      <span className="h-full w-1/3" style={{ backgroundColor: "#EF4135" }} />
    </span>
  );
}
