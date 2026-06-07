"""Fix the training cell in ML notebook: skip re-training if .pkl files already exist."""
import json, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.abspath(__file__))
nb_path = os.path.join(ROOT, "MSPR_Final", "MSPR", "03_Data_Science",
                        "notebooks", "Nouvelle_Aquitaine_Machine_Learning.ipynb")
models_dir_abs = os.path.join(ROOT, "MSPR_Final", "MSPR", "03_Data_Science", "models")
# Use forward slashes for the hardcoded fallback path in the notebook code
models_dir_fwd = models_dir_abs.replace("\\", "/")

with open(nb_path, encoding='utf-8') as f:
    nb = json.load(f)

NEW_SKIP = (
    "# ── SKIP SI MODÈLES DÉJÀ ENTRAÎNÉS ─────────────────────────────────────────\n"
    "import pickle, os\n"
    "_models_dir = r'" + models_dir_abs + "'\n"
    "_model_names = ['LogisticRegression', 'RandomForest', 'GradientBoosting', 'SVM', 'XGBoost']\n"
    "_all_exist = (\n"
    "    os.path.exists(os.path.join(_models_dir, 'scaler.pkl')) and\n"
    "    os.path.exists(os.path.join(_models_dir, 'label_encoder.pkl')) and\n"
    "    os.path.exists(os.path.join(_models_dir, 'feature_cols.pkl')) and\n"
    "    all(os.path.exists(os.path.join(_models_dir, f'{n}.pkl')) for n in _model_names)\n"
    ")\n"
    "if _all_exist:\n"
    "    print('\\n' + '='*80)\n"
    "    print('ÉTAPE 3 : MODÈLES DÉJÀ ENTRAÎNÉS — CHARGEMENT DEPUIS .PKL')\n"
    "    print('='*80)\n"
    "    with open(os.path.join(_models_dir, 'scaler.pkl'), 'rb') as _f: scaler = pickle.load(_f)\n"
    "    with open(os.path.join(_models_dir, 'label_encoder.pkl'), 'rb') as _f: le = pickle.load(_f)\n"
    "    with open(os.path.join(_models_dir, 'feature_cols.pkl'), 'rb') as _f: feature_cols = pickle.load(_f)\n"
    "    trained_models = {}\n"
    "    for _n in _model_names:\n"
    "        with open(os.path.join(_models_dir, f'{_n}.pkl'), 'rb') as _f:\n"
    "            trained_models[_n] = pickle.load(_f)\n"
    "    models_dir = _models_dir\n"
    "    from sklearn.metrics import precision_score, recall_score, f1_score\n"
    "    all_results = {}\n"
    "    for _n, _m in trained_models.items():\n"
    "        _preds = _m.predict(X_test_scaled)\n"
    "        _acc   = float((_preds == y_test).mean())\n"
    "        _prec  = float(precision_score(y_test, _preds, average='weighted', zero_division=0))\n"
    "        _rec   = float(recall_score(y_test, _preds, average='weighted', zero_division=0))\n"
    "        _f1    = float(f1_score(y_test, _preds, average='weighted', zero_division=0))\n"
    "        all_results[_n] = {\n"
    "            'cv_accuracy': _acc, 'cv_std': 0.0, 'cv_precision': _prec, 'cv_recall': _rec, 'cv_f1': _f1,\n"
    "            'test_accuracy': _acc, 'test_precision': _prec, 'test_recall': _rec, 'test_f1': _f1,\n"
    "            'y_pred': _preds,\n"
    "        }\n"
    "        print(f'  {_n:<22} chargé — acc:{_acc*100:.1f}%  f1:{_f1*100:.1f}%')\n"
    "    best_model_name = max(all_results, key=lambda x: all_results[x]['cv_accuracy'])\n"
    "    best_accuracy   = all_results[best_model_name]['cv_accuracy']\n"
    "    best_model      = trained_models[best_model_name]\n"
    "    accuracy        = best_accuracy\n"
    "    precision       = all_results[best_model_name]['test_precision']\n"
    "    recall          = all_results[best_model_name]['test_recall']\n"
    "    f1              = all_results[best_model_name]['test_f1']\n"
    "    y_pred_best     = all_results[best_model_name]['y_pred']\n"
    "    models_config   = {n: m for n, m in trained_models.items()}\n"
    "    skf             = None\n"
    "    _data_dir       = os.path.normpath(os.path.join(os.getcwd(), '..', '..'))\n"
    "    print(f'\\n  MEILLEUR MODÈLE : {best_model_name}  ({best_accuracy*100:.2f}%)')\n"
    "    print(f'  Modèles depuis : {_models_dir}')\n"
    "else:\n"
)

for cell in nb['cells']:
    if 'ba74a50c' not in cell.get('id', ''):
        continue
    src = ''.join(cell['source'])

    # Remove previous patch if any
    if "# ── SKIP SI MODÈLES DÉJÀ ENTRAÎNÉS" in src:
        # Find where the old SKIP block starts
        skip_start = src.find("# ── SKIP SI MODÈLES DÉJÀ ENTRAÎNÉS")
        # Find where the actual original cell starts (under the else: block)
        # It's indented by 4 spaces — un-indent it
        after_else = src.find("\nelse:\n", skip_start)
        if after_else != -1:
            original_indented = src[after_else + len("\nelse:\n"):]
            # Remove 4-space indentation
            original_lines = original_indented.split("\n")
            original = "\n".join(
                line[4:] if line.startswith("    ") else line
                for line in original_lines
            )
        else:
            print("ERROR: could not find 'else:' in existing patch")
            break
    else:
        original = src

    # Indent original under the else:
    indented = "\n".join("    " + line for line in original.split("\n"))
    new_src = NEW_SKIP + indented
    cell['source'] = [new_src]
    print("✓ ML notebook cell ba74a50c: skip-if-pkl patché")
    break

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print(f"Sauvegardé : {nb_path}")
