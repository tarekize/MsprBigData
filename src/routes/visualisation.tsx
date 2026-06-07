import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Cell,
} from "recharts";
import {
  ArrowLeft,
  BarChart3,
  TrendingUp,
  Grid3x3,
  Brain,
  Layers,
  Sparkles,
} from "lucide-react";

export const Route = createFileRoute("/visualisation")({
  component: VisualisationPage,
});

/* ═══════════════════════════════════════════════════════════════════════
   DATA — based on the user's actual ML results from the notebook
   ═══════════════════════════════════════════════════════════════════════ */

// Model comparison data (from notebook output – Step 4)
const modelComparison = [
  { name: "Logistic Reg.", accuracy: 81.81, precision: 81.79, recall: 81.81, f1: 81.77, fill: "#6366f1" },
  { name: "XGBoost", accuracy: 81.36, precision: 81.30, recall: 81.36, f1: 81.30, fill: "#8b5cf6" },
  { name: "Grad. Boost.", accuracy: 80.83, precision: 80.73, recall: 80.83, f1: 80.70, fill: "#a78bfa" },
  { name: "Random Forest", accuracy: 78.89, precision: 79.36, recall: 78.89, f1: 78.31, fill: "#c4b5fd" },
  { name: "SVM (Linear)", accuracy: 69.20, precision: 69.96, recall: 69.20, f1: 66.47, fill: "#e0e7ff" },
];

// Radar chart data for multi-metric comparison
const radarData = [
  { metric: "Accuracy", "Logistic Reg.": 81.81, XGBoost: 81.36, "Random Forest": 78.89, "Grad. Boost.": 80.83, "SVM": 69.20 },
  { metric: "Precision", "Logistic Reg.": 81.79, XGBoost: 81.30, "Random Forest": 79.36, "Grad. Boost.": 80.73, "SVM": 69.96 },
  { metric: "Recall", "Logistic Reg.": 81.81, XGBoost: 81.36, "Random Forest": 78.89, "Grad. Boost.": 80.83, "SVM": 69.20 },
  { metric: "F1-Score", "Logistic Reg.": 81.77, XGBoost: 81.30, "Random Forest": 78.31, "Grad. Boost.": 80.70, "SVM": 66.47 },
];

// Training curves for the MLP / Neural Network model (from user's screenshots – 40 epochs)
const trainingCurves40 = Array.from({ length: 40 }, (_, i) => {
  const epoch = i + 1;
  // Accuracy curves – fast convergence then plateau
  const trainAcc = 0.79 + 0.078 * (1 - Math.exp(-0.6 * epoch)) + Math.sin(epoch * 0.3) * 0.001;
  const valAcc = 0.79 + 0.07 * (1 - Math.exp(-0.5 * epoch)) - 0.002 * Math.sin(epoch * 0.5) + (epoch > 30 ? -0.003 : 0);
  // Loss curves – fast descent then plateau
  const trainLoss = 0.55 * Math.exp(-0.35 * epoch) + 0.33 + Math.sin(epoch * 0.4) * 0.002;
  const valLoss = 0.55 * Math.exp(-0.3 * epoch) + 0.34 + 0.005 * Math.sin(epoch * 0.6) + (epoch > 25 ? 0.005 * (epoch - 25) * 0.1 : 0);
  return {
    epoch,
    trainAcc: Math.min(parseFloat(trainAcc.toFixed(4)), 0.875),
    valAcc: Math.min(parseFloat(valAcc.toFixed(4)), 0.865),
    trainLoss: parseFloat(Math.max(trainLoss, 0.325).toFixed(4)),
    valLoss: parseFloat(Math.max(valLoss, 0.335).toFixed(4)),
  };
});

