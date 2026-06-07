"""
nosql_mongodb_setup.py
======================
Script de mise en place de la base NoSQL MongoDB — MSPR Electio-Analytics
Région Nouvelle-Aquitaine · Prédiction des tendances électorales

Base de données : MSPR_Elections
Collections :
  1. raw_data           — Données électorales brutes (2012, 2017)
  2. indicators         — Indicateurs socio-économiques (population, emploi, sécurité, revenus)
  3. final_data         — Données fusionnées et enrichies (ETL output)
  4. models_metrics     — Métriques des modèles ML entraînés
  5. predictions        — Prédictions géographiques (région / département / canton)

Exécution :
    python nosql_mongodb_setup.py
    python nosql_mongodb_setup.py --drop   # recrée tout depuis zéro
    python nosql_mongodb_setup.py --import # importe les données depuis les CSV/JSON existants
"""

import os
import sys
import json
import argparse
from datetime import datetime

# ── Try MongoDB; fallback to TinyDB ───────────────────────────────────────────
try:
    import pymongo
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    print('⚠️  pymongo non installé — utilisation de TinyDB (NoSQL local)')

try:
    from tinydb import TinyDB, Query
    TINYDB_AVAILABLE = True
except ImportError:
    TINYDB_AVAILABLE = False

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
TINYDB_PATH = os.path.join(ROOT, 'MSPR_Final', 'outputs', 'nosql_db.json')
PRED_PATH   = os.path.join(ROOT, 'public', 'data', 'predictions.json')

# ══════════════════════════════════════════════════════════════════════════════
#  MCD — MODÈLE CONCEPTUEL DE DONNÉES (NoSQL)
# ══════════════════════════════════════════════════════════════════════════════
#
#  ┌─────────────────────────────────────────────────────────────────────────┐
#  │                     BASE DE DONNÉES : MSPR_Elections                   │
#  ├────────────────┬────────────────────────────────────────────────────────┤
#  │  COLLECTION    │  STRUCTURE (document JSON)                            │
#  ├────────────────┼────────────────────────────────────────────────────────┤
#  │  raw_data      │  _id, annee, tour, code_dept, nom_dept, code_commune, │
#  │                │  nom_commune, inscrits, votants, abstentions,         │
#  │                │  exprimes, candidats: [{nom, voix, pct_voix}]        │
#  ├────────────────┼────────────────────────────────────────────────────────┤
#  │  indicators    │  _id, code_commune, nom_commune, code_dept, annee,   │
#  │                │  population, taux_emploi, taux_chomage,              │
#  │                │  taux_activite, revenus_median, nb_entreprises,      │
#  │                │  taux_delinquance, taux_pauvrete, vie_associative    │
#  ├────────────────┼────────────────────────────────────────────────────────┤
#  │  final_data    │  _id, code_commune, annee_ref, delta_features: {},   │
#  │                │  delta_eco_pct, etat_economique, orientation_predite,│
#  │                │  vainqueur_nom_predit, score_eco_raw                 │
#  ├────────────────┼────────────────────────────────────────────────────────┤
#  │  models_metrics│  _id, model_name, trained_at, accuracy, precision,  │
#  │                │  recall, f1_score, n_samples_train, n_samples_test,  │
#  │                │  hyperparams: {}, feature_importances: {}            │
#  ├────────────────┼────────────────────────────────────────────────────────┤
#  │  predictions   │  _id, model_name, generated_at, niveau,             │
#  │                │  entite, code_dept, predicted_winner,                │
#  │                │  real_winner, political_side, economic_state,        │
#  │                │  economic_score, is_correct, proba: {}               │
#  └────────────────┴────────────────────────────────────────────────────────┘
#
#  Relations (référence par champ, NoSQL):
#    final_data.code_commune  → raw_data.code_commune
#    final_data.code_commune  → indicators.code_commune
#    predictions.model_name   → models_metrics.model_name
#
# ══════════════════════════════════════════════════════════════════════════════

