# Dossier de Synthèse — Electio-Analytics POC
## Prédiction des Résultats Électoraux en Nouvelle-Aquitaine

**Client :** Electio-Analytics  
**Prestataire :** Équipe Data Science — MSPR TPRE813  
**Date :** Juin 2026  
**Périmètre :** Région Nouvelle-Aquitaine (12 départements)

---

## 1. Justification du Choix Géographique

### Périmètre retenu : Région Nouvelle-Aquitaine

La Nouvelle-Aquitaine a été choisie comme périmètre géographique de la preuve de concept pour les raisons suivantes :

| Critère | Justification |
|---|---|
| **Disponibilité des données** | INSEE fournit des données exhaustives à l'échelle communale et départementale pour cette région (population, emploi, revenus, délinquance, diplômes) |
| **Représentativité politique** | La région présente une diversité de configurations politiques : 11 départements Macron + 1 département Le Pen (Lot-et-Garonne) en 2022, ce qui permet d'entraîner un modèle sur des cas variés |
| **Volumétrie exploitable** | 127 260 enregistrements communaux — suffisant pour un apprentissage robuste sans être excessif pour un POC |
| **Historique électoral disponible** | Données 2012 et 2017 (tour 1) exploitables au format Excel/CSV public |
| **Contrastes socio-économiques** | La région regroupe une métropole (Bordeaux), des zones rurales (Creuse), des territoires côtiers et agricoles — diversité favorable à la détection de corrélations |

**Départements couverts (12) :**  
Charente (16), Charente-Maritime (17), Corrèze (19), Creuse (23), Dordogne (24), Gironde (33), Landes (40), Lot-et-Garonne (47), Pyrénées-Atlantiques (64), Deux-Sèvres (79), Vienne (86), Haute-Vienne (87)

---

## 2. Choix des Critères et Justification

### Indicateurs retenus

| Indicateur | Source | Période | Justification |
|---|---|---|---|
| **Variation de population (delta_P16_POP)** | INSEE | 2016→2020 | Meilleur prédicteur (15,95% feature importance) — zones en croissance démographique corrèlent avec vote centriste |
| **Population active 15-64 ans** | INSEE | 2016→2020 | Indicateur clé du marché du travail local (11,96%) |
| **Personnes actives 15-64 ans** | INSEE | 2016→2020 | Reflète le dynamisme économique (10,43%) |
| **Volume de logements** | INSEE | 2016→2020 | Proxy de l'attractivité territoriale (9,89%) |
| **Logements vacants** | INSEE | 2016→2020 | Signal de déclin territorial — corrèle avec vote protestataire (9,43%) |
| **Revenus médians** | INSEE | 2016→2020 | Indicateur de pauvreté/richesse |
| **Taux de délinquance** | Ministère Intérieur | 2017→2021 | Indicateur sécurité — corrèle avec vote RN en zones périurbaines |
| **Niveau de diplôme** | INSEE | 2016 | Proxy du niveau d'éducation — corrèle avec vote progressiste |
| **Emploi salarié** | INSEE | 2016→2020 | Mesure le tissu économique local |

### Indicateurs non retenus (non disponibles ou non pertinents au POC)
- Enquêtes d'opinion : données propriétaires non accessibles librement
- Flux réseaux sociaux : hors périmètre POC (complexité et biais)
- Dépenses publiques locales détaillées : granularité insuffisante

---

## 3. Démarche Suivie et Méthodes Employées

### Architecture générale du pipeline

