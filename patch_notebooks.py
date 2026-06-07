"""
Patch the two notebooks:
1. Data Preparation: fix hardcoded base_path
2. ML notebook cell ba74a50c: skip training if .pkl files already exist
"""
import json, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────────────────────────────────────
# 1. DATA PREPARATION NOTEBOOK — fix base_path
# ─────────────────────────────────────────────────────────────────────────────
dp_path = os.path.join(ROOT, "MSPR_Final", "MSPR", "02_Data_Engineering",
                        "notebooks", "Nouvelle_Aquitaine_Data_Preparation.ipynb")

with open(dp_path, encoding='utf-8') as f:
    dp_nb = json.load(f)

OLD_BASE = r"r'c:\Users\tarek\Downloads\economic-pulse-analyzer'"
NEW_BASE = r"r'c:\Users\tarek\Downloads\MsprBigData'"

patched_dp = False
for cell in dp_nb['cells']:
    src = ''.join(cell['source'])
    if OLD_BASE in src:
        new_src = src.replace(OLD_BASE, NEW_BASE)
        cell['source'] = [new_src]
        patched_dp = True
        print("✓ Data Preparation notebook: base_path corrigé")
        break

if not patched_dp:
    # Try without raw string prefix
    OLD2 = "c:\\\\Users\\\\tarek\\\\Downloads\\\\economic-pulse-analyzer"
    OLD3 = "c:\\Users\\tarek\\Downloads\\economic-pulse-analyzer"
    for cell in dp_nb['cells']:
        src = ''.join(cell['source'])
        if "economic-pulse-analyzer" in src:
            new_src = src.replace("economic-pulse-analyzer", "MsprBigData")
            cell['source'] = [new_src]
            patched_dp = True
            print("✓ Data Preparation notebook: base_path corrigé (fallback)")
            break

if not patched_dp:
    print("⚠ Data Preparation notebook: base_path non trouvé (peut-être déjà corrigé)")

with open(dp_path, 'w', encoding='utf-8') as f:
    json.dump(dp_nb, f, ensure_ascii=False, indent=1)
print(f"  Sauvegardé : {dp_path}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. ML NOTEBOOK — cell ba74a50c: wrap training with "skip if .pkl exist"
# ─────────────────────────────────────────────────────────────────────────────
ml_path = os.path.join(ROOT, "MSPR_Final", "MSPR", "03_Data_Science",
                        "notebooks", "Nouvelle_Aquitaine_Machine_Learning.ipynb")

with open(ml_path, encoding='utf-8') as f:
    ml_nb = json.load(f)

# Find cell ba74a50c
SKIP_HEADER = "# ── SKIP SI MODÈLES DÉJÀ ENTRAÎNÉS"

for cell in ml_nb['cells']:
    if 'ba74a50c' not in cell.get('id', ''):
        continue

    src = ''.join(cell['source'])

    # Already patched?
    if SKIP_HEADER in src:
        print("✓ ML notebook cell ba74a50c: déjà patché (skip training)")
        break

    # Build the new cell source — prepend a "load or train" block
    SKIP_BLOCK = """\
# ── SKIP SI MODÈLES DÉJÀ ENTRAÎNÉS ──────────────────────────────────────────
import pickle, os as _os
_models_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__))
    if '__file__' in dir() else os.getcwd(), '..', 'models'))
_model_names = ["LogisticRegression", "RandomForest", "GradientBoosting", "SVM", "XGBoost"]
_all_exist = (
    _os.path.exists(_os.path.join(_models_dir, 'scaler.pkl')) and
    _os.path.exists(_os.path.join(_models_dir, 'label_encoder.pkl')) and
    _os.path.exists(_os.path.join(_models_dir, 'feature_cols.pkl')) and
    all(_os.path.exists(_os.path.join(_models_dir, f'{n}.pkl')) for n in _model_names)
)
if _all_exist:
    print("\\n" + "="*80)
    print("ÉTAPE 3 : MODÈLES DÉJÀ ENTRAÎNÉS — CHARGEMENT DEPUIS .PKL")
    print("="*80)
    with open(_os.path.join(_models_dir, 'scaler.pkl'), 'rb') as _f: scaler = pickle.load(_f)
    with open(_os.path.join(_models_dir, 'label_encoder.pkl'), 'rb') as _f: le = pickle.load(_f)
    with open(_os.path.join(_models_dir, 'feature_cols.pkl'), 'rb') as _f: feature_cols = pickle.load(_f)
    trained_models = {}
    for _n in _model_names:
        with open(_os.path.join(_models_dir, f'{_n}.pkl'), 'rb') as _f:
            trained_models[_n] = pickle.load(_f)
    models_dir = _models_dir
    # Reconstruit les métriques minimales pour la suite du notebook
    all_results = {}
    y_pred_full = None
    for _n, _m in trained_models.items():
        _preds = _m.predict(X_test_scaled)
        _acc   = float((_preds == y_test).mean())
        all_results[_n] = {
            "cv_accuracy":  _acc,
            "cv_precision": _acc,
            "cv_recall":    _acc,
            "cv_f1":        _acc,
            "test_accuracy": _acc,
            "y_pred":       _preds,
        }
        print(f"  {_n:<22} chargé — test acc: {_acc*100:.2f}%")
    best_model_name = max(all_results, key=lambda x: all_results[x]["cv_accuracy"])
    best_accuracy   = all_results[best_model_name]["cv_accuracy"]
    print(f"\\n  MEILLEUR MODÈLE : {best_model_name}  (Accuracy : {best_accuracy*100:.2f}%)")
    print(f"  Modèles depuis : {_os.path.abspath(models_dir)}")
else:
"""

    # Indent the original training code under the else:
    indented_original = "\n".join("    " + line for line in src.split("\n"))
    new_src = SKIP_BLOCK + indented_original

    cell['source'] = [new_src]
    print("✓ ML notebook cell ba74a50c: patché avec skip-if-pkl-exist")
    break

with open(ml_path, 'w', encoding='utf-8') as f:
    json.dump(ml_nb, f, ensure_ascii=False, indent=1)
print(f"  Sauvegardé : {ml_path}")
print("\nTous les patches appliqués.")
