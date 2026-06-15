# Dictionnaire des Variables — Dataset Nouvelle-Aquitaine

**Projet :** Electio-Analytics POC — MSPR TPRE813  
**Fichier source :** `data_nouvelle_aquitaine_nettoye.csv`  
**Dimensions :** 113260 enregistrements × 21 variables  

---

| Variable | Type | Description | Source | Valeurs possibles |
|---|---|---|---|---|
| `codgeo` | str | Code géographique INSEE commune (5 chiffres) | INSEE | ex. 33001 |
| `code_departement` | str | Code département (2 chiffres) | INSEE | 16 à 87 |
| `nom_departement` | str | Nom du département | INSEE | ex. Gironde |
| `region` | str | Région administrative | INSEE | Nouvelle-Aquitaine |
| `delta_P16_POP` | float | Variation population totale 2016→2020 | INSEE RP | [-0.15 ; +0.20] |
| `delta_P22_POP1564` | float | Variation population active 15-64 ans | INSEE RP | [-0.12 ; +0.18] |
| `delta_P22_ACT1564` | float | Variation actifs 15-64 ans | INSEE RP | [-0.12 ; +0.18] |
| `delta_P22_LOG` | float | Variation nb logements | INSEE RP | [-0.12 ; +0.18] |
| `delta_P22_LOGVAC` | float | Variation logements vacants | INSEE RP | [-0.20 ; +0.25] |
| `delta_revenus_median` | float | Variation revenus médians | INSEE FiLoSoFi | [-0.05 ; +0.10] |
| `delta_P22_EMPLT` | float | Variation emploi salarié | INSEE RP | [-0.10 ; +0.15] |
| `delta_taux_chomage` | float | Variation taux de chômage | INSEE RP | [-0.08 ; +0.15] |
| `delta_delinquance` | float | Variation indicateur délinquance | Min. Intérieur | [-0.15 ; +0.20] |
| `delta_diplome_superieur` | float | Variation diplôme supérieur | INSEE RP | [-0.08 ; +0.12] |
| `score_eco_composite` | float | Score économique composite calculé | Calculé | Pondération deltas |
| `etat_economique` | categ. | État économique classifié | Calculé | Boom/Croissance/Stable/Déclin/Crise |
| `target_ml` | categ. | Variable cible pour ML (3 classes) | Calculé | Croissance/Stable/Déclin |
| `proba_macron` | float | Probabilité prédite bloc Macron (%) | Modèle XGBoost | [0 ; 100] |
| `proba_lepen` | float | Probabilité prédite bloc Le Pen (%) | Modèle XGBoost | [0 ; 100] |
| `vainqueur_predit` | str | Vainqueur prédit au second tour | Modèle XGBoost | MACRON / LE PEN |
| `annee_reference` | int | Année de référence de la prédiction | Référentiel | 2022 |

---

## Distribution des classes (variable cible `target_ml`)

- **Croissance** : 56228 enregistrements (49.6%)
- **Stable** : 46724 enregistrements (41.3%)
- **Déclin** : 10308 enregistrements (9.1%)

## Distribution géographique

- **Gironde** : 16000 enregistrements
- **Pyrénées-Atlantiques** : 12000 enregistrements
- **Charente-Maritime** : 10000 enregistrements
- **Landes** : 10000 enregistrements
- **Charente** : 9000 enregistrements
- **Dordogne** : 9000 enregistrements
- **Vienne** : 9000 enregistrements
- **Haute-Vienne** : 9000 enregistrements
- **Deux-Sèvres** : 8000 enregistrements
- **Corrèze** : 7500 enregistrements
- **Lot-et-Garonne** : 7500 enregistrements
- **Creuse** : 6260 enregistrements
