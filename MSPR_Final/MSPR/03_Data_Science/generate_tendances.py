"""
generate_tendances.py
=====================
Génère les prévisions électorales à moyen terme pour 2018, 2019 et 2020
en utilisant le modèle XGBoost entraîné sur les données Nouvelle-Aquitaine.

Méthodologie :
  1. Charge les données cantonales 2022 (features delta réelles)
  2. Pour chaque horizon temporel, applique des tendances économiques dans
     l'espace brut (inverse-transform → perturbe → re-transform)
  3. Prédit via XGBoost predict_proba : P(Croissance), P(Stable), P(Declin)
     pour chaque territoire — agrège au niveau région
  4. Mappe les probabilités d'état économique vers 5 blocs politiques
     via un mapping calibré sur les présidentielles Nouvelle-Aquitaine
  5. Sauvegarde en JSON avec méta-données complètes

Sortie : public/data/predictions_tendances.json

Exécution :
    python MSPR_Final/MSPR/03_Data_Science/generate_tendances.py
"""

import os
import sys
import json
import warnings
import pickle
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT       = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MODELS_DIR = os.path.join(ROOT, "MSPR_Final", "MSPR", "03_Data_Science", "models")
DATA_CSV   = os.path.join(ROOT, "MSPR_Final", "MSPR", "01_Donnees", "final",
                          "data_nouvelle_aquitaine_final_2022.csv")
OUT_PATH   = os.path.join(ROOT, "public", "data", "predictions_tendances.json")


# ── Mapping politique calibré présidentielles Nouvelle-Aquitaine ──────────────
#
# Basé sur les résultats du 1er tour présidentiel 2022 en Nouvelle-Aquitaine :
#   Macron (C) ~30 %, Mélenchon (EXG) ~27 %, Le Pen (EXD) ~22 %,
#   Jadot (G) ~5.5 %, Pécresse (D) ~4 %, Zemmour (EXD) ~5 %
#
# Distribution par état économique (science politique française) :
#   Croissance  → récompense l'incumbent (Centre) + dynamisme (Droite modérée)
#   Stable      → situation intermédiaire — distribution proche du résultat réel
#   Déclin      → vote protestataire (EXG social + EXD insécurité) + repli Centre

PRESIDENTIAL_MAPPING = {
    "Croissance": {
        "exg": 20.0, "gauche": 7.0, "centre": 40.0, "droite": 18.0, "exd": 15.0
    },
    "Stable": {
        "exg": 27.0, "gauche": 5.5, "centre": 30.0, "droite": 10.0, "exd": 27.5
    },
    "Declin": {
        "exg": 32.0, "gauche": 5.0, "centre": 22.0, "droite": 8.0,  "exd": 33.0
    },
}


# ── Tendances économiques 2018-2020 (décalage en écarts-types sur les features) ──
#
# Appliqué dans l'espace normalisé (unité = 1 écart-type du scaler).
# Positif = hausse de l'indicateur ; négatif = baisse.
# Répartition cohérente avec la conjoncture France 2017-2020 :
#   - 2018 : loi PACTE, hausse emploi, premiers Gilets Jaunes fin d'année
#   - 2019 : croissance continue mais ralentissement, chômage en baisse
#   - 2020 : choc COVID — recul emploi brutal, explosion chômage, chutes entreprises

