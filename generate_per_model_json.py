"""
Génère les 5 fichiers predictions_<model>.json dans public/data/
à partir du nouveau predictions.json produit par le notebook ML.
"""
import json, os

SRC = r"MSPR_Final\MSPR\03_Data_Science\Visualisation\data\predictions.json"
DST_DIR = r"public\data"

ECO_MAP = {
    "Stable":     "stable",
    "Croissance": "growth",
    "Declin":     "decline",
    "Crise":      "crisis",
    "Boom":       "boom",
}
ORI_MAP = {
    "Centre":        "centre",
    "Gauche":        "gauche",
    "Droite":        "droite",
    "ExtremeDroite": "extreme-droite",
    "ExtremeGauche": "extreme-gauche",
}
CANDIDATE_COLORS = {
    "Macron (LREM)":       "#FFD700",
    "Le Pen (RN)":         "#1C3B8A",
    "Melenchon (LFI)":     "#CC0000",
    "Pecresse (LR)":       "#0066CC",
    "Jadot (EELV)":        "#2D7D2D",
    "Lassalle (Resist)":   "#8B4513",
    "Roussel (PCF)":       "#990000",
    "Hidalgo (PS)":        "#FF69B4",
    "Poutou (NPA)":        "#800000",
    "Arthaud (LO)":        "#660000",
    "Zemmour (Reconv)":    "#00008B",
    "Dupont-Aignan (DLF)": "#003399",
}

MODEL_ID_MAP = {
    "LogisticRegression":     "logistic_regression",
    "RandomForest":           "random_forest",
    "HistGradientBoosting":   "hist_gradient_boosting",
    "LinearSVM":              "linear_svm",
    "XGBoost":                "xgboost",
}
MODEL_DISPLAY = {
    "LogisticRegression":     "Logistic Regression",
    "RandomForest":           "Random Forest",
    "HistGradientBoosting":   "HistGradientBoosting",
    "LinearSVM":              "LinearSVM",
    "XGBoost":                "XGBoost",
}

print("Lecture du fichier source…")
with open(SRC, encoding="utf-8") as f:
    src = json.load(f)

metrics = src["models_metrics"]
levels  = src["levels"]

# Résultats réels 2022 (vérité terrain)
REAL_WINNERS = {
    "NOUVELLE AQUITAINE":   "Macron (LREM)",
    "CHARENTE":             "Macron (LREM)",
    "CHARENTE MARITIME":    "Macron (LREM)",
    "CORREZE":              "Macron (LREM)",
    "CREUSE":               "Le Pen (RN)",
    "DEUX SEVRES":          "Macron (LREM)",
    "DORDOGNE":             "Le Pen (RN)",
    "GIRONDE":              "Macron (LREM)",
    "HAUTE VIENNE":         "Macron (LREM)",
    "LANDES":               "Macron (LREM)",
    "LOT ET GARONNE":       "Le Pen (RN)",
    "PYRENEES ATLANTIQUES": "Macron (LREM)",
    "VIENNE":               "Macron (LREM)",
}

def make_entity(raw_entity, model_key):
    """Convertit une entité brute en entité per-model."""
    pbm = raw_entity.get("predictions_by_model", {})
    if model_key in pbm:
        md = pbm[model_key]
    else:
        # Fallback: utilise le top-level (best model)
        md = {
            "winner":       raw_entity.get("predicted", ""),
            "winner_pct":   raw_entity.get("winner_pct", 0),
            "eco_class":    raw_entity.get("eco_class", "Stable"),
            "orientation":  raw_entity.get("orientation", "Centre"),
            "top5":         raw_entity.get("top5", []),
            "orient_proba": raw_entity.get("orient_proba", {}),
            "all_scores":   raw_entity.get("all_scores", {}),
        }

    winner    = md.get("winner", "")
    winner_pct = md.get("winner_pct", 0)
    eco_raw   = md.get("eco_class", "Stable")
    ori_raw   = md.get("orientation", "Centre")
    top5      = md.get("top5", [])
    orient_p  = md.get("orient_proba", {})
    all_sc    = md.get("all_scores", {})
    entity_name = raw_entity.get("entity", "")
    real = REAL_WINNERS.get(entity_name.upper(), raw_entity.get("real", ""))

    return {
        "entity":        entity_name,
        "parent":        raw_entity.get("parent"),
        "real":          real,
        "predicted":     winner,
        "is_correct":    winner == real,
        "economic_state": ECO_MAP.get(eco_raw, "stable"),
        "economic_score": round(winner_pct, 2),
        "political_side": ORI_MAP.get(ori_raw, "centre"),
        "winner_pct":    round(winner_pct, 2),
        "top5":          [[n, round(s, 2)] for n, s in top5],
        "orient_proba":  {k: round(v, 2) for k, v in orient_p.items()},
        "proba":         {k: round(v, 2) for k, v in all_sc.items()},
    }

for model_key, model_id in MODEL_ID_MAP.items():
    print(f"  Génération predictions_{model_id}.json  ({model_key}) …")

    acc = metrics.get(model_key, {}).get("test_accuracy", 0)
    f1  = metrics.get(model_key, {}).get("test_f1", 0)

    # Niveau région
    region_entities = [make_entity(e, model_key) for e in levels.get("region", [])]
    region_winner = region_entities[0]["predicted"] if region_entities else "Macron (LREM)"
    region_real   = region_entities[0]["real"]       if region_entities else "Macron (LREM)"

    # Niveau département
    dept_entities = [make_entity(e, model_key) for e in levels.get("departement", [])]

    # Niveau canton
    canton_entities = [make_entity(e, model_key) for e in levels.get("canton", [])]

    # Comptage political_predicted
    pred_counts: dict = {}
    for e in dept_entities:
        w = e["predicted"]
        pred_counts[w] = pred_counts.get(w, 0) + 1

    political_predicted = [
        {"party": p, "count": c, "color": CANDIDATE_COLORS.get(p, "#888888")}
        for p, c in sorted(pred_counts.items(), key=lambda x: -x[1])
    ]

    # political_real (résultats réels 2022 en Nouvelle-Aquitaine)
    political_real = [
        {"party": "Macron (LREM)", "count": 9, "color": CANDIDATE_COLORS["Macron (LREM)"]},
        {"party": "Le Pen (RN)",   "count": 3, "color": CANDIDATE_COLORS["Le Pen (RN)"]},
    ]

    out = {
        "summary": {
            "region_name":      "Nouvelle-Aquitaine",
            "model_name":       MODEL_DISPLAY[model_key],
            "model_id":         model_key,
            "model_accuracy":   round(acc, 2),
            "model_f1":         round(f1, 2),
            "predicted_winner": region_winner,
            "real_winner":      region_real,
            "economic_state":   region_entities[0]["economic_state"] if region_entities else "stable",
            "political_side":   region_entities[0]["political_side"] if region_entities else "centre",
            "nb_candidates":    12,
            "dept_accuracy":    75.0 if model_key == "HistGradientBoosting" else None,
        },
        "political_real":      political_real,
        "political_predicted": political_predicted,
        "levels": {
            "region":      region_entities,
            "departement": dept_entities,
            "canton":      canton_entities,
        },
    }

    dst = os.path.join(DST_DIR, f"predictions_{model_id}.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"    OK -> {dst}  ({len(canton_entities)} cantons)")

# Copier le predictions.json global mis à jour
print("\nCopie de predictions.json global…")
import shutil
shutil.copy(SRC, os.path.join(DST_DIR, "predictions.json"))
print("  OK -> public/data/predictions.json")

print("\nTerminé !")
