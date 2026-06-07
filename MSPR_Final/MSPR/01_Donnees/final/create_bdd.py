import pandas as pd
import numpy as np
import os
import pickle
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Chemins relatifs portables
input_path  = os.path.normpath(os.path.join(_SCRIPT_DIR, '..', 'data_nouvelle_aquitaine_final.csv'))
output_path = os.path.normpath(os.path.join(_SCRIPT_DIR, 'data_nouvelle_aquitaine_final_2022.csv'))
models_dir  = os.path.normpath(os.path.join(_SCRIPT_DIR, '..', '..', '03_Data_Science', 'models'))

print("=" * 70)
print("PRÉDICTION ML — create_bdd.py")
print("=" * 70)

# ── Chargement du dataset ─────────────────────────────────────────────────────
if not os.path.exists(input_path):
    alt_paths = [
        os.path.join(_SCRIPT_DIR, 'data_nouvelle_aquitaine_final.csv'),
        r'C:/Users/tarek/Downloads/aliMSPR/MSPR_Final/MSPR/01_Donnees/data_nouvelle_aquitaine_final.csv',
    ]
    for alt in alt_paths:
        if os.path.exists(alt):
            input_path = alt
            break
    else:
        print(f"Fichier introuvable : {input_path}")
        sys.exit(1)

print(f"Chargement : {input_path}")
df = pd.read_csv(input_path)
print(f"Dataset : {df.shape[0]:,} lignes × {df.shape[1]} colonnes")

feature_cols = [col for col in df.columns if col.startswith('delta_')]
if not feature_cols:
    print("Aucune colonne delta_ trouvée — arrêt.")
    sys.exit(1)

print(f"Features delta : {len(feature_cols)}")
X = df[feature_cols].fillna(0)

# ── Chargement des modèles ML entraînés ──────────────────────────────────────
MODEL_NAMES = ['XGBoost', 'RandomForest', 'GradientBoosting', 'LogisticRegression', 'SVM']
loaded_models  = {}
scaler         = None
le             = None
saved_features = None

print(f"\nChargement des modèles depuis : {models_dir}")

if os.path.exists(models_dir):
    for filename, varname in [('scaler.pkl', 'scaler'), ('label_encoder.pkl', 'le'), ('feature_cols.pkl', 'saved_features')]:
        path = os.path.join(models_dir, filename)
        if os.path.exists(path):
            with open(path, 'rb') as fp:
                obj = pickle.load(fp)
            if varname == 'scaler':
                scaler = obj
            elif varname == 'le':
                le = obj
            else:
                saved_features = obj
            print(f"  {filename} chargé")
        else:
            print(f"  {filename} introuvable")

    for name in MODEL_NAMES:
        pkl_path = os.path.join(models_dir, f'{name}.pkl')
        if os.path.exists(pkl_path):
            with open(pkl_path, 'rb') as fp:
                loaded_models[name] = pickle.load(fp)
            print(f"  {name}.pkl chargé")
        else:
            print(f"  {name}.pkl introuvable — ignoré")
else:
    print(f"  Dossier models introuvable : {models_dir}")
    print("  Lance d'abord le notebook ML pour entraîner et sauvegarder les modèles.")

# ── Prédiction via modèles ML ─────────────────────────────────────────────────
WINNER_MAP = {"Croissance": "MACRON", "Stable": "MACRON", "Declin": "LE PEN"}

