import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { useState, useMemo } from "react";
import { fetchPredictions, type Level, type PredictionEntity } from "@/lib/predictions";
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

function Index() {
  const [selectedModel, setSelectedModel] = useState<string>("xgboost");

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
      <nav className="sticky top-0 z-50 border-b border-border/60 bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent text-background font-bold">
              G
            </div>
            <div className="leading-tight">
              <p className="text-sm font-semibold tracking-wide">GouvData</p>
              <p className="text-[11px] uppercase tracking-widest text-muted-foreground">ML Analytics · 2022</p>
            </div>
          </div>
          <div className="hidden items-center gap-2 md:flex">
            <Link
              to="/visualisation"
              className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-primary to-accent px-4 py-2 text-xs font-semibold text-background transition-all hover:shadow-lg hover:shadow-primary/30 hover:scale-105"
            >
              <BarChart3 className="h-3.5 w-3.5" />
              Visualisation
            </Link>
            <span className="rounded-full border border-border bg-secondary/60 px-3 py-1 text-xs text-muted-foreground">
              {data?.summary.model_name ?? "—"} · {data?.summary.model_accuracy ?? "—"}% acc
            </span>
            <span className="flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400">
              <span className="relative flex h-1.5 w-1.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-400" />
              </span>
              Live
            </span>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <header className="relative overflow-hidden border-b border-border/40">
        <div className="absolute inset-0" style={{ background: "var(--gradient-glow)" }} />
        <div className="relative mx-auto max-w-7xl px-6 py-16 md:py-24">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-3xl"
          >
            <span className="inline-flex items-center gap-2 rounded-full border border-border bg-card/60 px-3 py-1 text-xs text-muted-foreground backdrop-blur">
              <Sparkles className="h-3.5 w-3.5 text-accent" />
              Présidentielle 2022 · Région Nouvelle-Aquitaine
            </span>
            <h1 className="mt-5 text-4xl font-semibold tracking-tight md:text-6xl">
              Prédire le vote{" "}
              <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
                par la donnée
              </span>
            </h1>
            <p className="mt-5 max-w-2xl text-base text-muted-foreground md:text-lg">
              Pipeline complet — collecte,
              feature engineering Delta Lake, entraînement XGBoost, et lecture macro-politique des résultats
              à l'échelle <span className="text-foreground">région · département · canton</span>.
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
            className="grid gap-6 rounded-3xl border border-border p-6 md:p-8 lg:grid-cols-[1.35fr_0.95fr]"
            style={{
              background:
                "linear-gradient(135deg, oklch(0.24 0.045 260 / 0.96), oklch(0.19 0.04 260 / 0.88))",
              boxShadow: "var(--shadow-elegant)",
            }}
          >
            <div>
              <p className="text-[11px] font-medium uppercase tracking-[0.22em] text-accent">
                Accès rapide à la visualisation
              </p>
              <h2 className="mt-3 max-w-2xl text-2xl font-semibold tracking-tight md:text-4xl">
                Ouvre une page dédiée pour lire les courbes, les corrélations et les comparaisons de modèles.
              </h2>
              <p className="mt-4 max-w-2xl text-sm text-muted-foreground md:text-base">
                La visualisation reprend tes résultats ML réels et les présente dans un format plus net : matrice de corrélation,
                courbes d'apprentissage et bar charts de performance.
              </p>

              <div className="mt-6 flex flex-wrap items-center gap-3">
                <Link
                  to="/visualisation"
                  className="group inline-flex items-center gap-3 rounded-2xl bg-gradient-to-r from-primary via-primary to-accent px-6 py-3 text-sm font-semibold text-background shadow-lg shadow-primary/25 transition-all duration-300 hover:scale-[1.02] hover:shadow-xl hover:shadow-primary/35"
                >
                  <BarChart3 className="h-5 w-5 transition-transform duration-300 group-hover:rotate-12" />
                  Voir la visualisation
                  <span className="transition-transform duration-300 group-hover:translate-x-1">→</span>
                </Link>
                <span className="rounded-full border border-border bg-secondary/60 px-4 py-2 text-xs text-muted-foreground">
                  {data.summary.model_name} · {data.summary.model_accuracy}% accuracy
                </span>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl border border-border/70 bg-background/20 p-4 backdrop-blur-sm">
                <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-muted-foreground">Meilleur modèle</p>
                <p className="mt-3 text-2xl font-semibold text-foreground">{data.summary.model_name}</p>
                <p className="mt-1 text-xs text-muted-foreground">Score global affiché dans le dashboard</p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-background/20 p-4 backdrop-blur-sm">
                <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-muted-foreground">Accuracy</p>
                <p className="mt-3 text-2xl font-semibold text-foreground">{data.summary.model_accuracy}%</p>
                <p className="mt-1 text-xs text-muted-foreground">Résultat du modèle chargé</p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-background/20 p-4 backdrop-blur-sm">
                <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-muted-foreground">Vue active</p>
                <p className="mt-3 text-2xl font-semibold text-foreground">{activeEntity?.entity || "Région"}</p>
                <p className="mt-1 text-xs text-muted-foreground">Lecture détaillée selon le filtre courant</p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-background/20 p-4 backdrop-blur-sm">
                <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-muted-foreground">Graphiques</p>
                <p className="mt-3 text-2xl font-semibold text-foreground">5+</p>
                <p className="mt-1 text-xs text-muted-foreground">Corrélations, courbes et comparaisons</p>
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