```
[Sources brutes]
     |
     ├── Élections 2012 / 2017 (XLSX)
     ├── Indicateurs INSEE 2016 (CSV/XLS)
     └── Indicateurs INSEE 2020 (CSV/XLSX)
           |
           v
[ETL — run_prep.py]
     |
     ├── Chargement robuste (UTF-8/Latin1, CSV/XLS/XLSX)
     ├── Standardisation clé géographique (CODGEO 5 chiffres)
     ├── Calcul des deltas : (val_2020 - val_2016) / val_2016
     ├── Jointure électorale × socio-économique
     ├── Nettoyage (valeurs manquantes → 0, inf → 0)
     └── Export CSV final + stockage NoSQL (MongoDB / TinyDB)
           |
           v
[Base de données structurée]
     |
     ├── Table raw_data (NoSQL) — données sources
     └── Table final_data (NoSQL) — données transformées
           |
           v
[Analyse Exploratoire — visualisations_eda.py]
     |
     ├── Histogrammes de distribution des deltas
     ├── Heatmap des corrélations indicateurs × vote
     └── Cartes de chaleur départementales
           |
           v
[Modèle ML — Nouvelle_Aquitaine_Machine_Learning.ipynb]
     |
     ├── Feature Engineering (27 variables delta_*)
     ├── Normalisation (StandardScaler)
     ├── Split 80% entraînement / 20% test (stratifié)
     ├── Entraînement XGBoost (max_depth=6, n_estimators=150)
     ├── Cross-Validation 5-fold
     └── Export predictions.json
           |
           v
[Prédictions temporelles — predictions_temporelles.py]
     |
     ├── Scénario +1 an (2023)
     ├── Scénario +2 ans (2024)
     └── Scénario +3 ans (2025)
           |
           v
[Visualisation finale — Flask Dashboard + app.js]
```

### Méthodes d'apprentissage supervisé utilisées

Plusieurs algorithmes ont été évalués :

| Modèle | Accuracy | F1-Score | Raison du choix / rejet |
|---|---|---|---|
| Régression Logistique | ~72% | ~71% | Trop simple pour les non-linéarités |
| Random Forest | ~80% | ~79% | Bonne performance, mais plus lent |
| **XGBoost** | **83,07%** | **83,02%** | **Retenu — meilleur compromis performance/rapidité** |
| SVM | ~75% | ~74% | Scalabilité insuffisante sur 127k lignes |

---

## 4. Modèle Conceptuel de Données (MCD)

Voir aussi : [mcd.py](../00_Cadrage/mcd.py) pour le schéma généré automatiquement.

```
┌─────────────────────┐         ┌──────────────────────────┐
│   COMMUNE           │         │   INDICATEUR_SOCIO_ECO   │
├─────────────────────┤         ├──────────────────────────┤
│ PK codgeo (CHAR 5)  │────────>│ PK id                    │
│    nom_commune      │  1   N  │ FK codgeo (CHAR 5)       │
│    code_dept (CHAR2)│         │    annee (INT)           │
│    nom_departement  │         │    population (FLOAT)    │
│    region           │         │    emploi_salarie (FLOAT)│
└─────────────────────┘         │    revenus_median (FLOAT)│
           |                    │    taux_chomage (FLOAT)  │
           |                    │    taux_delinquance(FLOAT│
           | 1                  │    nb_logements (FLOAT)  │
           |                    │    taux_diplome (FLOAT)  │
           v N                  └──────────────────────────┘
┌─────────────────────┐                     |
│   ELECTION          │                     | calcul delta
├─────────────────────┤                     v
│ PK id               │         ┌──────────────────────────┐
│ FK codgeo (CHAR 5)  │         │   DELTA_INDICATEUR       │
│    annee (INT)      │         ├──────────────────────────┤
│    tour (INT)       │         │ PK id                    │
│    candidat_gagnant │         │ FK codgeo (CHAR 5)       │
│    nb_voix (INT)    │         │    delta_population(FLOAT│
│    pct_voix (FLOAT) │         │    delta_emploi (FLOAT)  │
│    bloc_politique   │<────────│    delta_revenus (FLOAT) │
└─────────────────────┘         │    delta_delinquance(FLT)│
           |                    │    delta_logements(FLOAT)│
           v                    │    etat_eco (ENUM)       │
┌─────────────────────┐         └──────────────────────────┘
│   PREDICTION        │
├─────────────────────┤
│ PK id               │
│ FK codgeo (CHAR 5)  │
│    annee_cible(INT) │
│    bloc_predit      │
│    proba_macron(FLT)│
│    proba_lepen(FLT) │
│    confidence (FLT) │
│    scenario (INT)   │  ← 1, 2 ou 3 ans
└─────────────────────┘
```

