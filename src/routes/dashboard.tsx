import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  // eslint-disable-next-line @typescript-eslint/no-deprecated
  CartesianGrid, Cell, PieChart, Pie, Legend,
} from "recharts";
import { BarChart3, Brain, MapPin, ChevronDown, CheckCircle2, XCircle, TrendingUp } from "lucide-react";

export const Route = createFileRoute("/dashboard")({
  component: DashboardPage,
});

/* ═══════════════════════════════════════════════════════════════════════════
   CONSTANTS
═══════════════════════════════════════════════════════════════════════════ */
const MODELS = [
  { id: "xgboost",             name: "XGBoost",             key: "XGBoost" },
  { id: "random_forest",       name: "Random Forest",       key: "RandomForest" },
  { id: "gradient_boosting",   name: "Gradient Boosting",   key: "GradientBoosting" },
  { id: "logistic_regression", name: "Logistic Regression", key: "LogisticRegression" },
  { id: "svm_(linear)",        name: "SVM (Linear)",        key: "SVM" },
];

const DEPT_COLORS = [
  "#6366f1","#8b5cf6","#a78bfa","#06b6d4","#10b981",
  "#22c55e","#84cc16","#eab308","#f97316","#ef4444","#ec4899","#14b8a6",
];

/* ── Light palette ── */
const L = {
  pageBg:     "#eef1f8",
  white:      "#ffffff",
  border:     "#e2e8f4",
  dark:       "#0a0f2e",
  mid:        "#3d4f6a",
  muted:      "#7a8ea8",
  faint:      "#a0aec0",
  inputBg:    "#f5f7fc",
  inputBdr:   "#c5d3e8",
  active:     "#2a3d9e",
  activeLt:   "#dbeafe",
  activeDk:   "#1e3a8a",
  wrongLt:    "#fee2e2",
  wrongDk:    "#991b1b",
  labelUp:    "#64748b",
  accent:     "#4f6ef7",
  accentGlow: "rgba(79,110,247,0.15)",
};

/* ── Sidebar palette ── */
const SB = {
  bg:       "#080d28",
  navAct:   "#1a2870",
  subText:  "#94afd0",
  muted:    "#5d7090",
  sublabel: "#7080a8",
  divider:  "#131d3e",
};

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

/* ═══════════════════════════════════════════════════════════════════════════
   SMALL COMPONENTS
═══════════════════════════════════════════════════════════════════════════ */
function FrenchFlag({ w = 10, h = 22 }: { w?: number; h?: number }) {
  return (
    <div style={{ display: "flex", flexShrink: 0 }}>
      <div style={{ width: w, height: h, background: "#002395", borderRadius: "3px 0 0 3px" }} />
      <div style={{ width: w, height: h, background: "#ffffff" }} />
      <div style={{ width: w, height: h, background: "#ED2939", borderRadius: "0 3px 3px 0" }} />
    </div>
  );
}