# MongoDB JSONSchema validators
VALIDATORS = {
    'raw_data': {
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['annee', 'tour', 'code_dept', 'nom_dept'],
            'properties': {
                'annee':       {'bsonType': 'int',    'description': 'Année du scrutin (2012 ou 2017)'},
                'tour':        {'bsonType': 'int',    'enum': [1, 2], 'description': 'Tour (1 ou 2)'},
                'code_dept':   {'bsonType': 'string', 'description': 'Code INSEE du département'},
                'nom_dept':    {'bsonType': 'string', 'description': 'Nom du département'},
                'code_commune':{'bsonType': 'string'},
                'nom_commune': {'bsonType': 'string'},
                'inscrits':    {'bsonType': ['int', 'double', 'null']},
                'votants':     {'bsonType': ['int', 'double', 'null']},
                'abstentions': {'bsonType': ['int', 'double', 'null']},
                'exprimes':    {'bsonType': ['int', 'double', 'null']},
                'candidats': {
                    'bsonType': 'array',
                    'items': {
                        'bsonType': 'object',
                        'properties': {
                            'nom':       {'bsonType': 'string'},
                            'voix':      {'bsonType': ['int', 'double']},
                            'pct_voix':  {'bsonType': ['double', 'null']},
                        }
                    }
                }
            }
        }
    },
    'indicators': {
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['code_commune', 'annee'],
            'properties': {
                'code_commune':    {'bsonType': 'string'},
                'nom_commune':     {'bsonType': 'string'},
                'code_dept':       {'bsonType': 'string'},
                'nom_dept':        {'bsonType': 'string'},
                'annee':           {'bsonType': 'int'},
                'population':      {'bsonType': ['double', 'int', 'null']},
                'taux_emploi':     {'bsonType': ['double', 'null']},
                'taux_chomage':    {'bsonType': ['double', 'null']},
                'taux_activite':   {'bsonType': ['double', 'null']},
                'revenus_median':  {'bsonType': ['double', 'int', 'null']},
                'nb_entreprises':  {'bsonType': ['int', 'null']},
                'taux_delinquance':{'bsonType': ['double', 'null']},
                'taux_pauvrete':   {'bsonType': ['double', 'null']},
                'vie_associative': {'bsonType': ['int', 'null']},
            }
        }
    },
    'final_data': {
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['code_commune', 'etat_economique'],
            'properties': {
                'code_commune':       {'bsonType': 'string'},
                'annee_ref':          {'bsonType': ['int', 'null']},
                'delta_eco_pct':      {'bsonType': ['double', 'null']},
                'etat_economique':    {'bsonType': 'string',
                                      'enum': ['Boom', 'Croissance', 'Stable', 'Déclin', 'Crise']},
                'orientation_predite':{'bsonType': 'string',
                                      'enum': ['Centre', 'D', 'G', 'exD', 'exG']},
                'vainqueur_nom_predit':{'bsonType': 'string'},
                'score_eco_raw':       {'bsonType': ['double', 'null']},
            }
        }
    },
    'models_metrics': {
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['model_name', 'accuracy'],
            'properties': {
                'model_name':     {'bsonType': 'string'},
                'trained_at':     {'bsonType': 'string'},
                'accuracy':       {'bsonType': 'double', 'minimum': 0, 'maximum': 100},
                'precision':      {'bsonType': ['double', 'null']},
                'recall':         {'bsonType': ['double', 'null']},
                'f1_score':       {'bsonType': ['double', 'null']},
                'n_samples_train':{'bsonType': ['int', 'null']},
                'n_samples_test': {'bsonType': ['int', 'null']},
            }
        }
    },
    'predictions': {
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['model_name', 'niveau', 'entite'],
            'properties': {
                'model_name':      {'bsonType': 'string'},
                'generated_at':    {'bsonType': 'string'},
                'niveau':          {'bsonType': 'string', 'enum': ['region', 'departement', 'canton']},
                'entite':          {'bsonType': 'string'},
                'predicted_winner':{'bsonType': 'string'},
                'real_winner':     {'bsonType': ['string', 'null']},
                'political_side':  {'bsonType': 'string'},
                'economic_state':  {'bsonType': 'string'},
                'economic_score':  {'bsonType': ['double', 'null']},
                'is_correct':      {'bsonType': ['bool', 'null']},
                'proba':           {'bsonType': 'object'},
            }
        }
    },
}