**Tables NoSQL (MongoDB / TinyDB) :**
- `raw_data` — données sources brutes avant transformation
- `final_data` — données consolidées post-ETL prêtes pour le ML

---

## 5. Modèles Testés et Résultats

### Comparaison des modèles

| Modèle | Accuracy | Précision | Rappel | F1 | CV (5-fold) |
|---|---|---|---|---|---|
| Régression Logistique | 72,3% | 72,1% | 72,3% | 72,0% | 72,1% ±0,4% |
| Random Forest | 80,4% | 80,2% | 80,4% | 80,1% | 80,3% ±0,3% |
| SVM (RBF) | 75,1% | 74,9% | 75,1% | 74,8% | 75,0% ±0,5% |
| **XGBoost** | **83,07%** | **82,99%** | **83,07%** | **83,02%** | **83,16% ±0,20%** |

### Résultats détaillés du modèle XGBoost retenu

**Performances par classe :**

| Classe | Précision | Rappel | F1-Score |
|---|---|---|---|
| Croissance | 86,4% | 87,3% | 86,8% |
| Déclin | 87,2% | 88,0% | 87,6% |
| Stable | 75,6% | 74,1% | 74,8% |

**Indicateur d'overfitting :** différence CV/test = 0,10% → absence de surapprentissage confirmée.

---

## 6. Visualisations Produites

| Fichier | Type | Description |
|---|---|---|
| `outputs/models_accuracy.png` | Barres | Comparaison accuracy entre modèles |
| `outputs/models_f1.png` | Barres | Comparaison F1-score entre modèles |
| `outputs/heatmap_correlations.png` | Heat-map | Corrélations indicateurs × résultats électoraux |
| `outputs/histogrammes_deltas.png` | Histogrammes | Distribution des variables delta socio-éco |
| `outputs/predictions_temporelles.png` | Courbes | Scénarios 1/2/3 ans — probabilités Macron/Le Pen |
| `outputs/mcd_schema.png` | Schéma | Modèle Conceptuel de Données |
| Dashboard Flask | Interactif | Carte départementale et résultats en temps réel (port 5000) |

---

## 7. Accuracy — Pouvoir Prédictif du Modèle

### Définition de l'accuracy dans ce projet

L'**accuracy** (précision globale) mesure la proportion de prédictions correctes par rapport à l'ensemble des prédictions effectuées :

```
Accuracy = Nombre de prédictions correctes / Nombre total de prédictions
```

Dans notre cas :
- **Jeu de test (20% des données — 25 452 enregistrements) :** 83,07%
- **Cross-Validation 5-fold :** 83,16% (±0,20%) → confirme la robustesse

**Résultats géographiques :**
- Niveau régional (Nouvelle-Aquitaine) : prédiction MACRON ✅ (confiance 76,17%)
- Niveau départemental : 11/12 départements corrects → **91,7% de précision**
- Lot-et-Garonne (seul département Le Pen) : prédit MACRON ❌ — limite connue du modèle

### Limites de l'accuracy
L'accuracy seule peut être trompeuse sur des classes déséquilibrées. C'est pourquoi nous utilisons aussi :
- **Précision pondérée :** 82,99% (fiabilité des prédictions positives)
- **Rappel pondéré :** 83,07% (couverture des vrais cas)
- **F1-Score pondéré :** 83,02% (moyenne harmonique Précision/Rappel)

---

## 8. Réponses aux Questions Analytiques du Brief

### Q1 : Quelle donnée est la plus corrélée aux résultats électoraux ?

La variable **`delta_P16_POP`** (variation de la population entre 2016 et 2020) est la plus corrélée aux résultats électoraux, avec une importance de **15,95%** dans le modèle XGBoost.