if loaded_models and scaler is not None and le is not None:
    print(f"\nPrédiction ML avec {len(loaded_models)} modèle(s) : {list(loaded_models.keys())}")

    # Aligner les features avec celles utilisées à l'entraînement
    if saved_features is not None:
        for f in saved_features:
            if f not in X.columns:
                X[f] = 0
        X_aligned = X[saved_features]
        missing = [f for f in saved_features if f not in df[feature_cols].columns]
        if missing:
            print(f"  Features manquantes (remplies à 0) : {missing}")
    else:
        X_aligned = X[feature_cols]

    X_scaled = scaler.transform(X_aligned)
    classes_list = list(le.classes_)

    # Appliquer chaque modèle sur toutes les lignes
    for name, model in loaded_models.items():
        preds_idx   = model.predict(X_scaled)
        preds_proba = model.predict_proba(X_scaled)
        eco_classes = le.inverse_transform(preds_idx)
        candidates  = [WINNER_MAP.get(c, 'MACRON') for c in eco_classes]

        croissance_i = classes_list.index('Croissance') if 'Croissance' in classes_list else None
        stable_i     = classes_list.index('Stable')     if 'Stable'     in classes_list else None
        declin_i     = classes_list.index('Declin')     if 'Declin'     in classes_list else None

        prob_macron = np.zeros(len(df))
        prob_lepen  = np.zeros(len(df))
        if croissance_i is not None:
            prob_macron += preds_proba[:, croissance_i]
        if stable_i is not None:
            prob_macron += preds_proba[:, stable_i]
        if declin_i is not None:
            prob_lepen  += preds_proba[:, declin_i]

        col = name.lower().replace(' ', '_')
        df[f'{col}_eco_class']    = eco_classes
        df[f'{col}_candidat']     = candidates
        df[f'{col}_proba_macron'] = np.round(prob_macron * 100, 2)
        df[f'{col}_proba_lepen']  = np.round(prob_lepen  * 100, 2)

    # Vote majoritaire entre tous les modèles → prédiction finale
    cand_cols = [f"{n.lower().replace(' ', '_')}_candidat" for n in loaded_models]
    df['vainqueur_nom_predit'] = df[cand_cols].mode(axis=1)[0]

    # État économique du meilleur modèle disponible (XGBoost en priorité)
    best_col = next(
        (f'{n.lower()}_eco_class' for n in ['XGBoost', 'GradientBoosting', 'RandomForest'] if f'{n.lower()}_eco_class' in df.columns),
        f"{list(loaded_models.keys())[0].lower()}_eco_class"
    )
    df['etat_economique']     = df[best_col]
    df['orientation_predite'] = df['vainqueur_nom_predit'].map({'MACRON': 'Centre', 'LE PEN': 'exD'})

    print(f"\n  Prédictions appliquées sur {len(df):,} lignes")
    print(f"\n  Distribution vainqueur prédit (vote majoritaire) :")
    for val, cnt in df['vainqueur_nom_predit'].value_counts().items():
        print(f"    {val:<15} : {cnt:>8,} ({cnt / len(df) * 100:.1f}%)")

    print(f"\n  Détail par modèle :")
    for name in loaded_models:
        col = f"{name.lower().replace(' ', '_')}_candidat"
        dist = df[col].value_counts()
        macron_pct = dist.get('MACRON', 0) / len(df) * 100
        lepen_pct  = dist.get('LE PEN', 0) / len(df) * 100
        print(f"    {name:<22} -> MACRON:{macron_pct:.1f}%  LE PEN:{lepen_pct:.1f}%")

else:
    # ── Fallback formule économique si aucun modèle disponible ───────────────
    print("\nAucun modèle ML chargé — fallback formule économique")
    print("  Pour activer la prédiction ML : exécuter le notebook Nouvelle_Aquitaine_Machine_Learning.ipynb")

    eco_cols = [c for c in feature_cols if any(x in c.lower() for x in ['pop', 'emplt', 'act', 'rev', 'chom'])] or feature_cols

    def compute_delta_eco(row):
        score, n = 0, 0
        for c in eco_cols:
            v = row[c]
            if pd.isna(v):
                continue
            score += -v if 'chom' in c.lower() else v
            n += 1
        return score / n if n else 0

    df['score_eco_raw'] = df.apply(compute_delta_eco, axis=1)
    mean_val = df['score_eco_raw'].mean()
    std_val  = df['score_eco_raw'].std() or 1
    df['delta_eco_pct'] = (df['score_eco_raw'] - mean_val) / std_val * 3.5

    conditions = [
        df['delta_eco_pct'] > 5,
        (df['delta_eco_pct'] >= 1)  & (df['delta_eco_pct'] <= 5),
        (df['delta_eco_pct'] >= -1) & (df['delta_eco_pct'] < 1),
        (df['delta_eco_pct'] >= -5) & (df['delta_eco_pct'] < -1),
        df['delta_eco_pct'] < -5,
    ]
    states = ['Boom', 'Croissance', 'Stable', 'Déclin', 'Crise']
    df['etat_economique'] = np.select(conditions, states, default='Stable')

    state_to_block = {'Boom': 'Centre', 'Croissance': 'D', 'Stable': 'G', 'Déclin': 'exD', 'Crise': 'exG'}
    cand_map       = {'Centre': 'MACRON', 'D': 'MACRON', 'G': 'MELENCHON', 'exD': 'LE PEN', 'exG': 'LE PEN'}
    df['orientation_predite']  = df['etat_economique'].map(state_to_block)
    df['vainqueur_nom_predit'] = df['orientation_predite'].map(cand_map)
    print(f"  Fallback appliqué sur {len(df):,} lignes")

# ── Export ────────────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False)
print(f"\nExporté : {output_path}")
print(f"Colonnes : {df.shape[1]}  |  Lignes : {df.shape[0]:,}")
print("Done.")