# Seed data — model metrics
SEED_MODELS = [
    {
        'model_name': 'Logistic Regression',
        'trained_at': '2025-01-15T10:00:00',
        'accuracy': 81.81,
        'precision': 81.79,
        'recall': 81.81,
        'f1_score': 81.77,
        'n_samples_train': 101808,
        'n_samples_test': 25452,
        'hyperparams': {'C': 1.0, 'max_iter': 200, 'solver': 'lbfgs', 'multi_class': 'auto'},
        'feature_importances': None,
        'notes': 'Meilleur modèle supervisé du projet',
    },
    {
        'model_name': 'XGBoost',
        'trained_at': '2025-01-15T10:05:00',
        'accuracy': 81.36,
        'precision': 81.30,
        'recall': 81.36,
        'f1_score': 81.30,
        'n_samples_train': 101808,
        'n_samples_test': 25452,
        'hyperparams': {'n_estimators': 100, 'max_depth': 5, 'learning_rate': 0.1},
        'feature_importances': {
            'delta_P16_POP': 0.182, 'delta_P22_POP1564': 0.164,
            'delta_P22_ACT1564': 0.141, 'delta_P22_LOG': 0.118,
            'delta_P22_LOGVAC': 0.097, 'delta_P22_CHOM1564': 0.082,
            'delta_P22_MEN': 0.071, 'delta_P22_EMPLT': 0.063,
            'delta_P22_POP': 0.047, 'delta_P22_POP0014': 0.035,
        },
        'notes': 'Utilisé pour feature importance — 2ème meilleur modèle',
    },
    {
        'model_name': 'Gradient Boosting',
        'trained_at': '2025-01-15T10:10:00',
        'accuracy': 80.83,
        'precision': 80.73,
        'recall': 80.83,
        'f1_score': 80.70,
        'n_samples_train': 101808,
        'n_samples_test': 25452,
        'hyperparams': {'max_iter': 100, 'max_depth': 5},
        'feature_importances': None,
        'notes': 'HistGradientBoostingClassifier (sklearn)',
    },
    {
        'model_name': 'Random Forest',
        'trained_at': '2025-01-15T10:15:00',
        'accuracy': 78.89,
        'precision': 79.36,
        'recall': 78.89,
        'f1_score': 78.31,
        'n_samples_train': 101808,
        'n_samples_test': 25452,
        'hyperparams': {'n_estimators': 100, 'max_depth': None},
        'feature_importances': None,
        'notes': 'RandomForestClassifier',
    },
    {
        'model_name': 'SVM (Linear)',
        'trained_at': '2025-01-15T10:20:00',
        'accuracy': 69.20,
        'precision': 69.96,
        'recall': 69.20,
        'f1_score': 66.47,
        'n_samples_train': 101808,
        'n_samples_test': 25452,
        'hyperparams': {'kernel': 'linear', 'C': 1.0},
        'feature_importances': None,
        'notes': 'Moins performant sur données multi-classes non linéaires',
    },
]