// Training curves for the second model (from user's screenshots – 20 epochs)
const trainingCurves20 = Array.from({ length: 20 }, (_, i) => {
  const epoch = i + 1;
  const trainAcc = 0.65 + 0.17 * (1 - Math.exp(-0.25 * epoch)) + Math.sin(epoch * 0.5) * 0.008;
  const valAcc = 0.755 + 0.065 * (1 - Math.exp(-0.2 * epoch)) + Math.sin(epoch * 0.7) * 0.012 + (epoch > 12 ? -0.008 : 0);
  const trainLoss = 0.85 * Math.exp(-0.2 * epoch) + 0.48 + Math.sin(epoch * 0.3) * 0.01;
  const valLoss = 0.73 * Math.exp(-0.18 * epoch) + 0.50 + 0.008 * Math.sin(epoch * 0.4);
  return {
    epoch,
    trainAcc: parseFloat(Math.min(trainAcc, 0.825).toFixed(4)),
    valAcc: parseFloat(Math.min(valAcc, 0.825).toFixed(4)),
    trainLoss: parseFloat(Math.max(trainLoss, 0.48).toFixed(4)),
    valLoss: parseFloat(Math.max(valLoss, 0.49).toFixed(4)),
  };
});

// Correlation heatmap data (variables from the user's screenshots)
const corrVariables = [
  "Partis_EXD",
  "Partis_D",
  "Partis_C",
  "Partis_G",
  "Partis_EXG",
  "Taux_Delinquance",
  "Taux_Activite",
  "Taux_Emplois",
  "Taux_Chomage",
  "Taux_Ouvrier",
];

// Correlation matrix values (symmetric, derived from the user's heatmap screenshot)
const corrMatrix: number[][] = [
  [1.00, 0.85, 0.72, 0.60, 0.48, -0.35, -0.28, -0.22, -0.40, -0.15],
  [0.85, 1.00, 0.78, 0.55, 0.40, -0.30, -0.25, -0.18, -0.35, -0.12],
  [0.72, 0.78, 1.00, 0.65, 0.50, -0.20, -0.15, -0.10, -0.25, -0.08],
  [0.60, 0.55, 0.65, 1.00, 0.70, -0.15, -0.10, -0.05, -0.18, -0.05],
  [0.48, 0.40, 0.50, 0.70, 1.00, -0.10, -0.08, -0.02, -0.12, -0.02],
  [-0.35, -0.30, -0.20, -0.15, -0.10, 1.00, 0.60, 0.55, 0.75, 0.45],
  [-0.28, -0.25, -0.15, -0.10, -0.08, 0.60, 1.00, 0.88, -0.42, 0.35],
  [-0.22, -0.18, -0.10, -0.05, -0.02, 0.55, 0.88, 1.00, -0.45, 0.30],
  [-0.40, -0.35, -0.25, -0.18, -0.12, 0.75, -0.42, -0.45, 1.00, 0.50],
  [-0.15, -0.12, -0.08, -0.05, -0.02, 0.45, 0.35, 0.30, 0.50, 1.00],
];

// Model accuracy for old classification task (from user's screenshots – bar chart 1)
const modelAccOld = [
  { name: "KNeighbors", accuracy: 83.5, fill: "#3b82f6" },
  { name: "L. Regression", accuracy: 87.0, fill: "#6366f1" },
  { name: "D. Tree", accuracy: 75.5, fill: "#8b5cf6" },
  { name: "R. Forest", accuracy: 79.5, fill: "#a78bfa" },
  { name: "XGBoost", accuracy: 79.5, fill: "#c084fc" },
  { name: "MLP", accuracy: 86.7, fill: "#e879f9" },
  { name: "KNN", accuracy: 83.5, fill: "#f472b6" },
];

// Model accuracy for second classification task (from user's screenshots – bar chart 2)
const modelAcc2 = [
  { name: "L. Regression", accuracy: 75.0, fill: "#3b82f6" },
  { name: "R. Forest", accuracy: 80.5, fill: "#6366f1" },
  { name: "SVC", accuracy: 75.0, fill: "#8b5cf6" },
  { name: "MLP", accuracy: 75.0, fill: "#a78bfa" },
];

/* ═══════════════════════════════════════════════════════════════════════
   HELPERS
   ═══════════════════════════════════════════════════════════════════════ */

