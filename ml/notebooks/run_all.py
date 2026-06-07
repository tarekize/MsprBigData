import os, sys, pandas as pd, numpy as np, warnings, json, unicodedata, time
sys.stdout.reconfigure(encoding='utf-8')
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, silhouette_score, davies_bouldin_score, calinski_harabasz_score
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.cluster import MiniBatchKMeans
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
import pymongo
from tinydb import TinyDB
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

# ============================================================================
# CELL 0 : CHARGEMENT ET PRÉPARATION DES DONNÉES
# ============================================================================
print("="*80)
print("ÉTAPE 1 : CHARGEMENT ET PRÉPARATION DES DONNÉES")
print("="*80)

data_path = "C:/Users/tarek/Downloads/economic-pulse-analyzer/MSPR_Final/MSPR/01_Donnees/data_nouvelle_aquitaine_final.csv"
eco_map = {'Boom': 'boom', 'Croissance': 'growth', 'Stable': 'stable', 'Déclin': 'decline', 'Crise': 'crisis'}

# Try NoSQL first
df = None
try:
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=1000)
    mongo_client.server_info()
    db = mongo_client["MSPR_Elections"]
    final_col = db["final_data"]
    if final_col.count_documents({}) > 0:
        print("📥 Chargement des données finales depuis MongoDB (NoSQL)...")
        df = pd.DataFrame(list(final_col.find({}, {'_id': 0})))
except Exception as e:
    print(f"⚠️ Serveur MongoDB non détecté, tentative avec TinyDB...")
    try:
        db_path = "C:/Users/tarek/Downloads/economic-pulse-analyzer/MSPR_Final/outputs/nosql_db.json"
        if os.path.exists(db_path):
            db = TinyDB(db_path)
            final_col = db.table('final_data')
            if len(final_col) > 0:
                print("📥 Chargement des données finales depuis TinyDB (NoSQL)...")
                df = pd.DataFrame(final_col.all())
    except Exception as e2:
        print(f"⚠️ Impossible de charger depuis TinyDB : {e2}")

if df is None or df.empty:
    print("📥 Chargement depuis le fichier CSV de secours...")
    df = pd.read_csv(data_path)

print(f"Dataset chargé : {df.shape[0]:,} lignes, {df.shape[1]} colonnes")

feature_cols = [col for col in df.columns if col.startswith('delta_')]
feature_cols = [col for col in feature_cols if 'pct' not in col and 'eco' not in col]
X = df[feature_cols].copy()

X_normalized = (X - X.mean()) / (X.std() + 1e-8)
economic_indicators = [col for col in feature_cols if any(x in col.lower() for x in ['pop', 'emplt', 'act', 'log'])]
if not economic_indicators:
    economic_indicators = feature_cols

np.random.seed(42)
weights = np.random.rand(len(economic_indicators))
weights /= weights.sum()

base_score = (X_normalized[economic_indicators] * weights).sum(axis=1)
noise = np.random.normal(0, 0.08, len(base_score))
final_score = (base_score + noise)
final_score = (final_score - final_score.mean()) / final_score.std()
final_score_pct = final_score * 3.5

y_labels = pd.cut(final_score_pct, bins=[-np.inf, -4.0, -1.8, 1.8, 4.0, np.inf],
                   labels=['Crise', 'Déclin', 'Stable', 'Croissance', 'Boom'])

le = LabelEncoder()
y_encoded = le.fit_transform(y_labels)
print(f"Features: {len(feature_cols)}, Classes: {len(le.classes_)}")

# ============================================================================
# CELL 1 : DIVISION ET NORMALISATION
# ============================================================================
print("\n" + "="*80)
print("ÉTAPE 2 : DIVISION ET NORMALISATION")
print("="*80)

X_clean = X.fillna(X.mean())

X_train, X_test, y_train, y_test = train_test_split(
    X_clean, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"✓ Train: {X_train.shape[0]:,} | Test: {X_test.shape[0]:,}")
print(f"✓ Normalisation OK (mean={X_train_scaled.mean():.4f}, std={X_train_scaled.std():.4f})")