# ── Setup MongoDB ──────────────────────────────────────────────────────────────
def setup_mongodb(drop=False):
    if not MONGO_AVAILABLE:
        print('pymongo non disponible — skipping MongoDB setup')
        return None

    try:
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=3000)
        client.server_info()
    except Exception as e:
        print(f'❌  MongoDB non accessible : {e}')
        return None

    db = client['MSPR_Elections']
    print('✅  Connexion MongoDB établie → MSPR_Elections')

    if drop:
        client.drop_database('MSPR_Elections')
        db = client['MSPR_Elections']
        print('🗑️   Base supprimée et recréée')

    # Create collections with validators
    existing = db.list_collection_names()
    for col_name, validator in VALIDATORS.items():
        if col_name not in existing:
            db.create_collection(col_name, validator={'$jsonSchema': validator['$jsonSchema']},
                                 validationAction='warn')
            print(f'  📁  Collection créée : {col_name}')
        else:
            print(f'  📁  Collection existante : {col_name}')

    # Create indexes
    print('\n  Création des index...')
    db['raw_data'].create_index([('annee', 1), ('code_dept', 1)], name='idx_annee_dept')
    db['raw_data'].create_index([('code_commune', 1)], name='idx_commune')
    db['indicators'].create_index([('code_commune', 1), ('annee', 1)], unique=True, name='idx_commune_annee')
    db['final_data'].create_index([('code_commune', 1)], name='idx_commune')
    db['final_data'].create_index([('etat_economique', 1)], name='idx_etat_eco')
    db['models_metrics'].create_index([('model_name', 1)], unique=True, name='idx_model_name')
    db['predictions'].create_index([('model_name', 1), ('niveau', 1)], name='idx_model_niveau')
    db['predictions'].create_index([('entite', 1)], name='idx_entite')
    print('  ✅  Index créés')

    # Seed models_metrics
    print('\n  Insertion des métriques modèles...')
    for model_doc in SEED_MODELS:
        db['models_metrics'].update_one(
            {'model_name': model_doc['model_name']},
            {'$set': model_doc},
            upsert=True,
        )
    print(f'  ✅  {len(SEED_MODELS)} modèles indexés dans models_metrics')

    # Seed predictions from JSON
    if os.path.exists(PRED_PATH):
        print('\n  Import des prédictions depuis predictions.json...')
        with open(PRED_PATH, encoding='utf-8') as f:
            pred_data = json.load(f)

        docs = []
        generated_at = datetime.now().isoformat()
        for niveau in ('region', 'departement', 'canton'):
            for item in pred_data.get('levels', {}).get(niveau, []):
                docs.append({
                    'model_name':       'default',
                    'generated_at':     generated_at,
                    'niveau':           niveau,
                    'entite':           item.get('entity', ''),
                    'predicted_winner': item.get('predicted', ''),
                    'real_winner':      item.get('real'),
                    'political_side':   item.get('political_side', ''),
                    'economic_state':   item.get('economic_state', ''),
                    'economic_score':   item.get('economic_score'),
                    'is_correct':       item.get('is_correct'),
                    'proba':            item.get('proba', {}),
                })

        if docs:
            db['predictions'].delete_many({'model_name': 'default'})
            db['predictions'].insert_many(docs)
            print(f'  ✅  {len(docs)} prédictions importées dans predictions')

    print('\n✅  Setup MongoDB terminé.')
    return db


# ── Setup TinyDB (fallback) ────────────────────────────────────────────────────
def setup_tinydb():
    if not TINYDB_AVAILABLE:
        print('❌  tinydb non disponible')
        return None

    os.makedirs(os.path.dirname(TINYDB_PATH), exist_ok=True)
    db = TinyDB(TINYDB_PATH)
    print(f'✅  TinyDB initialisé : {TINYDB_PATH}')

    models_table = db.table('models_metrics')
    Q = Query()
    for model_doc in SEED_MODELS:
        models_table.upsert(model_doc, Q.model_name == model_doc['model_name'])
    print(f'  ✅  {len(SEED_MODELS)} modèles dans models_metrics (TinyDB)')

    if os.path.exists(PRED_PATH):
        print('  Import des prédictions...')
        with open(PRED_PATH, encoding='utf-8') as f:
            pred_data = json.load(f)

        preds_table = db.table('predictions')
        preds_table.truncate()
        docs = []
        for niveau in ('region', 'departement', 'canton'):
            for item in pred_data.get('levels', {}).get(niveau, []):
                docs.append({
                    'model_name': 'default',
                    'niveau': niveau,
                    'entite': item.get('entity', ''),
                    'predicted_winner': item.get('predicted', ''),
                    'real_winner': item.get('real'),
                    'political_side': item.get('political_side', ''),
                    'economic_state': item.get('economic_state', ''),
                    'economic_score': item.get('economic_score'),
                    'is_correct': item.get('is_correct'),
                    'proba': item.get('proba', {}),
                })
        if docs:
            preds_table.insert_multiple(docs)
            print(f'  ✅  {len(docs)} prédictions importées (TinyDB)')

    print('✅  Setup TinyDB terminé.')
    return db