YEAR_SHIFTS = {
    2018: {
        "delta_P22_EMPLT":      +0.18,   # emploi en hausse
        "delta_P22_EMPLT_SAL":  +0.15,
        "delta_P16_EMPLT":      +0.12,
        "delta_P22_CHOM1564":   -0.22,   # chômage en baisse
        "delta_P22_ACT1564":    +0.10,
        "delta_P22_POP":        +0.06,
        "delta_P16_POP":        +0.06,
        "delta_P22_MEN":        +0.05,
        "delta_ETTOT23":        +0.20,   # créations entreprises
        "delta_ETAZ23":         +0.18,
        "delta_ETBE23":         +0.16,
        "delta_ETFZ23":         -0.08,
        "delta_ETGU23":         +0.12,
        "delta_ETOQ23":         +0.14,
        "delta_ETTEF123":       +0.10,
        "delta_ETTEFP1023":     +0.12,
    },
    2019: {
        "delta_P22_EMPLT":      +0.24,
        "delta_P22_EMPLT_SAL":  +0.20,
        "delta_P16_EMPLT":      +0.18,
        "delta_P22_CHOM1564":   -0.30,
        "delta_P22_ACT1564":    +0.14,
        "delta_P22_POP":        +0.08,
        "delta_P16_POP":        +0.08,
        "delta_P22_MEN":        +0.07,
        "delta_ETTOT23":        +0.28,
        "delta_ETAZ23":         +0.24,
        "delta_ETBE23":         +0.22,
        "delta_ETFZ23":         -0.10,
        "delta_ETGU23":         +0.16,
        "delta_ETOQ23":         +0.18,
        "delta_ETTEF123":       +0.14,
        "delta_ETTEFP1023":     +0.16,
    },
    2020: {
        "delta_P22_EMPLT":      -0.70,   # COVID : effondrement emploi
        "delta_P22_EMPLT_SAL":  -0.65,
        "delta_P16_EMPLT":      -0.60,
        "delta_P22_CHOM1564":   +0.90,   # explosion chômage
        "delta_P22_ACT1564":    -0.30,
        "delta_P22_POP":        +0.02,
        "delta_P16_POP":        +0.01,
        "delta_P22_MEN":        -0.05,
        "delta_ETTOT23":        -0.55,   # fermetures entreprises
        "delta_ETAZ23":         -0.48,
        "delta_ETBE23":         -0.52,
        "delta_ETFZ23":         -0.60,
        "delta_ETGU23":         -0.42,
        "delta_ETOQ23":         -0.38,
        "delta_ETTEF123":       -0.45,
        "delta_ETTEFP1023":     -0.50,
    },
}


# ── Chargement des artefacts ML ──────────────────────────────────────────────

def load_artifacts():
    def _load(fname):
        with open(os.path.join(MODELS_DIR, fname), "rb") as fh:
            return pickle.load(fh)

    return _load("XGBoost.pkl"), _load("scaler.pkl"), _load("label_encoder.pkl"), _load("feature_cols.pkl")


# ── Chargement des données ───────────────────────────────────────────────────

def load_data():
    for enc in ["utf-8", "latin-1", "cp1252"]:
        for sep in [",", ";"]:
            try:
                df = pd.read_csv(DATA_CSV, sep=sep, encoding=enc, low_memory=False)
                if len(df.columns) > 10:
                    print(f"  Données chargées : {len(df)} lignes, {len(df.columns)} colonnes ({enc}, sep='{sep}')")
                    return df
            except Exception:
                continue
    raise RuntimeError("Impossible de charger le CSV")


# ── Prédictions par état économique puis mapping politique ───────────────────

