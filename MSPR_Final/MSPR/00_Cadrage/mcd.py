"""
Génère le Modèle Conceptuel de Données (MCD) du projet Electio-Analytics
et le sauvegarde dans outputs/mcd_schema.png
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_MSPR_FINAL = os.path.abspath(os.path.join(_SCRIPT_DIR, '..', '..'))
OUTPUT_DIR = os.path.join(_MSPR_FINAL, 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

ENTITY_COLOR = '#1a5276'
ENTITY_TEXT = 'white'
ATTR_COLOR = '#d6eaf8'
ATTR_BORDER = '#2980b9'
RELATION_COLOR = '#e8f8f5'
RELATION_BORDER = '#1abc9c'
LINE_COLOR = '#555555'
PK_COLOR = '#f39c12'

fig, ax = plt.subplots(figsize=(20, 14))
ax.set_xlim(0, 20)
ax.set_ylim(0, 14)
ax.axis('off')
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('#f8f9fa')


def draw_entity(ax, x, y, w, h, title, attributes):
    """Dessine une entité MCD avec son titre et ses attributs."""
    # En-tête entité
    header = FancyBboxPatch((x, y + h - 0.6), w, 0.6,
                             boxstyle="round,pad=0.05",
                             facecolor=ENTITY_COLOR, edgecolor=ENTITY_COLOR, linewidth=1.5)
    ax.add_patch(header)
    ax.text(x + w / 2, y + h - 0.3, title,
            ha='center', va='center', fontsize=10, fontweight='bold', color=ENTITY_TEXT)

    # Corps attributs
    body = FancyBboxPatch((x, y), w, h - 0.6,
                           boxstyle="round,pad=0.05",
                           facecolor=ATTR_COLOR, edgecolor=ATTR_BORDER, linewidth=1.5)
    ax.add_patch(body)

    row_h = (h - 0.6) / max(len(attributes), 1)
    for i, (attr_name, is_pk) in enumerate(attributes):
        attr_y = y + (h - 0.6) - (i + 0.5) * row_h
        if is_pk:
            ax.text(x + 0.2, attr_y, '🔑', ha='left', va='center', fontsize=8)
            ax.text(x + 0.6, attr_y, attr_name, ha='left', va='center',
                    fontsize=8, fontweight='bold', color=PK_COLOR,
                    style='italic', textcoords='data')
        else:
            ax.text(x + 0.3, attr_y, '▸', ha='left', va='center', fontsize=8, color='#555')
            ax.text(x + 0.6, attr_y, attr_name, ha='left', va='center',
                    fontsize=8, color='#2c3e50')
        if i < len(attributes) - 1:
            ax.plot([x + 0.1, x + w - 0.1],
                    [y + (h - 0.6) - (i + 1) * row_h,
                     y + (h - 0.6) - (i + 1) * row_h],
                    color='#bdc3c7', linewidth=0.5)


def draw_relation(ax, x, y, w, h, label):
    """Dessine un losange de relation."""
    diamond_x = [x + w / 2, x + w, x + w / 2, x, x + w / 2]
    diamond_y = [y + h, y + h / 2, y, y + h / 2, y + h]
    ax.fill(diamond_x, diamond_y, color=RELATION_COLOR, edgecolor=RELATION_BORDER, linewidth=1.5)
    ax.text(x + w / 2, y + h / 2, label,
            ha='center', va='center', fontsize=8, fontweight='bold', color='#1abc9c')


def draw_arrow(ax, x1, y1, x2, y2, card1='', card2=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=LINE_COLOR, lw=1.5))
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    if card1:
        ax.text(x1 + (x2 - x1) * 0.15, y1 + (y2 - y1) * 0.15, card1,
                fontsize=8, color='#c0392b', fontweight='bold', ha='center')
    if card2:
        ax.text(x1 + (x2 - x1) * 0.85, y1 + (y2 - y1) * 0.85, card2,
                fontsize=8, color='#c0392b', fontweight='bold', ha='center')


def draw_line(ax, x1, y1, x2, y2):
    ax.plot([x1, x2], [y1, y2], color=LINE_COLOR, linewidth=1.5)


# --- Titre ---
ax.text(10, 13.5, 'Modèle Conceptuel de Données — Electio-Analytics / Nouvelle-Aquitaine',
        ha='center', va='center', fontsize=14, fontweight='bold', color='#1a5276')
ax.text(10, 13.1, 'MSPR TPRE813 — POC Prédiction Électorale',
        ha='center', va='center', fontsize=10, color='#555')

# --- Entité COMMUNE (centre-haut) ---
commune_attrs = [
    ('codgeo CHAR(5)', True),
    ('nom_commune VARCHAR(100)', False),
    ('code_dept CHAR(2)', False),
    ('nom_departement VARCHAR(50)', False),
    ('region VARCHAR(50)', False),
]
draw_entity(ax, 7.5, 9.5, 4.5, 3.0, 'COMMUNE', commune_attrs)

# --- Entité ELECTION (gauche) ---
election_attrs = [
    ('id_election INT', True),
    ('codgeo CHAR(5) [FK]', False),
    ('annee INT', False),
    ('tour INT', False),
    ('candidat_gagnant VARCHAR(80)', False),
    ('nb_voix INT', False),
    ('pct_voix FLOAT', False),
    ('bloc_politique VARCHAR(20)', False),
]
draw_entity(ax, 0.5, 5.5, 4.5, 4.5, 'ELECTION', election_attrs)

# --- Entité INDICATEUR_SOCIO_ECO (droite) ---
indic_attrs = [
    ('id_indic INT', True),
    ('codgeo CHAR(5) [FK]', False),
    ('annee INT', False),
    ('population FLOAT', False),
    ('emploi_salarie FLOAT', False),
    ('revenus_median FLOAT', False),
    ('taux_chomage FLOAT', False),
    ('taux_delinquance FLOAT', False),
    ('nb_logements FLOAT', False),
    ('taux_diplome FLOAT', False),
]
draw_entity(ax, 14.5, 5.5, 5.0, 5.0, 'INDICATEUR_SOCIO_ECO', indic_attrs)

# --- Entité DELTA_INDICATEUR (centre-milieu) ---
delta_attrs = [
    ('id_delta INT', True),
    ('codgeo CHAR(5) [FK]', False),
    ('delta_population FLOAT', False),
    ('delta_emploi FLOAT', False),
    ('delta_revenus FLOAT', False),
    ('delta_delinquance FLOAT', False),
    ('delta_logements FLOAT', False),
    ('delta_chomage FLOAT', False),
    ('etat_eco ENUM(Boom,Crois,Stable,Déclin,Crise)', False),
]
draw_entity(ax, 7.5, 4.0, 4.5, 4.5, 'DELTA_INDICATEUR', delta_attrs)

# --- Entité PREDICTION (bas-centre) ---
pred_attrs = [
    ('id_pred INT', True),
    ('codgeo CHAR(5) [FK]', False),
    ('annee_cible INT', False),
    ('scenario INT (1/2/3 ans)', False),
    ('bloc_predit VARCHAR(20)', False),
    ('proba_macron FLOAT', False),
    ('proba_lepen FLOAT', False),
    ('confidence FLOAT', False),
]
draw_entity(ax, 7.5, 0.3, 4.5, 3.5, 'PREDICTION', pred_attrs)

# --- Relations ---
# COMMUNE ← ELECTION (1,N)
draw_line(ax, 5.0, 7.75, 7.5, 10.5)
ax.text(6.1, 9.4, '1', fontsize=9, color='#c0392b', fontweight='bold')
ax.text(5.3, 8.2, 'N', fontsize=9, color='#c0392b', fontweight='bold')
ax.text(6.2, 8.7, 'localisée_dans', fontsize=7, color='#555', rotation=37)

# COMMUNE ← INDICATEUR (1,N)
draw_line(ax, 12.0, 10.5, 14.5, 8.0)
ax.text(12.2, 10.1, '1', fontsize=9, color='#c0392b', fontweight='bold')
ax.text(13.8, 8.4, 'N', fontsize=9, color='#c0392b', fontweight='bold')
ax.text(12.8, 9.3, 'décrit_par', fontsize=7, color='#555', rotation=-30)

# INDICATEUR → DELTA (calcul)
draw_line(ax, 14.5, 7.0, 12.0, 6.0)
ax.text(13.8, 7.1, 'calcul\ndelta', fontsize=7, color='#1abc9c', fontweight='bold')

# DELTA ← COMMUNE (1,N)
draw_line(ax, 9.75, 8.5, 9.75, 8.5)
draw_line(ax, 9.75, 8.5, 9.75, 8.5)

# COMMUNE → DELTA
draw_line(ax, 9.75, 9.5, 9.75, 8.5)
ax.text(9.9, 9.0, '1', fontsize=9, color='#c0392b', fontweight='bold')
ax.text(9.9, 8.6, 'N', fontsize=9, color='#c0392b', fontweight='bold')

# DELTA → PREDICTION
draw_line(ax, 9.75, 4.0, 9.75, 3.8)
ax.text(9.9, 3.9, 'génère', fontsize=7, color='#555')
ax.annotate('', xy=(9.75, 3.8), xytext=(9.75, 4.0),
            arrowprops=dict(arrowstyle='->', color=LINE_COLOR, lw=1.5))

# ELECTION → PREDICTION (référence)
draw_line(ax, 5.0, 5.5, 7.5, 2.0)
ax.text(5.8, 3.5, 'alimente\n(historique)', fontsize=7, color='#555', rotation=30)

# --- Légende ---
legend_elements = [
    mpatches.Patch(facecolor=ENTITY_COLOR, label='Entité'),
    mpatches.Patch(facecolor=ATTR_COLOR, edgecolor=ATTR_BORDER, label='Attributs'),
    mpatches.Patch(facecolor='#fff3cd', edgecolor=PK_COLOR, label='Clé primaire (PK)'),
    plt.Line2D([0], [0], color=LINE_COLOR, linewidth=1.5, label='Association (1,N)'),
]
ax.legend(handles=legend_elements, loc='lower left', fontsize=8,
          framealpha=0.9, bbox_to_anchor=(0.01, 0.01))

plt.tight_layout()
out_path = os.path.join(OUTPUT_DIR, 'mcd_schema.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='#f8f9fa')
plt.close()
print(f"✅ MCD sauvegardé : {out_path}")