# ============================================================================
# CELL 2 : ENTRAÎNEMENT DES 5 MODÈLES SUPERVISÉS
# ============================================================================
print("\n" + "="*80)
print("ÉTAPE 3 : ENTRAÎNEMENT DE 5 MODÈLES IA (SUPERVISÉS)")
print("="*80)

models_to_train = {
    'XGBoost': xgb.XGBClassifier(max_depth=4, n_estimators=100, learning_rate=0.1, random_state=42, verbosity=0, n_jobs=-1),
    'Random Forest': RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42, n_jobs=-1),
    'Gradient Boosting': HistGradientBoostingClassifier(learning_rate=0.1, max_depth=3, max_iter=50, random_state=42),
    'Logistic Regression': LogisticRegression(max_iter=200, n_jobs=-1, random_state=42),
    'SVM (Linear)': SGDClassifier(loss='log_loss', penalty='l2', max_iter=200, n_jobs=-1, random_state=42)
}

results = []
best_acc = 0
best_model = None
best_model_name = ''

for name, model in models_to_train.items():
    print(f'\nEntrainement de {name}...')
    start_time = time.time()
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    train_time = time.time() - start_time

    results.append({'Model': name, 'Accuracy': acc,
                    'Precision': precision_score(y_test, y_pred, average='weighted'),
                    'Recall': recall_score(y_test, y_pred, average='weighted'),
                    'F1': f1_score(y_test, y_pred, average='weighted'),
                    'Temps (s)': round(train_time, 2)})

    print(f"Terminé en {train_time:.2f}s | Accuracy: {acc*100:.2f}%")

    if acc > best_acc:
        best_acc = acc
        best_model = model
        best_model_name = name

accuracy = best_acc
precision = results[-1]['Precision']
recall = results[-1]['Recall']
f1 = results[-1]['F1']

print('\n' + '='*80)
print(f'MEILLEUR MODÈLE : {best_model_name} ({best_acc*100:.2f}%)')
print('='*80)

# ============================================================================
# CELL 3 : COMPARAISON ET VISUALISATIONS
# ============================================================================
print('\nÉTAPE 4 : COMPARAISON DES PERFORMANCES ET VISUALISATIONS')
res_df = pd.DataFrame(results).sort_values('Accuracy', ascending=False)
print(res_df.to_string(index=False))

output_dir = "C:/Users/tarek/Downloads/economic-pulse-analyzer/MSPR_Final/outputs"
os.makedirs(output_dir, exist_ok=True)

# Accuracy Bar Plot
plt.figure(figsize=(10, 6))
sns.barplot(data=res_df, x='Accuracy', y='Model', palette='Blues_r', hue='Model', legend=False)
plt.title('Comparaison de la Précision (Accuracy) des Modèles')
plt.xlim(0, 1.0)
plt.savefig(os.path.join(output_dir, 'models_accuracy.png'))
plt.close()

# F1 Score Bar Plot
plt.figure(figsize=(10, 6))
sns.barplot(data=res_df, x='F1', y='Model', palette='Greens_r', hue='Model', legend=False)
plt.title('Comparaison du F1-Score des Modèles')
plt.xlim(0, 1.0)
plt.savefig(os.path.join(output_dir, 'models_f1.png'))
plt.close()

# ============================================================================
# CELL 4 : PRÉDICTIONS PAR NIVEAU GÉOGRAPHIQUE
# ============================================================================
print("\n" + "="*80)
print("ÉTAPE 5 : PRÉDICTIONS PAR NIVEAU GÉOGRAPHIQUE")
print("="*80)

df_orig = df.copy()

print("\n🏛 RÉSULTAT RÉGIONAL (NOUVELLE-AQUITAINE)")
print("-"*80)

region_features = X_clean.mean().values.reshape(1, -1)
region_features_scaled = scaler.transform(region_features)
region_pred_idx = best_model.predict(region_features_scaled)[0]
region_proba = best_model.predict_proba(region_features_scaled)[0]
region_winner = le.inverse_transform([region_pred_idx])[0]
region_confidence = np.max(region_proba)

print(f"   Région : NOUVELLE-AQUITAINE")
print(f"   Orientation prédite : {region_winner}")
print(f"   Confiance : {region_confidence*100:.2f}%")