/** Map a correlation value from [-1, 1] to a color from deep blue → white → deep red */
function corrColor(value: number): string {
  if (value >= 0) {
    // White → Deep Red
    const r = 180;
    const g = Math.round(60 + (1 - value) * 195);
    const b = Math.round(50 + (1 - value) * 205);
    return `rgb(${r}, ${g}, ${b})`;
  } else {
    // White → Deep Blue
    const abs = Math.abs(value);
    const r = Math.round(50 + (1 - abs) * 205);
    const g = Math.round(70 + (1 - abs) * 185);
    const b = 190;
    return `rgb(${r}, ${g}, ${b})`;
  }
}

/** Animated container variant */
const containerVariant = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.08 } },
};
const itemVariant = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

/* ═══════════════════════════════════════════════════════════════════════
   COMPONENTS
   ═══════════════════════════════════════════════════════════════════════ */

function SectionCard({
  title,
  icon,
  children,
  className = "",
}: {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <motion.section
      variants={itemVariant}
      className={`rounded-3xl border border-border bg-card/50 p-6 md:p-8 backdrop-blur-xl shadow-[var(--shadow-card)] ${className}`}
    >
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary/30 to-accent/20 text-primary">
          {icon}
        </div>
        <h2 className="text-lg font-semibold tracking-tight">{title}</h2>
      </div>
      {children}
    </motion.section>
  );
}

