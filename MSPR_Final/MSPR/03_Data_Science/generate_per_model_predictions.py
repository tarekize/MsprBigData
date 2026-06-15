"""
generate_per_model_predictions.py
==================================
Génère les fichiers JSON par modèle requis par le frontend ElectioAnalytics.

Le fichier predictions.json contient les prédictions de TOUS les modèles dans
le champ `predictions_by_model`. Le frontend attend des fichiers séparés :
  - predictions_xgboost.json
  - predictions_random_forest.json
  - predictions_gradient_boosting.json
  - predictions_logistic_regression.json
  - predictions_svm_(linear).json

Ce script extrait les données par modèle et génère ces fichiers avec la
structure attendue par le frontend (summary.model_name, levels.region, etc.)

Exécution :
    python MSPR_Final/MSPR/03_Data_Science/generate_per_model_predictions.py
"""

import os
import sys
import json
import warnings

warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT      = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PRED_PATH = os.path.join(ROOT, "public", "data", "predictions.json")
OUT_DIR   = os.path.join(ROOT, "public", "data")
CSV_PATH  = os.path.join(ROOT, "MSPR_Final", "MSPR", "01_Donnees", "final",
                         "data_nouvelle_aquitaine_final_2022.csv")

# ── Mapping : id frontend → clé dans predictions_by_model ────────────────────
MODEL_MAP = {
    "xgboost":            {"key": "XGBoost",           "label": "XGBoost"},
    "random_forest":      {"key": "RandomForest",       "label": "Random Forest"},
    "gradient_boosting":  {"key": "GradientBoosting",   "label": "Gradient Boosting"},
    "logistic_regression":{"key": "LogisticRegression", "label": "Logistic Regression"},
    "svm_(linear)":       {"key": "SVM",                "label": "SVM (Linear)"},
}

# Mapping état économique ML → EcoState frontend
ECO_MAP = {
    "Croissance": "growth",
    "Stable":     "stable",
    "Declin":     "decline",
}

# Mapping candidat prédit → bord politique
CANDIDATE_SIDE = {
    "MACRON":  "centre",
    "LE PEN":  "extreme-droite",
}


def load_canton_dept_mapping():
    """
    Lit le CSV pour construire un dict {NOM_CANTON_UPPER: NOM_DEPT_UPPER}.
    Utilise pandas si disponible, sinon csv module.
    """
    mapping = {}
    if not os.path.exists(CSV_PATH):
        print("  [WARN] CSV introuvable — les cantons n'auront pas de parent département")
        return mapping

    try:
        import pandas as pd
        for enc in ["utf-8", "latin-1", "cp1252"]:
            try:
                df = pd.read_csv(CSV_PATH, usecols=[0, 1, 2, 3],
                                 header=0, sep=",", encoding=enc,
                                 low_memory=False, nrows=5000)
                col_dept   = df.columns[1]  # Libellé du département
                col_canton = df.columns[3]  # Libellé du canton
                for _, row in df.drop_duplicates(subset=[col_canton]).iterrows():
                    canton_name = str(row[col_canton]).strip().upper()
                    dept_name   = str(row[col_dept]).strip().upper()
                    if canton_name and dept_name and canton_name != "NAN":
                        mapping[canton_name] = dept_name
                print(f"  Mapping canton→dept chargé : {len(mapping)} cantons uniques")
                return mapping
            except Exception:
                continue
    except ImportError:
        pass

    # Fallback : csv module
    import csv
    for enc in ["utf-8", "latin-1", "cp1252"]:
        try:
            with open(CSV_PATH, encoding=enc, newline="") as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                for i, row in enumerate(reader):
                    if i >= 5000:
                        break
                    if len(row) >= 4:
                        dept_name   = row[1].strip().upper()
                        canton_name = row[3].strip().upper()
                        if canton_name and dept_name:
                            mapping[canton_name] = dept_name
            print(f"  Mapping canton→dept chargé (csv) : {len(mapping)} entrées")
            return mapping
        except Exception:
            continue

    print("  [WARN] Impossible de lire le CSV pour le mapping canton→dept")
    return mapping