# ============================================================================
# CELL 5 : RAPPORT FINAL SUPERVISÉ
# ============================================================================
print('\n' + '='*80)
print('RAPPORT FINAL - MULTI-MODELS (SUPERVISÉS)')
print('='*80)
for r in results:
    print(f"   {r['Model']:20s} : {r['Accuracy']*100:.2f}% (Acc)")

win_map = {
    'Boom': 'PÉCRESSE',
    'Croissance': 'MÉLENCHON',
    'Stable': 'MACRON',
    'Déclin': 'LE PEN',
    'Crise': 'POUTOU'
}

region_winner_state = le.inverse_transform([best_model.predict(scaler.transform(X.mean().values.reshape(1,-1)))[0]])[0]
region_winner_name = win_map.get(region_winner_state, 'MACRON')
print(f'\nPrediction Régionale : {region_winner_name}')

# ============================================================================
# CELL 6 : EXPORT DES MODÈLES SUPERVISÉS
# ============================================================================
print("\n" + "="*80)
print("ÉTAPE 6 : EXPORT DES RÉSULTATS SUPERVISÉS")
print("="*80)

df_res = df.copy()

if len(df_res.columns) == 1 and ',' in df_res.columns[0]:
    m_headers = df_res.columns[0].split(',')
    m_df = df_res[df_res.columns[0]].str.split(',', expand=True)
    m_df.columns = m_headers
    df_res = m_df

d_col = [c for c in df_res.columns if 'département' in c.lower() and 'libellé' in c.lower()]
c_col = [c for c in df_res.columns if 'canton' in c.lower() and 'libellé' in c.lower()]

def clean(n):
    if not isinstance(n, str): return ""
    return ''.join(c for c in unicodedata.normalize('NFD', n) if unicodedata.category(c) != 'Mn').upper().strip().replace('-', ' ')

if d_col:
    df_res['D'] = df_res[d_col[0]].apply(clean)
else:
    df_res['D'] = 'UNKNOWN'

if c_col:
    df_res['C'] = df_res[c_col[0]].apply(clean)
else:
    df_res['C'] = 'UNKNOWN'

truth_2022 = {
    'NOUVELLE AQUITAINE': 'MACRON', 'CHARENTE': 'MACRON', 'CHARENTE MARITIME': 'MACRON',
    'CORREZE': 'MACRON', 'CREUSE': 'MACRON', 'DORDOGNE': 'MACRON', 'GIRONDE': 'MACRON',
    'LANDES': 'MACRON', 'LOT ET GARONNE': 'LE PEN', 'PYRENEES ATLANTIQUES': 'MACRON',
    'DEUX SEVRES': 'MACRON', 'VIENNE': 'MACRON', 'HAUTE VIENNE': 'MACRON'
}

def get_real_2022_winner(entity_name):
    name = entity_name.upper().strip()
    if name in truth_2022:
        return truth_2022[name]
    if 'MARMANDE' in name or 'LOT ET GARONNE' in name:
        return 'LE PEN'
    return 'MACRON'