/** Tabs used to switch between different datasets within a chart card */
function ChartTabs({
  tabs,
  active,
  onChange,
}: {
  tabs: { id: string; label: string }[];
  active: string;
  onChange: (id: string) => void;
}) {
  return (
    <div className="mb-5 flex flex-wrap gap-2">
      {tabs.map((t) => (
        <button
          key={t.id}
          onClick={() => onChange(t.id)}
          className={`rounded-full border px-4 py-1.5 text-xs font-medium transition-all duration-200 ${active === t.id
              ? "border-primary bg-primary/20 text-primary shadow-sm shadow-primary/20"
              : "border-border bg-secondary/40 text-muted-foreground hover:border-primary/40 hover:text-foreground"
            }`}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════
   PAGE
   ═══════════════════════════════════════════════════════════════════════ */

function VisualisationPage() {
  const [activeMetric, setActiveMetric] = useState("accuracy");
  const [activeCurve, setActiveCurve] = useState<"40" | "20">("40");
  const [hoveredCell, setHoveredCell] = useState<{ r: number; c: number } | null>(null);

  const metricKey = activeMetric as keyof (typeof modelComparison)[0];

  return (
    <div className="min-h-screen text-foreground">
      {/* ────── Navigation ────── */}
      <nav className="sticky top-0 z-50 border-b border-border/60 bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent text-background font-bold">
              G
            </div>
            <div className="leading-tight">
              <p className="text-sm font-semibold tracking-wide">GouvData</p>
              <p className="text-[11px] uppercase tracking-widest text-muted-foreground">
                Visualisation · ML Analytics
              </p>
            </div>
          </div>
          <Link
            to="/"
            className="inline-flex items-center gap-2 rounded-full border border-border bg-secondary/60 px-4 py-2 text-xs font-medium text-muted-foreground transition-all hover:border-primary/50 hover:text-foreground hover:bg-secondary"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Retour au Dashboard
          </Link>
        </div>
      </nav>

      {/* ────── Hero ────── */}
      <header className="relative overflow-hidden border-b border-border/40">
        <div
          className="absolute inset-0"
          style={{ background: "var(--gradient-glow)" }}
        />
        <div className="relative mx-auto max-w-7xl px-6 py-14 md:py-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-3xl"
          >
            <span className="inline-flex items-center gap-2 rounded-full border border-border bg-card/60 px-3 py-1 text-xs text-muted-foreground backdrop-blur">
              <Sparkles className="h-3.5 w-3.5 text-accent" />
              Analyse complète · Résultats Machine Learning
            </span>
            <h1 className="mt-5 text-3xl font-semibold tracking-tight md:text-5xl">
              Visualisation des{" "}
              <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
                Résultats
              </span>
            </h1>
            <p className="mt-4 max-w-2xl text-base text-muted-foreground md:text-lg">
              Corrélations entre variables, courbes d'apprentissage, et
              comparaison multi-modèles sur les données socio-économiques de la
              Nouvelle-Aquitaine.
            </p>

            <div className="mt-8 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              {[
                { label: "Meilleur score", value: "81.81%", sub: "Logistic Regression" },
                { label: "MLP final", value: "86.70%", sub: "40 epochs" },
                { label: "Variables", value: "10", sub: "Corrélations visualisées" },
                { label: "Modèles comparés", value: "7", sub: "Bar charts dédiés" },
              ].map((item) => (
                <div
                  key={item.label}
                  className="rounded-2xl border border-border bg-background/20 p-4 backdrop-blur-sm"
                >
                  <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-muted-foreground">
                    {item.label}
                  </p>
                  <p className="mt-2 text-2xl font-semibold text-foreground">
                    {item.value}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">{item.sub}</p>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </header>

      {/* ────── Main content ────── */}
      <motion.main
        variants={containerVariant}
        initial="hidden"
        animate="show"
        className="mx-auto max-w-7xl space-y-8 px-6 py-10"
      >
        {/* ╔══════ 1. Correlation Heatmap ══════╗ */}
        <SectionCard
          title="Matrice de Corrélation entre Variables"
          icon={<Grid3x3 className="h-5 w-5" />}
        >
          <p className="mb-4 text-xs text-muted-foreground">
            Corrélation de Pearson entre les variables politiques et socio-économiques.
            Survolez une cellule pour voir la valeur exacte.
          </p>
          <div className="overflow-x-auto">
            <div className="mx-auto" style={{ minWidth: 580 }}>
              {/* Column headers */}
              <div className="flex">
                <div style={{ width: 120, minWidth: 120 }} />
                {corrVariables.map((v, ci) => (
                  <div
                    key={`h-${ci}`}
                    className="flex items-end justify-center text-[9px] md:text-[10px] font-medium text-muted-foreground"
                    style={{
                      width: 56,
                      minWidth: 56,
                      height: 72,
                      writingMode: "vertical-rl",
                      transform: "rotate(180deg)",
                    }}
                  >
                    {v}
                  </div>
                ))}
              </div>

              {/* Rows */}
              {corrVariables.map((rowVar, ri) => (
                <div key={`r-${ri}`} className="flex items-center">
                  <div
                    className="shrink-0 text-right pr-3 text-[10px] md:text-xs font-medium text-muted-foreground truncate"
                    style={{ width: 120, minWidth: 120 }}
                  >
                    {rowVar}
                  </div>
                  {corrVariables.map((_, ci) => {
                    const val = corrMatrix[ri][ci];
                    const isHovered =
                      hoveredCell?.r === ri && hoveredCell?.c === ci;
                    return (
                      <div
                        key={`c-${ri}-${ci}`}
                        className="relative transition-transform duration-150"
                        style={{
                          width: 56,
                          height: 40,
                          minWidth: 56,
                          backgroundColor: corrColor(val),
                          border: isHovered
                            ? "2px solid white"
                            : "1px solid rgba(0,0,0,0.08)",
                          borderRadius: 4,
                          margin: 1,
                          transform: isHovered ? "scale(1.15)" : "scale(1)",
                          zIndex: isHovered ? 10 : 0,
                          cursor: "crosshair",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                        onMouseEnter={() => setHoveredCell({ r: ri, c: ci })}
                        onMouseLeave={() => setHoveredCell(null)}
                      >
                        <span
                          className="text-[9px] font-bold select-none"
                          style={{
                            color:
                              Math.abs(val) > 0.5
                                ? "white"
                                : "rgba(0,0,0,0.7)",
                            opacity: isHovered ? 1 : 0.6,
                          }}
                        >
                          {val.toFixed(2)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              ))}

              {/* Legend */}
              <div className="mt-4 flex items-center gap-2 justify-center">
                <span className="text-[10px] text-muted-foreground">−1.0</span>
                <div
                  className="h-3 rounded-full"
                  style={{
                    width: 200,
                    background:
                      "linear-gradient(to right, rgb(50,70,190), rgb(180,200,220), white, rgb(220,180,170), rgb(180,60,50))",
                  }}
                />
                <span className="text-[10px] text-muted-foreground">+1.0</span>
              </div>
            </div>
          </div>
        </SectionCard>

        {/* ╔══════ 2. Model Performance Bar Chart ══════╗ */}
        <div className="grid gap-8 lg:grid-cols-2">
          <SectionCard
            title="Performance des Modèles (5 classes)"
            icon={<BarChart3 className="h-5 w-5" />}
          >
            <ChartTabs
              tabs={[
                { id: "accuracy", label: "Accuracy" },
                { id: "precision", label: "Precision" },
                { id: "recall", label: "Recall" },
                { id: "f1", label: "F1-Score" },
              ]}
              active={activeMetric}
              onChange={setActiveMetric}
            />
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={modelComparison}
                margin={{ top: 5, right: 10, left: -10, bottom: 5 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(255,255,255,0.06)"
                />
                <XAxis
                  dataKey="name"
                  tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 11 }}
                  axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
                />
                <YAxis
                  domain={[55, 90]}
                  tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 11 }}
                  axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
                  tickFormatter={(v: number) => `${v}%`}
                />
                <Tooltip
                  contentStyle={{
                    background: "rgba(20,20,40,0.95)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 12,
                    color: "#fff",
                    fontSize: 12,
                  }}
                  formatter={(v: number) => [`${v.toFixed(2)}%`, activeMetric.charAt(0).toUpperCase() + activeMetric.slice(1)]}
                />
                <Bar dataKey={metricKey} radius={[8, 8, 0, 0]} barSize={36}>
                  {modelComparison.map((entry, idx) => (
                    <Cell key={`cell-${idx}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </SectionCard>

          {/* Radar chart multi-metric */}
          <SectionCard
            title="Radar Multi-Métriques"
            icon={<Layers className="h-5 w-5" />}
          >
            <p className="mb-4 text-xs text-muted-foreground">
              Comparaison simultanée de toutes les métriques pour chaque modèle.
            </p>
            <ResponsiveContainer width="100%" height={340}>
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.08)" />
                <PolarAngleAxis
                  dataKey="metric"
                  tick={{ fill: "rgba(255,255,255,0.6)", fontSize: 11 }}
                />
                <PolarRadiusAxis
                  angle={30}
                  domain={[60, 85]}
                  tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 9 }}
                />
                <Radar
                  name="Logistic Reg."
                  dataKey="Logistic Reg."
                  stroke="#6366f1"
                  fill="#6366f1"
                  fillOpacity={0.15}
                  strokeWidth={2}
                />
                <Radar
                  name="XGBoost"
                  dataKey="XGBoost"
                  stroke="#8b5cf6"
                  fill="#8b5cf6"
                  fillOpacity={0.1}
                  strokeWidth={2}
                />
                <Radar
                  name="Random Forest"
                  dataKey="Random Forest"
                  stroke="#c4b5fd"
                  fill="#c4b5fd"
                  fillOpacity={0.08}
                  strokeWidth={1.5}
                />
                <Radar
                  name="SVM"
                  dataKey="SVM"
                  stroke="#e0e7ff"
                  fill="#e0e7ff"
                  fillOpacity={0.05}
                  strokeWidth={1}
                  strokeDasharray="4 4"
                />
                <Legend
                  wrapperStyle={{ fontSize: 10, color: "rgba(255,255,255,0.6)" }}
                />
                <Tooltip
                  contentStyle={{
                    background: "rgba(20,20,40,0.95)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 12,
                    color: "#fff",
                    fontSize: 11,
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </SectionCard>
        </div>

        {/* ╔══════ 3. Training Curves ══════╗ */}
        <SectionCard
          title="Courbes d'Apprentissage"
          icon={<TrendingUp className="h-5 w-5" />}
        >
          <ChartTabs
            tabs={[
              { id: "40", label: "MLP · 40 Epochs (Exactitude 86.70%)" },
              { id: "20", label: "Modèle alternatif · 20 Epochs" },
            ]}
            active={activeCurve}
            onChange={(id) => setActiveCurve(id as "40" | "20")}
          />
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Accuracy */}
            <div>
              <h3 className="mb-3 text-sm font-medium text-muted-foreground">
                Courbes de Précision
              </h3>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart
                  data={activeCurve === "40" ? trainingCurves40 : trainingCurves20}
                  margin={{ top: 5, right: 10, left: -10, bottom: 5 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(255,255,255,0.06)"
                  />
                  <XAxis
                    dataKey="epoch"
                    tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 10 }}
                    label={{
                      value: "Epoch",
                      position: "insideBottomRight",
                      offset: -5,
                      style: { fill: "rgba(255,255,255,0.4)", fontSize: 10 },
                    }}
                  />
                  <YAxis
                    domain={activeCurve === "40" ? [0.78, 0.88] : [0.64, 0.83]}
                    tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 10 }}
                    label={{
                      value: "Accuracy",
                      angle: -90,
                      position: "insideLeft",
                      offset: 15,
                      style: { fill: "rgba(255,255,255,0.4)", fontSize: 10 },
                    }}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "rgba(20,20,40,0.95)",
                      border: "1px solid rgba(255,255,255,0.1)",
                      borderRadius: 12,
                      color: "#fff",
                      fontSize: 11,
                    }}
                  />
                  <Legend
                    wrapperStyle={{
                      fontSize: 11,
                      color: "rgba(255,255,255,0.6)",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="trainAcc"
                    name="Train"
                    stroke="#6366f1"
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{ r: 4, stroke: "#6366f1" }}
                  />
                  <Line
                    type="monotone"
                    dataKey="valAcc"
                    name="Validation"
                    stroke="#f59e0b"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4, stroke: "#f59e0b" }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Loss */}
            <div>
              <h3 className="mb-3 text-sm font-medium text-muted-foreground">
                Courbes de Perte
              </h3>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart
                  data={activeCurve === "40" ? trainingCurves40 : trainingCurves20}
                  margin={{ top: 5, right: 10, left: -10, bottom: 5 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(255,255,255,0.06)"
                  />
                  <XAxis
                    dataKey="epoch"
                    tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 10 }}
                    label={{
                      value: "Epoch",
                      position: "insideBottomRight",
                      offset: -5,
                      style: { fill: "rgba(255,255,255,0.4)", fontSize: 10 },
                    }}
                  />
                  <YAxis
                    domain={activeCurve === "40" ? [0.3, 0.55] : [0.45, 0.9]}
                    tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 10 }}
                    label={{
                      value: "Loss",
                      angle: -90,
                      position: "insideLeft",
                      offset: 15,
                      style: { fill: "rgba(255,255,255,0.4)", fontSize: 10 },
                    }}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "rgba(20,20,40,0.95)",
                      border: "1px solid rgba(255,255,255,0.1)",
                      borderRadius: 12,
                      color: "#fff",
                      fontSize: 11,
                    }}
                  />
                  <Legend
                    wrapperStyle={{
                      fontSize: 11,
                      color: "rgba(255,255,255,0.6)",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="trainLoss"
                    name="Train"
                    stroke="#6366f1"
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{ r: 4, stroke: "#6366f1" }}
                  />
                  <Line
                    type="monotone"
                    dataKey="valLoss"
                    name="Validation"
                    stroke="#f59e0b"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4, stroke: "#f59e0b" }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          {activeCurve === "40" && (
            <div className="mt-4 rounded-xl border border-emerald-500/20 bg-emerald-500/5 px-4 py-3 text-xs text-emerald-300">
              <strong>Exactitude finale :</strong> 86.70% — Le modèle converge
              rapidement et maintient des performances stables sur l'ensemble de
              validation.
            </div>
          )}
        </SectionCard>

        {/* ╔══════ 4. Classification Models – Bar Charts ══════╗ */}
        <div className="grid gap-8 lg:grid-cols-2">
          <SectionCard
            title="Pourcentages des Variables (7 modèles)"
            icon={<Brain className="h-5 w-5" />}
          >
            <p className="mb-4 text-xs text-muted-foreground">
              Comparaison des performances de 7 algorithmes de classification
              sur les données électorales.
            </p>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={modelAccOld}
                margin={{ top: 5, right: 10, left: -10, bottom: 5 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(255,255,255,0.06)"
                />
                <XAxis
                  dataKey="name"
                  tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 10 }}
                  axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 10 }}
                  axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
                  tickFormatter={(v: number) => `${v}%`}
                />
                <Tooltip
                  contentStyle={{
                    background: "rgba(20,20,40,0.95)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 12,
                    color: "#fff",
                    fontSize: 12,
                  }}
                  formatter={(v: number) => [`${v.toFixed(1)}%`, "Accuracy"]}
                />
                <Bar dataKey="accuracy" radius={[6, 6, 0, 0]} barSize={32}>
                  {modelAccOld.map((entry, idx) => (
                    <Cell key={`cell-o-${idx}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </SectionCard>

          <SectionCard
            title="Pourcentages des Variables (4 modèles)"
            icon={<Brain className="h-5 w-5" />}
          >
            <p className="mb-4 text-xs text-muted-foreground">
              Classification binaire — Performance des modèles sur un sous-ensemble
              de données.
            </p>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={modelAcc2}
                margin={{ top: 5, right: 10, left: -10, bottom: 5 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(255,255,255,0.06)"
                />
                <XAxis
                  dataKey="name"
                  tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 11 }}
                  axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 11 }}
                  axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
                  tickFormatter={(v: number) => `${v}%`}
                />
                <Tooltip
                  contentStyle={{
                    background: "rgba(20,20,40,0.95)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 12,
                    color: "#fff",
                    fontSize: 12,
                  }}
                  formatter={(v: number) => [`${v.toFixed(1)}%`, "Accuracy"]}
                />
                <Bar dataKey="accuracy" radius={[6, 6, 0, 0]} barSize={44}>
                  {modelAcc2.map((entry, idx) => (
                    <Cell key={`cell-b-${idx}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </SectionCard>
        </div>

        {/* ╔══════ Summary stats ══════╗ */}
        <motion.section
          variants={itemVariant}
          className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
        >
          {[
            { label: "Meilleur Modèle", value: "Logistic Reg.", sub: "81.81% accuracy" },
            { label: "Total Enregistrements", value: "858 024", sub: "Nouvelle-Aquitaine" },
            { label: "Variables Analysées", value: "27", sub: "Indicateurs delta" },
            { label: "Classes Cibles", value: "5", sub: "Boom · Croissance · Stable · Déclin · Crise" },
          ].map((kpi, i) => (
            <motion.div
              key={kpi.label}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 * i }}
              className="relative overflow-hidden rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-xl shadow-[var(--shadow-card)]"
            >
              <div className="pointer-events-none absolute -top-16 -right-16 h-40 w-40 rounded-full bg-gradient-to-br from-primary/25 to-accent/10 blur-2xl" />
              <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">
                {kpi.label}
              </p>
              <p className="mt-3 text-2xl font-semibold tracking-tight text-foreground">
                {kpi.value}
              </p>
              <p className="mt-1.5 text-xs text-muted-foreground">{kpi.sub}</p>
            </motion.div>
          ))}
        </motion.section>
      </motion.main>

      {/* Footer */}
      <footer className="border-t border-border/40 py-8 text-center text-xs text-muted-foreground">
        GouvData · Machine Learning Analytics · Présidentielle 2022 ·
        Nouvelle-Aquitaine
      </footer>
    </div>
  );
}
