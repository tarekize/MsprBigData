import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { useState, useMemo, useEffect } from "react";
import { type PredictionEntity } from "@/lib/predictions";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { PoliticalSpectrum } from "@/components/dashboard/PoliticalSpectrum";
import { PartyDonut } from "@/components/dashboard/PartyDonut";
import { PredictionTable } from "@/components/dashboard/PredictionTable";
import { Activity, Brain, MapPin, Sparkles, Database, BarChart3 } from "lucide-react";

export const Route = createFileRoute("/")({
  component: Index,
});

const SUPERVISED_MODELS = [
  { id: "xgboost", name: "XGBoost" },
  { id: "random_forest", name: "Random Forest" },
  { id: "gradient_boosting", name: "Gradient Boosting" },
  { id: "logistic_regression", name: "Logistic Regression" },
  { id: "svm_(linear)", name: "SVM (Linear)" }
];

const itemVariant = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

interface TendancePrediction {
  annee: string; year: number; is_base: boolean;
  exg: number; gauche: number; centre: number; droite: number; exd: number;
  confidence?: number;
}
interface TendancesJSON {
  metadata: { model: string; model_accuracy: number; base_year: number; forecast_years: number[] };
  deltas: Record<string, number>;
  predictions: TendancePrediction[];
}

const BLOCS_PREVIEW = [
  { key: "exg",    label: "Extrême G.", color: "#b91c1c" },
  { key: "gauche", label: "Gauche",     color: "#ef4444" },
  { key: "centre", label: "Centre",     color: "#eab308" },
  { key: "droite", label: "Droite",     color: "#3b82f6" },
  { key: "exd",    label: "Extrême D.", color: "#1d4ed8" },
] as const;