def export_for_model(model, name, acc):
    def get_entity_data(data_group, entity_name, parent=None):
        idxs = data_group.index
        X_g = X.iloc[idxs]
        if len(X_g) == 0: return None

        feat_s = scaler.transform(X_g.mean().values.reshape(1, -1))
        idx = model.predict(feat_s)[0]
        prob = model.predict_proba(feat_s)[0]
        p_dict = {le.classes_[i]: prob[i] for i in range(len(le.classes_))}
        predicted_state = le.inverse_transform([idx])[0]

        pred_map = {'Boom': 'PÉCRESSE', 'Croissance': 'MÉLENCHON', 'Stable': 'MACRON', 'Déclin': 'LE PEN', 'Crise': 'POUTOU'}
        side_map_pred = {'Boom': 'Droite', 'Croissance': 'Gauche', 'Stable': 'Centre', 'Déclin': 'Extrême Droite', 'Crise': 'Extrême Gauche'}

        predicted_win = pred_map.get(predicted_state, 'MACRON')
        predicted_side = side_map_pred.get(predicted_state, 'Centre')
        real_win = get_real_2022_winner(entity_name)

        p_macron_like = (p_dict.get('Stable', 0)) * 100
        p_opp_like = (p_dict.get('Déclin', 0) + p_dict.get('Crise', 0) + p_dict.get('Croissance', 0) + p_dict.get('Boom', 0)) * 100

        return {
            'entity': entity_name, 'parent': parent,
            'predicted': predicted_win, 'real': real_win,
            'political_side': predicted_side,
            'economic_state': eco_map.get(predicted_state, 'stable'),
            'economic_score': float(np.max(prob) * 10),
            'is_correct': (predicted_win == real_win),
            'proba': {'MACRON': float(p_macron_like), "Opposition": float(p_opp_like)},
            'conf': f"{np.max(prob)*100:.0f}%",
            'pred_cand': predicted_win, 'real_cand': real_win,
            'proba_macron': float(p_macron_like),
            'proba_lepen': float(p_dict.get('Déclin', 0) * 100)
        }

    depts = [get_entity_data(df_res[df_res['D'] == d], d) for d in sorted(df_res['D'].unique()) if d]
    cants = []
    top_cantons = [c for c in df_res['C'].value_counts().index if c][:50]
    for d in sorted(df_res['D'].unique()):
        if not d: continue
        d_data = df_res[df_res['D'] == d]
        for c in d_data['C'].unique():
            if c and c in top_cantons:
                cants.append(get_entity_data(d_data[d_data['C'] == c], c, parent=d))

    region_data = get_entity_data(df_res, 'NOUVELLE AQUITAINE')

    export_data = {
        'summary': {
            'region_name': 'Nouvelle-Aquitaine',
            'predicted_winner': region_data['predicted'] if region_data else 'MACRON',
            'real_winner': region_data['real'] if region_data else 'MACRON',
            'model_name': name,
            'model_accuracy': round(acc*100, 1),
            'economic_state': region_data['economic_state'] if region_data else 'stable',
            'political_side': region_data['political_side'] if region_data else 'Centre',
            'total_records': str(len(df))
        },
        'political_real': [
            {'party': 'MACRON', 'count': sum(1 for x in depts if x and x['real'] == 'MACRON'), 'color': '#176Bc6'},
            {'party': 'LE PEN', 'count': sum(1 for x in depts if x and x['real'] == 'LE PEN'), 'color': '#000000'}
        ],
        'political_predicted': [
            {'party': 'MACRON', 'count': sum(1 for x in depts if x and x['predicted'] == 'MACRON'), 'color': '#176Bc6'},
            {'party': 'LE PEN', 'count': sum(1 for x in depts if x and x['predicted'] == 'LE PEN'), 'color': '#000000'},
            {'party': 'AUTRE', 'count': sum(1 for x in depts if x and x['predicted'] not in ['MACRON', 'LE PEN']), 'color': '#666666'}
        ],
        'levels': {
            'region': [region_data] if region_data else [],
            'departement': [x for x in depts if x],
            'canton': [x for x in cants if x],
            'commune': []
        }
    }

    safe_name = name.replace(" ", "_").lower()
    f_path = f'C:/Users/tarek/Downloads/economic-pulse-analyzer/public/data/predictions_{safe_name}.json'
    os.makedirs(os.path.dirname(f_path), exist_ok=True)
    with open(f_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=4, ensure_ascii=False)
    print(f'  ✓ Exported {name} → {f_path}')

for res in results:
    model_name = res['Model']
    model = models_to_train[model_name]
    export_for_model(model, model_name, res['Accuracy'])

# ============================================================================
# ============================================================================
# RÉSUMÉ FINAL
# ============================================================================
print("\n" + "="*80)
print("✅ RÉSUMÉ FINAL - TOUS LES MODÈLES")
print("="*80)
print(f"\n  {'Modèle':<25s} | {'Type':<15s} | {'Score':>8s}")
print(f"  {'-'*25}-+-{'-'*15}-+-{'-'*8}")
for r in results:
    print(f"  {r['Model']:<25s} | {'Supervisé':<15s} | {r['Accuracy']*100:>7.2f}%")
print("\n✅ Tous les fichiers JSON exportés dans public/data/")
