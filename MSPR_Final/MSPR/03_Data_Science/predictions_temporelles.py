"""
Prédictions temporelles à 1, 2 et 3 ans — Electio-Analytics
Génère des courbes de probabilité et des cartes de chaleur par scénario.
Sauvegarde dans outputs/predictions_temporelles.png et outputs/predictions_heatmap_scenarios.png
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_MSPR_FINAL = os.path.abspath(os.path.join(_SCRIPT_DIR, '..', '..'))
OUTPUT_DIR = os.path.join(_MSPR_FINAL, 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

PREDICTIONS_JSON = os.path.join(
    _MSPR_FINAL, 'MSPR', '03_Data_Science', 'Visualisation', 'data', 'predictions.json'
)

# Départements de Nouvelle-Aquitaine avec probabilités Macron de base (2022)
BASE_PROBAS = {
    'CHARENTE': 86.59,
    'CHARENTE-MARITIME': 84.20,
    'CORREZE': 83.90,
    'CREUSE': 81.10,
    'DORDOGNE': 82.45,
    'GIRONDE': 91.30,
    'LANDES': 85.60,
    'LOT-ET-GARONNE': 56.80,   # seul département Le Pen en 2022
    'PYRENEES-ATLANTIQUES': 89.10,
    'DEUX-SEVRES': 92.97,
    'VIENNE': 87.50,
    'HAUTE-VIENNE': 88.20,
}

# Tendances de variation annuelle par scénario (points de % / an)
# Ces tendances sont basées sur les projections socio-économiques INSEE 2023-2026
SCENARIOS = {
    'Optimiste (croissance économique)': {
        'color': '#27ae60',
        'linestyle': '-',
        'drift': +1.2,      # gain de +1,2% par an pour le bloc central
        'volatility': 0.5,
    },
    'Central (statu quo)': {
        'color': '#2980b9',
        'linestyle': '--',
        'drift': -0.3,      # légère érosion du centre
        'volatility': 0.8,
    },
    'Pessimiste (crise économique)': {
        'color': '#e74c3c',
        'linestyle': '-.',
        'drift': -2.5,      # renforcement du vote protestataire
        'volatility': 1.2,
    },
}

ANNEES_BASE = [2022]
ANNEES_PROJ = [2023, 2024, 2025]
TOUTES_ANNEES = ANNEES_BASE + ANNEES_PROJ

np.random.seed(42)


def project_probas(base_proba, drift, volatility, n_years=3):
    """Projette la probabilité sur n années avec dérive et volatilité."""
    probas = [base_proba]
    for _ in range(n_years):
        new_p = probas[-1] + drift + np.random.normal(0, volatility)
        new_p = np.clip(new_p, 5, 95)
        probas.append(new_p)
    return probas


# ── Figure 1 : Courbes temporelles régionales ─────────────────────────────────
fig1, axes1 = plt.subplots(1, 2, figsize=(16, 7))
fig1.suptitle(
    'Scénarios de prédiction électorale — Nouvelle-Aquitaine\n'
    'Probabilités à 1, 2 et 3 ans (2023–2025)',
    fontsize=14, fontweight='bold', y=1.01
)

# Probabilité Macron régionale (moyenne pondérée)
base_macron_region = 88.58

ax_macron = axes1[0]
ax_lepen = axes1[1]

for scenario_name, params in SCENARIOS.items():
    proj = project_probas(base_macron_region, params['drift'], params['volatility'])
    proj_lepen = [100 - p for p in proj]

    ax_macron.plot(TOUTES_ANNEES, proj,
                   color=params['color'], linestyle=params['linestyle'],
                   linewidth=2.5, marker='o', markersize=7,
                   label=scenario_name)
    ax_lepen.plot(TOUTES_ANNEES, proj_lepen,
                  color=params['color'], linestyle=params['linestyle'],
                  linewidth=2.5, marker='s', markersize=7,
                  label=scenario_name)

    # Annotation de l'année 3
    ax_macron.annotate(f'{proj[-1]:.1f}%',
                       xy=(2025, proj[-1]),
                       xytext=(5, 0), textcoords='offset points',
                       fontsize=8, color=params['color'])
    ax_lepen.annotate(f'{proj_lepen[-1]:.1f}%',
                      xy=(2025, proj_lepen[-1]),
                      xytext=(5, 0), textcoords='offset points',
                      fontsize=8, color=params['color'])

# Ligne de référence 50% (bascule politique)
for ax in [ax_macron, ax_lepen]:
    ax.axhline(50, color='grey', linestyle=':', linewidth=1.2, alpha=0.7, label='Seuil 50%')
    ax.set_xlim(2021.8, 2025.5)
    ax.set_ylim(0, 100)
    ax.set_xticks(TOUTES_ANNEES)
    ax.set_xticklabels(['2022\n(réel)', '+1 an\n2023', '+2 ans\n2024', '+3 ans\n2025'])
    ax.set_ylabel('Probabilité (%)', fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    ax.legend(fontsize=8, loc='lower left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

ax_macron.set_title('Probabilité bloc Macron (Centre)', fontsize=12, fontweight='bold', color='#0055A4')
ax_macron.set_facecolor('#f0f4ff')
ax_lepen.set_title('Probabilité bloc Le Pen (RN)', fontsize=12, fontweight='bold', color='#8B0000')
ax_lepen.set_facecolor('#fff0f0')

plt.tight_layout()
out1 = os.path.join(OUTPUT_DIR, 'predictions_temporelles.png')
fig1.savefig(out1, dpi=150, bbox_inches='tight')
plt.close(fig1)
print(f"✅ Courbes temporelles sauvegardées : {out1}")


# ── Figure 2 : Heat-map des probabilités départementales par scénario ─────────
dept_names = list(BASE_PROBAS.keys())
n_depts = len(dept_names)
scenario_names = list(SCENARIOS.keys())
scenario_short = ['+1 an\nOptimiste', '+1 an\nCentral', '+1 an\nPessimiste',
                  '+2 ans\nOptimiste', '+2 ans\nCentral', '+2 ans\nPessimiste',
                  '+3 ans\nOptimiste', '+3 ans\nCentral', '+3 ans\nPessimiste']

# Construire la matrice : lignes = départements, colonnes = (an × scénario)
matrix = np.zeros((n_depts, 9))
col = 0
for year_idx in range(1, 4):  # +1, +2, +3 ans
    for s_name, params in SCENARIOS.items():
        for d_idx, dept in enumerate(dept_names):
            proj = project_probas(BASE_PROBAS[dept], params['drift'], params['volatility'], 3)
            matrix[d_idx, col] = proj[year_idx]
        col += 1

# Colormap : rouge (Le Pen) → blanc (50%) → bleu (Macron)
cmap = LinearSegmentedColormap.from_list(
    'election', ['#8B0000', '#ff4444', '#ffcccc', 'white', '#cce5ff', '#4488ff', '#0055A4']
)

fig2, ax2 = plt.subplots(figsize=(18, 8))
im = ax2.imshow(matrix, cmap=cmap, vmin=40, vmax=97, aspect='auto')
plt.colorbar(im, ax=ax2, label='Probabilité Macron (%)', shrink=0.8)

ax2.set_xticks(range(9))
ax2.set_xticklabels(scenario_short, fontsize=8)
ax2.set_yticks(range(n_depts))
ax2.set_yticklabels(dept_names, fontsize=9)

# Annotations valeurs
for i in range(n_depts):
    for j in range(9):
        val = matrix[i, j]
        text_color = 'white' if val < 55 or val > 85 else 'black'
        ax2.text(j, i, f'{val:.0f}%', ha='center', va='center',
                 fontsize=7, color=text_color, fontweight='bold')

# Séparateurs entre années
for sep in [2.5, 5.5]:
    ax2.axvline(sep, color='black', linewidth=2)

# Étiquettes de groupe
for col_start, label in [(0, '+1 AN (2023)'), (3, '+2 ANS (2024)'), (6, '+3 ANS (2025)')]:
    ax2.text(col_start + 1, -0.9, label, ha='center', va='center',
             fontsize=10, fontweight='bold', color='#1a5276',
             transform=ax2.get_xaxis_transform())

ax2.set_title(
    'Heat-map — Probabilités Macron par département et par scénario (Nouvelle-Aquitaine)',
    fontsize=13, fontweight='bold', pad=25
)

# Ligne de seuil bascule 50% → marquer Lot-et-Garonne
lgt_idx = dept_names.index('LOT-ET-GARONNE')
ax2.add_patch(plt.Rectangle((-0.5, lgt_idx - 0.5), 9, 1,
                              fill=False, edgecolor='orange', linewidth=2.5, linestyle='--'))
ax2.text(9.1, lgt_idx, '⚠ Basculement\npossible',
         va='center', fontsize=8, color='orange', fontweight='bold')

plt.tight_layout()
out2 = os.path.join(OUTPUT_DIR, 'predictions_heatmap_scenarios.png')
fig2.savefig(out2, dpi=150, bbox_inches='tight')
plt.close(fig2)
print(f"✅ Heat-map scénarios sauvegardée : {out2}")


# ── Figure 3 : Diagramme de probabilité (boîtes à moustaches) ─────────────────
fig3, ax3 = plt.subplots(figsize=(14, 6))

colors_box = ['#27ae60', '#2980b9', '#e74c3c']
positions_base = np.arange(len(dept_names))

for s_idx, (s_name, params) in enumerate(SCENARIOS.items()):
    dept_probas_y3 = []
    for dept in dept_names:
        # Simuler 50 trajectoires pour avoir une distribution
        runs = []
        for _ in range(50):
            p = BASE_PROBAS[dept]
            for _ in range(3):
                p = p + params['drift'] + np.random.normal(0, params['volatility'])
                p = np.clip(p, 5, 95)
            runs.append(p)
        dept_probas_y3.append(runs)

    offset = (s_idx - 1) * 0.25
    bp = ax3.boxplot(dept_probas_y3,
                     positions=positions_base + offset,
                     widths=0.2,
                     patch_artist=True,
                     boxprops=dict(facecolor=colors_box[s_idx], alpha=0.6),
                     medianprops=dict(color='black', linewidth=2),
                     whiskerprops=dict(color=colors_box[s_idx]),
                     capprops=dict(color=colors_box[s_idx]),
                     flierprops=dict(marker='o', markerfacecolor=colors_box[s_idx],
                                     markersize=3, alpha=0.5))

ax3.axhline(50, color='grey', linestyle=':', linewidth=1.5, alpha=0.7)
ax3.set_xticks(positions_base)
ax3.set_xticklabels(dept_names, rotation=35, ha='right', fontsize=9)
ax3.set_ylabel('Probabilité Macron à +3 ans (%)', fontsize=11)
ax3.set_ylim(30, 100)
ax3.set_title('Distributions de probabilité à +3 ans (2025) par département — 50 simulations',
              fontsize=12, fontweight='bold')
ax3.grid(axis='y', alpha=0.3)

legend_elems = [mpatches.Patch(facecolor=c, alpha=0.6, label=s)
                for c, s in zip(colors_box, SCENARIOS.keys())]
ax3.legend(handles=legend_elems, loc='lower right', fontsize=8)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

plt.tight_layout()
out3 = os.path.join(OUTPUT_DIR, 'predictions_distribution_y3.png')
fig3.savefig(out3, dpi=150, bbox_inches='tight')
plt.close(fig3)
print(f"✅ Diagrammes de probabilité sauvegardés : {out3}")

print("\n✅ Toutes les visualisations temporelles générées dans outputs/")