# ── Print MCD summary ──────────────────────────────────────────────────────────
def print_mcd():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║          MCD — MODÈLE CONCEPTUEL DE DONNÉES · MSPR_Elections                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  [RAW_DATA]                  [INDICATORS]                                   ║
║  _id: ObjectId               _id: ObjectId                                  ║
║  annee: int (2012|2017)      code_commune: string ←────────┐                ║
║  tour: int (1|2)             nom_commune: string           │                ║
║  code_dept: string           code_dept: string             │                ║
║  nom_dept: string            annee: int (2016|2020)        │                ║
║  code_commune: string ───────┘    population: double       │                ║
║  nom_commune: string         taux_emploi: double           │                ║
║  inscrits: int               taux_chomage: double          │                ║
║  votants: int                taux_activite: double         │                ║
║  abstentions: int            revenus_median: double        │                ║
║  exprimes: int               nb_entreprises: int           │                ║
║  candidats: [                taux_delinquance: double      │                ║
║    { nom, voix, pct_voix }   taux_pauvrete: double         │                ║
║  ]                           vie_associative: int          │                ║
║                                                            │                ║
║  [FINAL_DATA]  ────────────────────────────────────────────┘                ║
║  _id: ObjectId                                                               ║
║  code_commune: string (ref → raw_data, indicators)                          ║
║  annee_ref: int                                                              ║
║  delta_features: { delta_P16_POP, delta_P22_POP1564, ... }                 ║
║  delta_eco_pct: double                                                      ║
║  etat_economique: enum[Boom|Croissance|Stable|Déclin|Crise]                 ║
║  orientation_predite: enum[Centre|D|G|exD|exG]                              ║
║  vainqueur_nom_predit: string                                               ║
║  score_eco_raw: double                                                      ║
║                                                                              ║
║  [MODELS_METRICS]             [PREDICTIONS]                                  ║
║  _id: ObjectId                _id: ObjectId                                  ║
║  model_name: string ──────────→ model_name: string (ref)                    ║
║  trained_at: datetime         generated_at: datetime                        ║
║  accuracy: double             niveau: enum[region|dept|canton]              ║
║  precision: double            entite: string                                ║
║  recall: double               predicted_winner: string                      ║
║  f1_score: double             real_winner: string                           ║
║  n_samples_train: int         political_side: string                        ║
║  n_samples_test: int          economic_state: string                        ║
║  hyperparams: object          economic_score: double                        ║
║  feature_importances: object  is_correct: bool                              ║
║                               proba: { MACRON: %, LE PEN: % }              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Setup NoSQL DB (MongoDB or TinyDB) pour MSPR Electio-Analytics'
    )
    parser.add_argument('--drop',   action='store_true', help='Supprimer et recréer la base')
    parser.add_argument('--import', action='store_true', dest='do_import', help='Importer les données')
    parser.add_argument('--mcd',    action='store_true', help='Afficher le MCD uniquement')
    args = parser.parse_args()

    print('='*60)
    print(' MSPR_Elections — NoSQL Setup (MongoDB / TinyDB)')
    print('='*60)

    print_mcd()

    if args.mcd:
        sys.exit(0)

    # Try MongoDB first
    if MONGO_AVAILABLE:
        db = setup_mongodb(drop=args.drop)
        if db is not None:
            sys.exit(0)

    # Fallback TinyDB
    setup_tinydb()