function SectionCard({ title, children, style }: { title: string; children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <div style={{ background: L.white, borderRadius: 18, border: `1px solid ${L.border}`, padding: 22, marginBottom: 20, boxShadow: "0 2px 12px rgba(10,15,46,0.06)", ...style }}>
      <p style={{ color: L.dark, fontWeight: 700, fontSize: 14, margin: "0 0 16px", display: "flex", alignItems: "center", gap: 8, letterSpacing: "0.01em" }}>
        {title}
      </p>
      {children}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   MAIN PAGE
═══════════════════════════════════════════════════════════════════════════ */
function DashboardPage() {
  const [selectedModel, setSelectedModel] = useState("logistic_regression");
  const [selectedDept, setSelectedDept]   = useState("ALL");
  const [selectedCanton, setSelectedCanton] = useState("ALL");

  /* ── Data fetching ─────────────────────────────────────────────────── */
  /* Base file → models_metrics for the comparison cards */
  const { data: baseData } = useQuery({
    queryKey: ["base_predictions"],
    queryFn: async () => {
      const r = await fetch("/data/predictions.json");
      if (!r.ok) throw new Error("predictions.json manquant");
      return r.json();
    },
    staleTime: Infinity,
  });

  /* Per-model file → geographic levels + summary */
  const { data, isLoading } = useQuery({
    queryKey: ["predictions", selectedModel],
    queryFn: async () => {
      const r = await fetch(`/data/predictions_${selectedModel}.json`, { cache: "no-store" });
      if (!r.ok) throw new Error(`predictions_${selectedModel}.json manquant`);
      return r.json();
    },
    staleTime: 30_000,
  });

  /* ── Active entity ──────────────────────────────────────────────────── */
  const activeEntity = useMemo<Entity | null>(() => {
    if (!data) return null;
    if (selectedDept === "ALL") return data.levels?.region?.[0] ?? null;
    const dept = data.levels?.departement?.find((d: Entity) => d.entity === selectedDept) ?? null;
    if (!dept || selectedCanton === "ALL") return dept;
    return data.levels?.canton?.find((c: Entity) => c.entity === selectedCanton) ?? dept;
  }, [data, selectedDept, selectedCanton]);

  /* ── Table rows ─────────────────────────────────────────────────────── */
  const tableData = useMemo<Entity[]>(() => {
    if (!data) return [];
    if (selectedDept === "ALL") return data.levels?.departement ?? [];
    const cantons = (data.levels?.canton ?? []).filter((c: Entity) => c.parent === selectedDept);
    if (selectedCanton === "ALL") return cantons;
    return cantons.filter((c: Entity) => c.entity === selectedCanton);
  }, [data, selectedDept, selectedCanton]);

  /* ── Derived values ─────────────────────────────────────────────────── */
  const selectedModelDef = MODELS.find(m => m.id === selectedModel)!;
  const metrics = baseData?.models_metrics ?? {};

  const activeAcc: number | null =
    metrics[selectedModelDef.key]?.test_accuracy ??
    data?.summary?.model_accuracy ??
    null;

  const ecoState = (
    activeEntity?.economic_state?.toUpperCase() ?? "—"
  );
  const ecoScore = activeEntity?.economic_score?.toFixed(1) ?? "—";

  /* ── Chart data ─────────────────────────────────────────────────────── */
  const barData = MODELS.map(m => ({
    name: m.name,
    accuracy: metrics[m.key]?.test_accuracy ?? 0,
    active: m.id === selectedModel,
    fill: m.id === selectedModel ? L.accent : "#6366f1",
  }));

  const donutData = activeEntity
    ? [
        { name: "Macron", value: +(activeEntity.proba_macron ?? 0).toFixed(1), fill: "#1e2a78" },
        { name: "Le Pen", value: +(activeEntity.proba_lepen  ?? 0).toFixed(1), fill: "#ef4444" },
      ]
    : [];

  /* ─────────────────────────────────────────────────────────────────────── */
  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden", fontFamily: "'Space Grotesk', 'Sora', sans-serif" }}>

      {/* ════════════════════ SIDEBAR ════════════════════ */}
      <aside style={{
        width: 260, flexShrink: 0,
        background: `linear-gradient(180deg, #0b1030 0%, #080d28 100%)`,
        display: "flex", flexDirection: "column", overflowY: "auto",
        boxShadow: "2px 0 20px rgba(0,0,0,0.25)",
      }}>

        {/* Logo */}
        <div style={{ padding: "24px 20px 20px", borderBottom: `1px solid ${SB.divider}` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <FrenchFlag w={10} h={22} />
            <div>
              <p style={{ color: "#fff", fontWeight: 700, fontSize: 14, margin: 0 }}>GouvData</p>
              <p style={{ color: SB.muted, fontSize: 10, margin: 0, textTransform: "uppercase", letterSpacing: "0.1em" }}>ML Analytics</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div style={{ padding: "20px 14px 0" }}>
          <p style={{ color: SB.muted, fontSize: 10, fontWeight: 600, letterSpacing: "0.14em", textTransform: "uppercase", margin: "0 0 10px", paddingLeft: 4 }}>
            Navigation
          </p>

          {/* Dashboard — actif */}
          <div style={{
            background: "linear-gradient(135deg, #1e3080 0%, #2a3d9e 100%)",
            borderRadius: 10, padding: "10px 14px",
            marginBottom: 4, display: "flex", alignItems: "center", gap: 10, cursor: "default",
            boxShadow: "0 2px 12px rgba(79,110,247,0.25)",
            border: "1px solid rgba(100,130,255,0.2)",
          }}>
            <BarChart3 style={{ color: "#fff", width: 16, height: 16, flexShrink: 0 }} />
            <div>
              <p style={{ color: "#fff", fontWeight: 700, fontSize: 13, margin: 0 }}>Dashboard</p>
              <p style={{ color: SB.subText, fontSize: 10, margin: 0 }}>Prédictions géographiques</p>
            </div>
          </div>

          {/* Visualisation ML */}
          <Link to="/visualisation" style={{ textDecoration: "none", display: "block" }}>
            <div
              className="group"
              style={{ borderRadius: 10, padding: "10px 14px", marginBottom: 4, display: "flex", alignItems: "center", gap: 10, cursor: "pointer", transition: "background 0.15s" }}
              onMouseEnter={e => (e.currentTarget.style.background = "#1a2340")}
              onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
            >
              <Brain style={{ color: SB.muted, width: 16, height: 16, flexShrink: 0 }} />
              <div>
                <p style={{ color: SB.subText, fontWeight: 500, fontSize: 13, margin: 0 }}>Visualisation ML</p>
                <p style={{ color: SB.muted, fontSize: 10, margin: 0 }}>Graphiques & métriques</p>
              </div>
            </div>
          </Link>
        </div>

        <div style={{ margin: "16px 16px", borderTop: `1px solid ${SB.divider}` }} />

        {/* Périmètre */}
        <div style={{ padding: "0 16px" }}>
          <p style={{ color: SB.muted, fontSize: 10, fontWeight: 600, letterSpacing: "0.14em", textTransform: "uppercase", margin: "0 0 12px" }}>
            Périmètre
          </p>
          <div style={{ display: "flex", alignItems: "flex-start", gap: 10, marginBottom: 12 }}>
            <span style={{ color: "#5b7ab8", fontSize: 14, marginTop: 1 }}>📅</span>
            <div>
              <p style={{ color: SB.sublabel, fontSize: 10, margin: "0 0 2px" }}>Élection</p>
              <p style={{ color: "#fff", fontWeight: 600, fontSize: 12, margin: 0 }}>Présidentielle 2022</p>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
            <MapPin style={{ color: "#5b7ab8", width: 14, height: 14, marginTop: 1, flexShrink: 0 }} />
            <div>
              <p style={{ color: SB.sublabel, fontSize: 10, margin: "0 0 2px" }}>Région</p>
              <p style={{ color: "#fff", fontWeight: 600, fontSize: 12, margin: 0 }}>Nouvelle-Aquitaine</p>
            </div>
          </div>
        </div>

        <div style={{ margin: "16px 16px", borderTop: `1px solid ${SB.divider}` }} />

        {/* Modèle actif */}
        <div style={{ padding: "0 16px" }}>
          <p style={{ color: SB.muted, fontSize: 10, fontWeight: 600, letterSpacing: "0.14em", textTransform: "uppercase", margin: "0 0 10px" }}>
            Modèle actif
          </p>
          <motion.div
            key={selectedModel}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 10, padding: "12px 14px" }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <Brain style={{ color: "#6080e0", width: 15, height: 15, flexShrink: 0 }} />
              <p style={{ color: "#fff", fontWeight: 700, fontSize: 12, margin: 0 }}>{selectedModelDef.name}</p>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <p style={{ color: SB.sublabel, fontSize: 11, margin: 0 }}>Accuracy</p>
              <p style={{ color: "#fff", fontWeight: 700, fontSize: 12, margin: 0 }}>
                {activeAcc != null ? `${activeAcc.toFixed(1)}%` : "—"}
              </p>
            </div>
          </motion.div>
        </div>

        {/* Filtre résumé dans la sidebar */}
        {selectedDept !== "ALL" && (
          <>
            <div style={{ margin: "16px 16px", borderTop: `1px solid ${SB.divider}` }} />
            <div style={{ padding: "0 16px" }}>
              <p style={{ color: SB.muted, fontSize: 10, fontWeight: 600, letterSpacing: "0.14em", textTransform: "uppercase", margin: "0 0 8px" }}>
                Vue active
              </p>
              <p style={{ color: "#fff", fontSize: 12, fontWeight: 600, margin: "0 0 2px" }}>{selectedDept}</p>
              {selectedCanton !== "ALL" && (
                <p style={{ color: SB.subText, fontSize: 11, margin: 0 }}>Canton : {selectedCanton}</p>
              )}
              <button
                onClick={() => { setSelectedDept("ALL"); setSelectedCanton("ALL"); }}
                style={{ marginTop: 8, color: "#6080e0", fontSize: 11, background: "none", border: "none", cursor: "pointer", padding: 0, textDecoration: "underline" }}
              >
                Réinitialiser →
              </button>
            </div>
          </>
        )}

        {/* Spacer + Flag */}
        <div style={{ flex: 1 }} />
        <div style={{ padding: "20px", textAlign: "center", borderTop: `1px solid ${SB.divider}` }}>
          <div style={{ display: "flex", justifyContent: "center", marginBottom: 6 }}>
            <FrenchFlag w={14} h={38} />
          </div>
          <p style={{ color: SB.muted, fontSize: 10, textTransform: "uppercase", letterSpacing: "0.12em", margin: 0 }}>France</p>
        </div>
      </aside>

      {/* ════════════════════ MAIN ════════════════════ */}
      <main style={{ flex: 1, overflowY: "auto", background: L.pageBg }}>

        {/* ── Header ───────────────────────────────────────────────────── */}
        <div style={{
          textAlign: "center", padding: "32px 32px 24px",
          background: "linear-gradient(135deg, #ffffff 0%, #f5f7ff 100%)",
          borderBottom: `1px solid ${L.border}`,
          position: "relative", overflow: "hidden",
        }}>
          <div style={{
            position: "absolute", top: -60, right: -60, width: 200, height: 200,
            borderRadius: "50%", background: "radial-gradient(circle, rgba(79,110,247,0.08) 0%, transparent 70%)",
            pointerEvents: "none",
          }} />
          <span style={{
            display: "inline-block", background: "linear-gradient(135deg, #eef1ff, #dbeafe)",
            color: L.accent, fontWeight: 700, fontSize: 10, letterSpacing: "0.22em",
            textTransform: "uppercase", borderRadius: 20, padding: "4px 14px",
            border: `1px solid rgba(79,110,247,0.2)`, marginBottom: 12,
          }}>
            Présidentielle 2022 · Nouvelle-Aquitaine
          </span>
          <h1 style={{ color: L.dark, fontWeight: 800, fontSize: 28, margin: "0 0 8px", letterSpacing: "-0.02em" }}>
            Tableau de Bord Prédictif
          </h1>
          <p style={{ color: L.mid, fontSize: 13, margin: "0 0 20px" }}>
            Prédiction du vote par indicateurs socio-économiques · Région · Département · Canton
          </p>
          <Link
            to="/visualisation"
            style={{
              display: "inline-flex", alignItems: "center", gap: 8,
              background: "linear-gradient(135deg, #2a3d9e, #4f6ef7)",
              color: "#fff", borderRadius: 12, padding: "10px 24px", fontSize: 13,
              fontWeight: 600, textDecoration: "none", transition: "all 0.2s",
              boxShadow: "0 4px 14px rgba(79,110,247,0.35)",
            }}
            onMouseEnter={e => ((e.currentTarget as HTMLElement).style.transform = "translateY(-1px)")}
            onMouseLeave={e => ((e.currentTarget as HTMLElement).style.transform = "translateY(0)")}
          >
            <BarChart3 style={{ width: 16, height: 16 }} />
            Visualisation ML
          </Link>
        </div>

        {/* ── Content ──────────────────────────────────────────────────── */}
        <div style={{ padding: "24px 28px", maxWidth: 1300, margin: "0 auto" }}>

          {/* ── 5 Model Cards ─────────────────────────────────────────── */}
          <SectionCard title="⊕  Modèle d'Intelligence Artificielle">
            <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 12 }}>
              {MODELS.map(m => {
                const acc = metrics[m.key]?.test_accuracy ?? null;
                const active = m.id === selectedModel;
                return (
                  <motion.button
                    key={m.id}
                    onClick={() => { setSelectedModel(m.id); setSelectedDept("ALL"); setSelectedCanton("ALL"); }}
                    whileHover={{ scale: 1.04, y: -2 }}
                    whileTap={{ scale: 0.97 }}
                    style={{
                      background: active
                        ? "linear-gradient(135deg, #2a3d9e 0%, #4f6ef7 100%)"
                        : L.white,
                      border: `1px solid ${active ? "transparent" : L.border}`,
                      borderRadius: 14, padding: "18px 10px",
                      cursor: "pointer", textAlign: "center", transition: "all 0.18s",
                      boxShadow: active
                        ? "0 6px 24px rgba(79,110,247,0.35)"
                        : "0 1px 4px rgba(10,15,46,0.06)",
                    }}
                  >
                    <p style={{ color: active ? "rgba(255,255,255,0.65)" : L.labelUp, fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.14em", margin: "0 0 6px" }}>
                      Modèle
                    </p>
                    <p style={{ color: active ? "#fff" : L.dark, fontWeight: 700, fontSize: 12, margin: "0 0 10px", lineHeight: 1.3 }}>
                      {m.name}
                    </p>
                    <p style={{ color: active ? "#fff" : L.accent, fontWeight: 800, fontSize: 22, margin: 0, letterSpacing: "-0.02em" }}>
                      {acc != null ? `${acc.toFixed(1)}%` : "—"}
                    </p>
                  </motion.button>
                );
              })}
            </div>
          </SectionCard>

          {/* ── 3 KPI Cards ────────────────────────────────────────────── */}
          <AnimatePresence mode="wait">
            <motion.div
              key={`${selectedModel}-${selectedDept}-${selectedCanton}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 20 }}
            >
              {[
                {
                  label: `Vainqueur Prédit — ${activeEntity?.entity ?? "Nouvelle-Aquitaine"}`,
                  value: activeEntity?.predicted ?? (isLoading ? "…" : "—"),
                  sub:   `Résultat réel : ${activeEntity?.real ?? "—"}`,
                  correct: activeEntity ? activeEntity.is_correct : null,
                },
                {
                  label: "État Économique",
                  value: isLoading ? "…" : ecoState,
                  sub:   `Score : ${ecoScore}`,
                  correct: null,
                },
                {
                  label: `Accuracy — ${selectedModelDef.name}`,
                  value: activeAcc != null ? `${activeAcc.toFixed(1)}%` : (isLoading ? "…" : "—"),
                  sub:   "Sur l'ensemble d'entraînement socio-éco",
                  correct: null,
                },
              ].map((kpi, i) => (
                <motion.div
                  key={i}
                  transition={{ delay: i * 0.06 }}
                  style={{ background: L.white, borderRadius: 12, border: `1px solid ${L.border}`, padding: 20 }}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
                    <p style={{ color: L.muted, fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.14em", margin: 0 }}>
                      {kpi.label}
                    </p>
                    {kpi.correct === true  && <CheckCircle2 style={{ color: "#059669", width: 16, height: 16, flexShrink: 0 }} />}
                    {kpi.correct === false && <XCircle      style={{ color: "#dc2626", width: 16, height: 16, flexShrink: 0 }} />}
                  </div>
                  <p style={{ color: L.dark, fontWeight: 700, fontSize: 28, margin: "0 0 6px" }}>
                    {kpi.value}
                  </p>
                  <p style={{ color: L.faint, fontSize: 12, margin: 0 }}>{kpi.sub}</p>
                </motion.div>
              ))}
            </motion.div>
          </AnimatePresence>

          {/* ── Geographic Filters ────────────────────────────────────── */}
          <SectionCard title="▼  Filtres géographiques">
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>

              {/* Région (fixe) */}
              <div>
                <p style={{ color: L.labelUp, fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.12em", margin: "0 0 8px" }}>Région</p>
                <div style={{ background: L.inputBg, border: `1px solid ${L.inputBdr}`, borderRadius: 8, padding: "10px 14px", color: L.mid, fontSize: 13, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span>Nouvelle-Aquitaine</span>
                  <ChevronDown style={{ width: 14, height: 14, color: L.muted, opacity: 0.4 }} />
                </div>
              </div>

              {/* Département */}
              <div>
                <p style={{ color: L.labelUp, fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.12em", margin: "0 0 8px" }}>Département</p>
                <div style={{ position: "relative" }}>
                  <select
                    value={selectedDept}
                    onChange={e => { setSelectedDept(e.target.value); setSelectedCanton("ALL"); }}
                    style={{
                      width: "100%", background: L.inputBg, border: `1px solid ${L.inputBdr}`,
                      borderRadius: 8, padding: "10px 14px", color: L.dark,
                      fontSize: 13, cursor: "pointer", appearance: "auto", outline: "none",
                    }}
                  >
                    <option value="ALL">Tous les départements</option>
                    {data?.levels?.departement?.map((d: Entity) => (
                      <option key={d.entity} value={d.entity}>{d.entity}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Canton */}
              <div>
                <p style={{ color: L.labelUp, fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.12em", margin: "0 0 8px" }}>Canton</p>
                <select
                  value={selectedCanton}
                  onChange={e => setSelectedCanton(e.target.value)}
                  disabled={selectedDept === "ALL"}
                  style={{
                    width: "100%", background: L.inputBg, border: `1px solid ${L.inputBdr}`,
                    borderRadius: 8, padding: "10px 14px", color: L.dark,
                    fontSize: 13, cursor: selectedDept === "ALL" ? "not-allowed" : "pointer",
                    opacity: selectedDept === "ALL" ? 0.5 : 1, appearance: "auto", outline: "none",
                  }}
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
          </SectionCard>

          {/* ── Charts Row ──────────────────────────────────────────────── */}
          <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 20, marginBottom: 20 }}>

            {/* Bar chart — model comparison */}
            <div style={{ background: L.white, borderRadius: 16, border: `1px solid ${L.border}`, padding: 20 }}>
              <p style={{ color: L.dark, fontWeight: 700, fontSize: 15, margin: "0 0 4px" }}>
                <TrendingUp style={{ display: "inline", width: 16, height: 16, marginRight: 6, verticalAlign: "text-bottom" }} />
                Comparaison Accuracy — 5 Modèles
              </p>
              <p style={{ color: L.faint, fontSize: 11, margin: "0 0 16px" }}>
                Cliquez sur un modèle ci-dessus pour changer la vue
              </p>
              {barData.some(d => d.accuracy > 0) ? (
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={barData} barSize={36}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f2f8" vertical={false} />
                    <XAxis dataKey="name" tick={{ fill: L.labelUp, fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis domain={[50, 100]} tick={{ fill: L.labelUp, fontSize: 11 }} axisLine={false} tickLine={false} unit="%" />
                    <Tooltip
                      formatter={(v: unknown) => [`${Number(v).toFixed(2)}%`, "Accuracy"] as [string, string]}
                      contentStyle={{ background: L.white, border: `1px solid ${L.border}`, borderRadius: 8, fontSize: 12 }}
                      cursor={{ fill: L.pageBg }}
                    />
                    <Bar dataKey="accuracy" radius={[6, 6, 0, 0]}>
                      {barData.map((entry, i) => (
                        // eslint-disable-next-line @typescript-eslint/no-deprecated
                        <Cell key={i} fill={entry.fill} opacity={entry.active ? 1 : 0.65} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div style={{ height: 220, display: "flex", alignItems: "center", justifyContent: "center", color: L.faint, fontSize: 13 }}>
                  Chargement des métriques…
                </div>
              )}
            </div>

            {/* Donut — Macron vs Le Pen */}
            <div style={{ background: L.white, borderRadius: 16, border: `1px solid ${L.border}`, padding: 20 }}>
              <p style={{ color: L.dark, fontWeight: 700, fontSize: 15, margin: "0 0 4px" }}>
                Probabilités prédites
              </p>
              <p style={{ color: L.faint, fontSize: 11, margin: "0 0 8px" }}>
                {activeEntity?.entity ?? "Nouvelle-Aquitaine"}
              </p>
              {donutData.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={donutData}
                      cx="50%" cy="50%"
                      innerRadius={60} outerRadius={90}
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
                    <Legend formatter={(v) => <span style={{ color: L.mid, fontSize: 12 }}>{v}</span>} />
                    <Tooltip formatter={(v: unknown) => [`${Number(v)}%`] as [string]} contentStyle={{ background: L.white, border: `1px solid ${L.border}`, borderRadius: 8, fontSize: 12 }} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div style={{ height: 220, display: "flex", alignItems: "center", justifyContent: "center", color: L.faint, fontSize: 13 }}>
                  {isLoading ? "Chargement…" : "Sélectionnez un département"}
                </div>
              )}
            </div>
          </div>

          {/* ── Results Table ────────────────────────────────────────────── */}
          {tableData.length > 0 && (
            <SectionCard title={`📋  Résultats — ${selectedDept === "ALL" ? "Départements" : selectedCanton === "ALL" ? `Cantons de ${selectedDept}` : selectedCanton}`}>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                  <thead>
                    <tr style={{ background: L.pageBg }}>
                      {["Entité", "Prédit", "Réel", "Correct", "Macron %", "Le Pen %", "Conf."].map(h => (
                        <th key={h} style={{
                          padding: "10px 14px", textAlign: "left",
                          color: L.labelUp, fontWeight: 700, fontSize: 10,
                          textTransform: "uppercase", letterSpacing: "0.1em",
                          borderBottom: `1px solid ${L.border}`,
                        }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {tableData.slice(0, 30).map((row: Entity, i: number) => (
                      <motion.tr
                        key={i}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: i * 0.02 }}
                        style={{ borderBottom: `1px solid #f0f2f8`, cursor: "default" }}
                        onMouseEnter={e => (e.currentTarget.style.background = L.pageBg)}
                        onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
                      >
                        <td style={{ padding: "10px 14px", fontWeight: 600, color: L.dark }}>{row.entity}</td>
                        <td style={{ padding: "10px 14px" }}>
                          <span style={{
                            background: row.predicted === "MACRON" ? L.activeLt : L.wrongLt,
                            color: row.predicted === "MACRON" ? L.activeDk : L.wrongDk,
                            borderRadius: 6, padding: "2px 8px", fontWeight: 600, fontSize: 12,
                          }}>{row.predicted}</span>
                        </td>
                        <td style={{ padding: "10px 14px", color: L.mid }}>{row.real}</td>
                        <td style={{ padding: "10px 14px" }}>
                          {row.is_correct
                            ? <CheckCircle2 style={{ color: "#059669", width: 16, height: 16 }} />
                            : <XCircle      style={{ color: "#dc2626", width: 16, height: 16 }} />}
                        </td>
                        <td style={{ padding: "10px 14px", color: L.mid }}>
                          {row.proba_macron != null ? `${row.proba_macron.toFixed(1)}%` : "—"}
                        </td>
                        <td style={{ padding: "10px 14px", color: L.mid }}>
                          {row.proba_lepen != null ? `${row.proba_lepen.toFixed(1)}%` : "—"}
                        </td>
                        <td style={{ padding: "10px 14px", color: L.faint }}>{row.confidence ?? "—"}</td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
                {tableData.length > 30 && (
                  <p style={{ color: L.faint, fontSize: 12, margin: "12px 0 0", textAlign: "center" }}>
                    {tableData.length - 30} lignes supplémentaires (affinez le filtre canton pour voir plus)
                  </p>
                )}
              </div>
            </SectionCard>
          )}

          {/* ── Département badges ───────────────────────────────────────── */}
          <div style={{ textAlign: "center", padding: "8px 0 32px" }}>
            <div style={{ display: "flex", justifyContent: "center", gap: 8, marginBottom: 8, flexWrap: "wrap" }}>
              {DEPT_COLORS.map((c, i) => (
                <motion.div
                  key={i}
                  whileHover={{ scale: 1.3 }}
                  style={{ width: 22, height: 22, background: c, borderRadius: 6, cursor: "default" }}
                />
              ))}
            </div>
            <p style={{ color: L.faint, fontSize: 12, margin: 0 }}>
              12 départements · Nouvelle-Aquitaine
            </p>
          </div>

          {isLoading && (
            <div style={{ textAlign: "center", padding: "40px 0", color: L.muted, fontSize: 13 }}>
              <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }} style={{ display: "inline-block", width: 20, height: 20, border: "2px solid #dde3f0", borderTopColor: L.active, borderRadius: "50%", marginBottom: 10 }} />
              <p style={{ margin: 0 }}>Chargement des prédictions…</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