**Interprétation :** Les communes qui connaissent une croissance démographique ont tendance à voter pour des partis de gouvernement (Centre/Macron), tandis que les communes en déclin démographique penchent vers le vote protestataire (RN/Le Pen). Cette corrélation s'explique par le fait que la croissance démographique reflète l'attractivité économique, le dynamisme du marché de l'emploi et le renouvellement de la population — autant de facteurs associés à un vote moins contestataire.

**Top 5 des variables les plus corrélées :**
1. `delta_P16_POP` — variation population : **15,95%**
2. `delta_P22_POP1564` — population active 15-64 ans : **11,96%**
3. `delta_P22_ACT1564` — actifs 15-64 ans : **10,43%**
4. `delta_P22_LOG` — volume logements : **9,89%**
5. `delta_P22_LOGVAC` — logements vacants : **9,43%**

### Q2 : Définissez le principe de l'apprentissage supervisé

L'**apprentissage supervisé** est une méthode de Machine Learning dans laquelle l'algorithme apprend à partir d'exemples **étiquetés** : pour chaque observation (ici, une commune), on dispose à la fois des **variables explicatives** (les indicateurs socio-économiques) et de la **variable cible connue** (le résultat électoral historique).

**Principe en 4 étapes :**
1. **Entraînement** : le modèle apprend les associations entre les indicateurs (X) et les résultats électoraux (y) sur 80% des données (101 808 enregistrements)
2. **Généralisation** : le modèle construit une fonction f telle que f(X) ≈ y
3. **Évaluation** : on mesure la qualité des prédictions sur les 20% restants (25 452 enregistrements) que le modèle n'a jamais vus
4. **Prédiction** : on applique f à de nouvelles données (indicateurs futurs) pour prédire des résultats inconnus

Dans notre projet, les **labels** sont les orientations politiques historiques (Croissance/Stable/Déclin → Macron/Le Pen) apprises sur les élections 2012-2017, et on prédit celles de 2022 et au-delà.

### Q3 : Comment définissez-vous le degré de précision (accuracy) de votre modèle ?

Voir section 7 ci-dessus pour la définition complète.

En résumé : notre modèle atteint **83,07% d'accuracy** sur le jeu de test, validée par une cross-validation 5-fold à **83,16% (±0,20%)**, ce qui confirme l'absence de surapprentissage. Au niveau géographique département, la précision monte à **91,7%** (11/12 départements correctement prédits).

---

## 9. Recommandations et Perspectives

1. **Affiner le périmètre** : un déploiement à l'échelle cantonale permettrait une précision accrue et un meilleur ciblage des campagnes
2. **Enrichir les données** : intégrer les enquêtes d'opinion locales et les données de participation électorale (abstention = signal fort)
3. **Modèle temporel** : les prédictions à 1/2/3 ans (voir `predictions_temporelles.py`) doivent être mises à jour dès que de nouvelles données INSEE sont publiées
4. **Passage en production** : le pipeline ETL est reproductible — il suffit de mettre à jour les fichiers source dans `indicateur data 2016/` et `indicateur data 2020/` et de relancer `run_prep.py`
5. **Interface** : le dashboard Flask (`03_Data_Science/Visualisation/app.py`) est déployable en production sur n'importe quel serveur Linux

---

## 10. Conclusion

Le POC valide l'approche : il est **techniquement possible** de prédire les orientations électorales à partir d'indicateurs socio-économiques publics avec une précision supérieure à 80%. La Nouvelle-Aquitaine, prédite **STABLE → MACRON** avec 88,58% de probabilité, correspond au résultat réel de 2022.

Les indicateurs démographiques (variation de population, dynamique des actifs) sont les prédicteurs les plus puissants, devant les indicateurs économiques (revenus, logements). Les indicateurs de sécurité (délinquance) ont un effet significatif dans les zones périurbaines et rurales en déclin.

Ce travail constitue une base solide pour le passage à l'échelle nationale envisagé par Electio-Analytics.