def project_entity(entity, model_key, level, canton_dept_map):
    """
    Extrait les prédictions d'un modèle spécifique pour une entité
    et retourne un objet avec la structure attendue par le frontend.
    """
    by_model  = entity.get("predictions_by_model", {})
    m         = by_model.get(model_key, {})

    predicted    = m.get("predicted",    entity.get("predicted", "MACRON"))
    eco_class    = m.get("eco_class",    "Stable")
    proba_macron = float(m.get("proba_macron", entity.get("proba_macron", 50.0)))
    proba_lepen  = float(m.get("proba_lepen",  entity.get("proba_lepen",  50.0)))
    confidence   = m.get("confidence", entity.get("conf", "—"))
    is_correct   = predicted == entity.get("real", "")

    result = {
        "entity":         entity["entity"],
        "real":           entity.get("real", "—"),
        "predicted":      predicted,
        "is_correct":     is_correct,
        "economic_state": ECO_MAP.get(eco_class, "stable"),
        "economic_score": round(proba_macron, 2),
        "political_side": CANDIDATE_SIDE.get(predicted, "centre"),
        "proba": {
            "MACRON":  proba_macron,
            "LE PEN":  proba_lepen,
        },
        "proba_macron": proba_macron,
        "proba_lepen":  proba_lepen,
        "confidence":   confidence,
    }

    if level == "canton":
        result["parent"] = canton_dept_map.get(entity["entity"].upper())

    return result


def main():
    print("\n=== generate_per_model_predictions.py — ElectioAnalytics ===\n")

    print("[1] Chargement de predictions.json...")
    with open(PRED_PATH, encoding="utf-8") as f:
        pred = json.load(f)
    print(f"  Région: {pred['summary']['region_name']}")
    print(f"  Modèles disponibles dans le JSON: {list(pred.get('models_metrics', {}).keys())}")

    print("\n[2] Construction du mapping canton→département...")
    canton_dept_map = load_canton_dept_mapping()

    print("\n[3] Génération des fichiers par modèle...\n")

    from collections import Counter

    for model_id, model_info in MODEL_MAP.items():
        model_key   = model_info["key"]
        model_label = model_info["label"]

        metrics  = pred.get("models_metrics", {}).get(model_key, {})
        accuracy = metrics.get("test_accuracy", metrics.get("cv_accuracy", 0.0))

        region_data = [
            project_entity(e, model_key, "region", canton_dept_map)
            for e in pred["levels"]["region"]
        ]
        dept_data = [
            project_entity(e, model_key, "departement", canton_dept_map)
            for e in pred["levels"]["departement"]
        ]
        canton_data = [
            project_entity(e, model_key, "canton", canton_dept_map)
            for e in pred["levels"]["canton"]
        ]

        dept_counts = Counter(e["predicted"] for e in dept_data)

        output = {
            "summary": {
                "region_name":      pred["summary"]["region_name"],
                "model_name":       model_label,
                "model_accuracy":   round(accuracy, 2),
                "predicted_winner": region_data[0]["predicted"] if region_data else "—",
                "real_winner":      region_data[0]["real"]      if region_data else "—",
                "economic_state":   region_data[0]["economic_state"] if region_data else "stable",
                "political_side":   region_data[0]["political_side"] if region_data else "centre",
            },
            "political_real": pred.get("political_real", []),
            "political_predicted": [
                {"party": "MACRON", "count": dept_counts.get("MACRON", 0), "color": "#0055A4"},
                {"party": "LE PEN", "count": dept_counts.get("LE PEN", 0), "color": "#8B0000"},
            ],
            "levels": {
                "region":      region_data,
                "departement": dept_data,
                "canton":      canton_data,
            },
        }

        out_path = os.path.join(OUT_DIR, f"predictions_{model_id}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        region_pred = region_data[0]["predicted"] if region_data else "—"
        correct_dept = sum(1 for e in dept_data if e["is_correct"])
        print(f"  [{model_label}] acc={accuracy}%  région→{region_pred}  "
              f"depts corrects={correct_dept}/{len(dept_data)}  "
              f"→ predictions_{model_id}.json ✓")

    print(f"\n[OK] {len(MODEL_MAP)} fichiers générés dans public/data/\n")


if __name__ == "__main__":
    main()