function Index() {
  const [selectedModel, setSelectedModel] = useState<string>("xgboost");
  const [tendances, setTendances] = useState<TendancesJSON | null>(null);
  const [selectedTendanceYear, setSelectedTendanceYear] = useState<number>(2020);

  useEffect(() => {
    fetch("/data/predictions_tendances.json")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d: TendancesJSON) => setTendances(d))
      .catch(() => {});
  }, []);

  const MODELS = SUPERVISED_MODELS;

  const { data, isLoading, error } = useQuery({
    queryKey: ['predictions', selectedModel],
    queryFn: async () => {
      const res = await fetch(`/data/predictions_${selectedModel}.json`, { cache: 'no-store' });
      if (!res.ok) throw new Error("Les prédictions de ce modèle ne sont pas disponibles.");
      return res.json();
    },
  });

  const [selectedDept, setSelectedDept] = useState<string>("ALL");
  const [selectedCanton, setSelectedCanton] = useState<string>("ALL");

  const { activeEntity, tableLevel, tableData } = useMemo(() => {
    if (!data) return { activeEntity: null, tableLevel: "Région", tableData: [] };

    let active = data.levels.region[0];
    let tLevel = "Départements";
    let tData = data.levels.departement || [];

    if (selectedDept !== "ALL") {
      active = data.levels.departement.find((d: PredictionEntity) => d.entity === selectedDept) || active;
      tLevel = "Cantons";
      tData = (data.levels.canton || []).filter((c: PredictionEntity) => c.parent === selectedDept);

      if (selectedCanton !== "ALL") {
        active = data.levels.canton.find((c: PredictionEntity) => c.entity === selectedCanton) || active;
        tLevel = "Canton Sélectionné";
        tData = [active];
      }
    }

    return { activeEntity: active, tableLevel: tLevel, tableData: tData };
  }, [data, selectedDept, selectedCanton]);

  return (
    <div className="min-h-screen text-foreground">
      {/* Top nav */}
      <nav className="sticky top-0 z-50 border-b border-border bg-card shadow-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground font-bold text-sm">
              G
            </div>
            <div className="leading-tight">
              <p className="text-sm font-semibold tracking-wide">GouvData</p>
              <p className="text-[11px] uppercase tracking-widest text-muted-foreground">ML Analytics · 2022</p>
            </div>
          </div>
          <div className="hidden items-center gap-2 md:flex">
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-secondary px-4 py-2 text-xs font-semibold text-foreground transition-all hover:border-primary/40 hover:bg-primary/5 no-underline"
            >
              <Activity className="h-3.5 w-3.5" />
              Dashboard
            </Link>
            <Link
              to="/visualisation"
              className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground transition-all hover:bg-primary/90 hover:shadow-md shadow-primary/20 no-underline"
            >
              <BarChart3 className="h-3.5 w-3.5" />
              Visualisation
            </Link>
            <span className="rounded-xl border border-border bg-secondary px-3 py-1.5 text-xs text-muted-foreground">
              {data?.summary.model_name ?? "—"} · {data?.summary.model_accuracy ?? "—"}% acc
            </span>
            <span className="flex items-center gap-1.5 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-600">
              <span className="relative flex h-1.5 w-1.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-500 opacity-75" />
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-500" />
              </span>
              Live
            </span>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <header className="relative overflow-hidden border-b border-border/50 bg-card">
        <div className="absolute inset-0 opacity-40" style={{ background: "var(--gradient-glow)" }} />
        <div className="relative mx-auto max-w-7xl px-6 py-14 md:py-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-3xl"
          >
            <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs text-primary font-semibold uppercase tracking-widest">
              <Sparkles className="h-3.5 w-3.5" />
              Présidentielle 2022 · Région Nouvelle-Aquitaine
            </span>
            <h1 className="mt-5 text-4xl font-bold tracking-tight text-foreground md:text-5xl">
              Prédire le vote{" "}
              <span className="text-primary">
                par la donnée
              </span>
            </h1>
            <p className="mt-5 max-w-2xl text-base text-muted-foreground md:text-lg">
              Pipeline complet — collecte,
              feature engineering Delta Lake, entraînement XGBoost, et lecture macro-politique des résultats
              à l'échelle <span className="font-semibold text-foreground">région · département · canton</span>.
            </p>

            <div className="mt-7 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
              <Badge icon={<Database className="h-3.5 w-3.5" />}>Données traitées</Badge>
              <Badge icon={<Brain className="h-3.5 w-3.5" />}>Machine Learning</Badge>
              <Badge icon={<Activity className="h-3.5 w-3.5" />}>Croissance · Stable · Déclin</Badge>
              <Badge icon={<MapPin className="h-3.5 w-3.5" />}>Filtrage dynamique</Badge>
            </div>

            <div className="mt-8">
              <Link
                to="/visualisation"
                className="group inline-flex items-center gap-3 rounded-2xl bg-gradient-to-r from-primary via-primary to-accent px-7 py-3.5 text-sm font-semibold text-background shadow-lg shadow-primary/25 transition-all duration-300 hover:shadow-xl hover:shadow-primary/40 hover:scale-[1.03]"
              >
                <BarChart3 className="h-5 w-5 transition-transform duration-300 group-hover:rotate-12" />
                Voir les Visualisations
                <span className="ml-1 text-background/70 transition-transform duration-300 group-hover:translate-x-1">→</span>
              </Link>
            </div>
          </motion.div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-10 px-6 py-12">
        {data && (
          <motion.section
            variants={itemVariant}
            initial="hidden"
            animate="show"
            className="grid gap-6 rounded-3xl border border-primary/20 bg-primary p-6 md:p-8 lg:grid-cols-[1.35fr_0.95fr]"
            style={{ boxShadow: "var(--shadow-elegant)" }}
          >
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-widest text-primary-foreground/70">
                Accès rapide à la visualisation
              </p>
              <h2 className="mt-3 max-w-2xl text-2xl font-bold tracking-tight text-primary-foreground md:text-3xl">
                Explorez les courbes, corrélations et comparaisons de modèles ML.
              </h2>
              <p className="mt-4 max-w-2xl text-sm text-primary-foreground/70 md:text-base">
                La visualisation reprend les résultats ML réels : matrice de corrélation,
                courbes d'apprentissage et bar charts de performance.
              </p>

              <div className="mt-6 flex flex-wrap items-center gap-3">
                <Link
                  to="/visualisation"
                  className="group inline-flex items-center gap-2 rounded-xl bg-white/15 border border-white/25 px-5 py-2.5 text-sm font-semibold text-white backdrop-blur transition-all hover:bg-white/25 no-underline"
                >
                  <BarChart3 className="h-4 w-4" />
                  Voir la visualisation
                  <span className="transition-transform duration-300 group-hover:translate-x-1">→</span>
                </Link>
                <span className="rounded-full border border-white/20 bg-white/10 px-4 py-2 text-xs text-primary-foreground/80">
                  {data.summary.model_name} · {data.summary.model_accuracy}% accuracy
                </span>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl border border-white/15 bg-white/10 p-4">
                <p className="text-[10px] font-semibold uppercase tracking-widest text-primary-foreground/60">Meilleur modèle</p>
                <p className="mt-3 text-2xl font-bold text-primary-foreground">{data.summary.model_name}</p>
                <p className="mt-1 text-xs text-primary-foreground/60">Score global affiché dans le dashboard</p>
              </div>
              <div className="rounded-2xl border border-white/15 bg-white/10 p-4">
                <p className="text-[10px] font-semibold uppercase tracking-widest text-primary-foreground/60">Accuracy</p>
                <p className="mt-3 text-2xl font-bold text-primary-foreground">{data.summary.model_accuracy}%</p>
                <p className="mt-1 text-xs text-primary-foreground/60">Résultat du modèle chargé</p>
              </div>
              <div className="rounded-2xl border border-white/15 bg-white/10 p-4">
                <p className="text-[10px] font-semibold uppercase tracking-widest text-primary-foreground/60">Vue active</p>
                <p className="mt-3 text-2xl font-bold text-primary-foreground">{activeEntity?.entity || "Région"}</p>
                <p className="mt-1 text-xs text-primary-foreground/60">Lecture détaillée selon le filtre courant</p>
              </div>
              <div className="rounded-2xl border border-white/15 bg-white/10 p-4">
                <p className="text-[10px] font-semibold uppercase tracking-widest text-primary-foreground/60">Graphiques</p>
                <p className="mt-3 text-2xl font-bold text-primary-foreground">5+</p>
                <p className="mt-1 text-xs text-primary-foreground/60">Corrélations, courbes et comparaisons</p>
              </div>
            </div>
          </motion.section>
        )}

        {error && (
          <div className="rounded-2xl border border-destructive/40 bg-destructive/10 p-5 text-sm text-destructive-foreground">
            Impossible de charger <code>predictions.json</code>. Lance le notebook ML pour le générer dans <code>/public/data/</code>.
          </div>
        )}

        {/* Filters */}
        <section className="flex flex-wrap gap-4 rounded-3xl border border-border bg-card/50 p-6 backdrop-blur-xl shadow-[var(--shadow-card)] mb-6">

          <div className="flex flex-col gap-2 flex-1 min-w-[200px]">
            <label className="text-[11px] font-medium text-primary uppercase tracking-[0.18em]">Modèle d'Intelligence Artificielle</label>
            <select
              value={selectedModel}
              onChange={e => setSelectedModel(e.target.value)}
              className="bg-background border border-primary/40 rounded-xl px-4 py-3 text-sm text-foreground focus:border-primary outline-none transition-colors"
              style={{ appearance: 'auto' }}
            >
              {MODELS.map(m => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
          </div>
        </section>

        {data && (
          <section className="flex flex-wrap gap-4 rounded-3xl border border-border bg-card/50 p-6 backdrop-blur-xl shadow-[var(--shadow-card)]">
            <div className="flex flex-col gap-2 flex-1 min-w-[200px]">
              <label className="text-[11px] font-medium text-accent uppercase tracking-[0.18em]">Région</label>
              <select disabled className="bg-secondary/50 border border-border rounded-xl px-4 py-3 text-sm text-foreground opacity-70">
                <option>Nouvelle-Aquitaine</option>
              </select>
            </div>

            <div className="flex flex-col gap-2 flex-1 min-w-[200px]">
              <label className="text-[11px] font-medium text-accent uppercase tracking-[0.18em]">Département</label>
              <select
                value={selectedDept}
                onChange={e => {
                  setSelectedDept(e.target.value);
                  setSelectedCanton("ALL");
                }}
                className="bg-background border border-border rounded-xl px-4 py-3 text-sm text-foreground focus:border-primary outline-none transition-colors"
              >
                <option value="ALL">Tous les départements</option>
                {data.levels.departement?.map((d: PredictionEntity) => (
                  <option key={d.entity} value={d.entity}>{d.entity}</option>
                ))}
              </select>
            </div>

            <div className="flex flex-col gap-2 flex-1 min-w-[200px]">
              <label className="text-[11px] font-medium text-accent uppercase tracking-[0.18em]">Canton</label>
              <select
                value={selectedCanton}
                onChange={e => setSelectedCanton(e.target.value)}
                disabled={selectedDept === "ALL"}
                className="bg-background border border-border rounded-xl px-4 py-3 text-sm text-foreground focus:border-primary outline-none transition-colors disabled:opacity-50"
              >
                <option value="ALL">Tous les cantons</option>
                {selectedDept !== "ALL" && data.levels.canton
                  ?.filter((c: PredictionEntity) => c.parent === selectedDept)
                  .map((c: PredictionEntity) => (
                    <option key={c.entity} value={c.entity}>{c.entity}</option>
                  ))
                }
              </select>
            </div>
          </section>
        )}

        {/* Political spectrum for active entity */}
        {activeEntity && (
          <PoliticalSpectrum entityName={activeEntity.entity} ecoState={activeEntity.economic_state} />
        )}

        {/* Tables */}
        {data && <PredictionTable data={tableData} levelLabel={tableLevel} />}

        {/* Prévision tendances 5 blocs — aperçu rapide (données depuis predictions_tendances.json) */}
        {tendances && (
          <motion.section
            variants={itemVariant}
            initial="hidden"
            animate="show"
            className="rounded-3xl border border-border bg-card/50 p-6 backdrop-blur-xl shadow-[var(--shadow-card)]"
          >
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-accent">
                  Prévision électorale à moyen terme · {tendances.metadata.model}
                </p>
                <h2 className="mt-1 text-lg font-semibold tracking-tight">
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
              {tendances.metadata.model} ({tendances.metadata.model_accuracy}% acc.) sur indicateurs delta socio-économiques.
              Base {tendances.metadata.base_year}.
            </p>

            {/* Sélecteur d'année */}
            <div className="mb-4 flex flex-wrap gap-2">
              {tendances.predictions.map((p) => (
                <button
                  key={p.year}
                  onClick={() => setSelectedTendanceYear(p.year)}
                  className={`rounded-full px-3 py-1 text-xs font-semibold transition-all border ${
                    selectedTendanceYear === p.year
                      ? "border-primary bg-primary/20 text-primary"
                      : "border-border bg-secondary/40 text-muted-foreground hover:border-primary/50 hover:text-foreground"
                  }`}
                >
                  {p.year}{p.is_base ? " (base)" : ""}
                  {p.confidence != null && !p.is_base && (
                    <span className="ml-1 opacity-60">· {p.confidence}%</span>
                  )}
                </button>
              ))}
            </div>

            {/* Cartes 5 blocs pour l'année sélectionnée */}
            {(() => {
              const basePred   = tendances.predictions.find((p) => p.is_base) ?? tendances.predictions[0];
              const yearPred   = tendances.predictions.find((p) => p.year === selectedTendanceYear) ?? basePred;
              return (
                <>
                  <div className="grid gap-3 sm:grid-cols-5">
                    {BLOCS_PREVIEW.map((bloc) => {
                      const val   = yearPred?.[bloc.key] ?? 0;
                      const base  = basePred?.[bloc.key] ?? 0;
                      const delta = +(val - base).toFixed(2);
                      const isUp  = delta > 0;
                      const deltaColor =
                        bloc.key === "centre"
                          ? isUp ? "text-emerald-400" : "text-rose-400"
                          : isUp ? "text-amber-400" : "text-emerald-400";
                      return (
                        <div key={bloc.key} className="rounded-2xl border border-border bg-background/30 p-3 text-center">
                          <p className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground leading-tight">{bloc.label}</p>
                          <p className="mt-2 text-xl font-bold" style={{ color: bloc.color }}>{val.toFixed(1)}%</p>
                          {yearPred?.is_base ? (
                            <p className="mt-1 text-xs text-muted-foreground">base</p>
                          ) : (
                            <p className={`mt-1 text-xs font-semibold ${deltaColor}`}>
                              {isUp ? "+" : ""}{delta}pp vs {basePred?.year}
                            </p>
                          )}
                          <div className="mt-2 h-1 rounded-full bg-border/40">
                            <div
                              className="h-1 rounded-full"
                              style={{ width: `${Math.min(val, 100)}%`, backgroundColor: bloc.color, opacity: 0.7 }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  {!yearPred?.is_base && (
                    <div className="mt-4 rounded-xl border border-rose-500/20 bg-rose-500/5 px-4 py-2.5 text-xs text-rose-300">
                      <strong>{yearPred?.year} vs {basePred?.year} :</strong>{" "}
                      Centre {((yearPred?.centre ?? 0) - (basePred?.centre ?? 0)) >= 0 ? "+" : ""}
                      {+((yearPred?.centre ?? 0) - (basePred?.centre ?? 0)).toFixed(2)}pp —{" "}
                      EXD {((yearPred?.exd ?? 0) - (basePred?.exd ?? 0)) >= 0 ? "+" : ""}
                      {+((yearPred?.exd ?? 0) - (basePred?.exd ?? 0)).toFixed(2)}pp —{" "}
                      EXG {((yearPred?.exg ?? 0) - (basePred?.exg ?? 0)) >= 0 ? "+" : ""}
                      {+((yearPred?.exg ?? 0) - (basePred?.exg ?? 0)).toFixed(2)}pp
                      {yearPred?.confidence != null && (
                        <span className="ml-2 opacity-70">· confiance modèle : {yearPred.confidence}%</span>
                      )}
                    </div>
                  )}
                </>
              );
            })()}
          </motion.section>
        )}

        {/* KPI grid */}
        <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <KpiCard
            label={`Vainqueur prédit (${activeEntity?.entity || '—'})`}
            value={activeEntity?.predicted ?? "—"}
            hint={`Réel : ${activeEntity?.real ?? "—"}`}
            accent="primary"
            delay={0}
          />
          <KpiCard
            label="État économique calculé"
            value={activeEntity?.economic_state?.toUpperCase() ?? "—"}
            hint={`Score : ${activeEntity?.economic_score?.toFixed(1) ?? "—"}`}
            accent="accent"
            delay={0.05}
          />
          <KpiCard
            label={`Accuracy modèle (${data?.summary.model_name ?? '—'})`}
            value={data ? `${data.summary.model_accuracy}%` : "—"}
            hint="Entraînement sur variables socio-éco"
            accent="success"
            delay={0.1}
          />
        </section>

        {/* Donuts */}
        {data && selectedDept === "ALL" && (
          <section className="grid gap-5 md:grid-cols-2">
            <PartyDonut title="Réel · Départements" data={data.political_real} />
            <PartyDonut title="Prédit · Départements" data={data.political_predicted} />
          </section>
        )}

        {isLoading && <div className="text-center text-sm text-muted-foreground">Chargement…</div>}
      </main>
    </div>
  );
}

function Badge({ icon, children }: { icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-card/40 px-3 py-1.5 backdrop-blur">
      {icon}
      {children}
    </span>
  );
}