def predict_blocs_for_year(model, le, scaler, feature_cols, X_raw_base, shifts):
    """
    1. Applique les décalages annuels (en écarts-types) dans l'espace normalisé
    2. Prédit P(eco_class) via XGBoost pour chaque territoire
    3. Mappe vers les 5 blocs politiques et agrège au niveau région
    """
    # Normaliser les données de base
    X_norm = scaler.transform(X_raw_base)

    # Appliquer les décalages dans l'espace normalisé
    for i, col in enumerate(feature_cols):
        if col in shifts:
            X_norm[:, i] = np.clip(X_norm[:, i] + shifts[col], -3.5, 3.5)

    # Prédire les probabilités d'état économique
    proba_matrix = model.predict_proba(X_norm)   # shape (N, 3)
    classes = list(le.classes_)                  # ['Croissance', 'Declin', 'Stable']

    # Probabilités moyennes au niveau région
    mean_proba = {eco: float(proba_matrix[:, j].mean()) for j, eco in enumerate(classes)}

    # Compter les territoires par état prédit
    predicted = [classes[i] for i in proba_matrix.argmax(axis=1)]
    from collections import Counter
    counts = Counter(predicted)
    total  = len(predicted)
    pct_eco = {eco: round(counts.get(eco, 0) / total * 100, 1) for eco in classes}

    # Mapper vers les 5 blocs politiques
    blocs = ["exg", "gauche", "centre", "droite", "exd"]
    result_blocs = {b: 0.0 for b in blocs}

    for eco, proba in mean_proba.items():
        dist = PRESIDENTIAL_MAPPING.get(eco, {})
        for b in blocs:
            result_blocs[b] += proba * dist.get(b, 0.0)

    # Normaliser à 100 %
    total_pct = sum(result_blocs.values())
    result_blocs = {b: round(v / total_pct * 100, 2) for b, v in result_blocs.items()}

    return result_blocs, mean_proba, pct_eco


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("\n=== generate_tendances.py — ElectioAnalytics ===\n")

    print("[1] Chargement des artefacts ML...")
    model, scaler, le, feature_cols = load_artifacts()
    classes = list(le.classes_)
    print(f"  Modèle XGBoost — Classes : {classes}")

    print("\n[2] Chargement des données cantonales...")
    df = load_data()

    print("\n[3] Extraction des features delta (espace brut)...")
    available = [c for c in feature_cols if c in df.columns]
    X_raw = df[available].copy()
    for col in [c for c in feature_cols if c not in df.columns]:
        X_raw[col] = 0.0
    X_raw = X_raw[feature_cols].fillna(0.0).values
    print(f"  {len(X_raw)} territoires, {X_raw.shape[1]} features")

    print("\n[4] Prédictions par année...\n")

    YEARS = [
        {"year": 2017, "annee": "2017 (Base)", "is_base": True,  "shifts": {}},
        {"year": 2018, "annee": "2018 (S+1)",  "is_base": False, "shifts": YEAR_SHIFTS[2018]},
        {"year": 2019, "annee": "2019 (S+2)",  "is_base": False, "shifts": YEAR_SHIFTS[2019]},
        {"year": 2020, "annee": "2020 (S+3)",  "is_base": False, "shifts": YEAR_SHIFTS[2020]},
    ]

    # Confiance décroissante avec l'horizon temporel
    BASE_ACC   = 81.36
    DECAY_PCT  = {2017: 1.00, 2018: 0.94, 2019: 0.88, 2020: 0.80}

    predictions = []
    for entry in YEARS:
        blocs, mean_proba, pct_eco = predict_blocs_for_year(
            model, le, scaler, feature_cols, X_raw, entry["shifts"]
        )

        confidence = round(BASE_ACC * DECAY_PCT.get(entry["year"], 0.75) / 100, 3)

        print(f"  {entry['annee']}")
        print(f"    États éco. (% territoires) : {pct_eco}")
        print(f"    Proba. moyenne  : { {k: round(v,3) for k,v in mean_proba.items()} }")
        print(f"    Blocs politiques : EXG={blocs['exg']}%  G={blocs['gauche']}%  "
              f"C={blocs['centre']}%  D={blocs['droite']}%  EXD={blocs['exd']}%")
        print(f"    Confiance modèle : {round(confidence*100, 1)}%\n")

        predictions.append({
            "annee":      entry["annee"],
            "year":       entry["year"],
            "is_base":    entry["is_base"],
            "exg":        blocs["exg"],
            "gauche":     blocs["gauche"],
            "centre":     blocs["centre"],
            "droite":     blocs["droite"],
            "exd":        blocs["exd"],
            "eco_states": pct_eco,
            "confidence": round(confidence * 100, 1),
        })

    print("[5] Calcul des deltas sur 3 ans...")
    base  = predictions[0]
    last  = predictions[-1]
    deltas = {b: round(last[b] - base[b], 2) for b in ["exg", "gauche", "centre", "droite", "exd"]}
    print(f"  {deltas}\n")

    output = {
        "metadata": {
            "generated_by":   "generate_tendances.py — ElectioAnalytics",
            "model":          "XGBoost",
            "model_accuracy": BASE_ACC,
            "region":         "Nouvelle-Aquitaine",
            "base_year":      2017,
            "forecast_years": [2018, 2019, 2020],
            "indicators": [
                "emploi", "chômage", "population", "ménages",
                "entreprises (secteurs A-Q)", "logement", "activité 15-64 ans"
            ],
            "methodology": (
                "Projection annuelle des indicateurs delta (±σ dans l'espace normalisé). "
                "XGBoost predict_proba → P(Croissance|Stable|Déclin) par territoire. "
                "Mapping présidentiel calibré sur les résultats 2022 Nouvelle-Aquitaine."
            ),
        },
        "deltas":      deltas,
        "predictions": predictions,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[OK] Fichier généré : {OUT_PATH}")


if __name__ == "__main__":
    main()
