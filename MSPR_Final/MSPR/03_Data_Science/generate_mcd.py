"""
generate_mcd.py
===============
Génère le Modèle Conceptuel de Données (MCD — Merise) du projet
ElectioAnalytics · MSPR TPRE813 — Nouvelle-Aquitaine.

Sortie : public/data/charts/MCD_ElectioAnalytics.png

Exécution :
    python MSPR_Final/MSPR/03_Data_Science/generate_mcd.py
"""

import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT      = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT_PATH  = os.path.join(ROOT, "public", "data", "charts", "MCD_ElectioAnalytics.png")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

# ── Palette ───────────────────────────────────────────────────────────────────
BG        = "#0f1117"
CARD      = "#1a1d2e"
ENTITY_BG = "#1e2235"
ENTITY_BD = "#6366f1"
ASSOC_BG  = "#2d1f3d"
ASSOC_BD  = "#a78bfa"
TEXT      = "#e2e8f0"
MUTED     = "#94a3b8"
PRIMARY   = "#6366f1"
ACCENT    = "#a78bfa"
GREEN     = "#10b981"
AMBER     = "#f59e0b"
ROSE      = "#f43f5e"

# ── Entités (x_centre, y_centre, largeur, hauteur, nom, [attributs]) ──────────
ENTITIES = {
    "REGION": {
        "pos": (2.5, 13.5), "w": 3.8, "h": 2.2, "color": ENTITY_BD,
        "attrs": ["# code_region", "nom_region"],
    },
    "DEPARTEMENT": {
        "pos": (2.5, 10.0), "w": 3.8, "h": 2.4, "color": ENTITY_BD,
        "attrs": ["# code_departement", "nom_departement", "code_region (FK)"],
    },
    "CANTON": {
        "pos": (2.5, 6.5), "w": 3.8, "h": 2.4, "color": ENTITY_BD,
        "attrs": ["# code_canton", "nom_canton", "code_departement (FK)"],
    },
    "TERRITOIRE": {
        "pos": (2.5, 2.8), "w": 3.8, "h": 2.8, "color": ENTITY_BD,
        "attrs": ["# codgeo", "nom_commune", "code_canton (FK)", "superficie", "est_zone_urbaine"],
    },
    "ELECTION": {
        "pos": (9.5, 13.5), "w": 3.8, "h": 2.4, "color": GREEN,
        "attrs": ["# id_election", "annee", "tour", "type_election"],
    },
    "CANDIDAT": {
        "pos": (16.0, 13.5), "w": 3.8, "h": 2.4, "color": GREEN,
        "attrs": ["# id_candidat", "nom", "prenom", "orientation_politique"],
    },
    "RESULTAT_ELECTORAL": {
        "pos": (9.5, 9.5), "w": 4.2, "h": 3.6, "color": AMBER,
        "attrs": [
            "# id_resultat",
            "code_canton (FK)",
            "id_election (FK)",
            "id_candidat (FK)",
            "nb_inscrits",
            "nb_votants  /  nb_exprimes",
            "nb_voix",
            "pct_voix_ins  /  pct_voix_exp",
        ],
    },
    "INDICATEUR_SOCIONOM": {
        "pos": (9.5, 4.5), "w": 4.6, "h": 4.0, "color": ACCENT,
        "attrs": [
            "# id_indicateur",
            "codgeo (FK)",
            "annee_reference",
            "delta_population",
            "delta_emploi  /  delta_chomage",
            "delta_logement",
            "delta_entreprises (secteurs)",
            "score_eco_composite",
            "etat_economique",
            "target_ml",
        ],
    },
    "MODELE_ML": {
        "pos": (16.5, 7.5), "w": 4.0, "h": 3.2, "color": ROSE,
        "attrs": [
            "# id_modele",
            "nom_modele",
            "type_modele",
            "cv_accuracy  /  test_accuracy",
            "precision  /  recall  /  f1",
        ],
    },
    "PREDICTION": {
        "pos": (16.5, 2.8), "w": 4.0, "h": 3.2, "color": ROSE,
        "attrs": [
            "# id_prediction",
            "codgeo (FK)",
            "id_modele (FK)",
            "etat_eco_predit",
            "candidat_predit",
            "proba_macron  /  proba_lepen",
        ],
    },
    "TENDANCE_ELECTORALE": {
        "pos": (16.5, 12.5), "w": 4.2, "h": 3.6, "color": ROSE,
        "attrs": [
            "# id_tendance",
            "id_modele (FK)",
            "annee_base",
            "annee_prevision",
            "pct_extreme_gauche",
            "pct_gauche  /  pct_centre",
            "pct_droite  /  pct_extreme_droite",
            "confiance_modele",
        ],
    },
}

# ── Associations (nom, pos_centre, [(entite1, cote, card), (entite2, cote, card)]) ──
ASSOCIATIONS = [
    {
        "name": "CONTIENT",
        "pos": (2.5, 11.75),
        "links": [("REGION", "bottom", "1,1"), ("DEPARTEMENT", "top", "0,n")],
    },
    {
        "name": "CONTIENT",
        "pos": (2.5, 8.25),
        "links": [("DEPARTEMENT", "bottom", "1,1"), ("CANTON", "top", "0,n")],
    },
    {
        "name": "REGROUPE",
        "pos": (2.5, 4.65),
        "links": [("CANTON", "bottom", "1,1"), ("TERRITOIRE", "top", "0,n")],
    },
    {
        "name": "ENREGISTRE",
        "pos": (6.0, 9.5),
        "links": [("CANTON", "right", "1,1"), ("RESULTAT_ELECTORAL", "left", "0,n")],
    },
    {
        "name": "CONCERNE",
        "pos": (9.5, 11.75),
        "links": [("ELECTION", "bottom", "1,1"), ("RESULTAT_ELECTORAL", "top", "1,n")],
    },
    {
        "name": "OBTIENT",
        "pos": (13.0, 11.75),
        "links": [("CANDIDAT", "bottom", "0,n"), ("RESULTAT_ELECTORAL", "right", "1,n")],
    },
    {
        "name": "POSSEDE",
        "pos": (6.0, 4.5),
        "links": [("TERRITOIRE", "right", "1,1"), ("INDICATEUR_SOCIONOM", "left", "0,n")],
    },
    {
        "name": "EFFECTUE",
        "pos": (13.5, 5.5),
        "links": [("MODELE_ML", "left", "1,1"), ("INDICATEUR_SOCIONOM", "right", "1,n")],
    },
    {
        "name": "GENERE",
        "pos": (13.5, 2.8),
        "links": [("MODELE_ML", "bottom", "1,1"), ("PREDICTION", "left", "1,n")],
    },
    {
        "name": "PREVOIT",
        "pos": (13.5, 11.5),
        "links": [("MODELE_ML", "top", "1,1"), ("TENDANCE_ELECTORALE", "left", "0,n")],
    },
    {
        "name": "CONCERNE",
        "pos": (11.5, 2.8),
        "links": [("TERRITOIRE", "right", "1,1"), ("PREDICTION", "left", "0,n")],
    },
]


def entity_border(entity_name, side):
    """Retourne le point sur le bord d'une entité (pour les flèches)."""
    e = ENTITIES[entity_name]
    x, y = e["pos"]
    w, h  = e["w"], e["h"]
    if side == "top":    return (x, y + h / 2)
    if side == "bottom": return (x, y - h / 2)
    if side == "left":   return (x - w / 2, y)
    if side == "right":  return (x + w / 2, y)
    return (x, y)


def draw_entity(ax, name, info):
    x, y = info["pos"]
    w, h  = info["w"], info["h"]
    color = info["color"]
    attrs = info["attrs"]

    # Fond entité
    rect = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.08",
        linewidth=1.8, edgecolor=color,
        facecolor=ENTITY_BG, zorder=3,
    )
    ax.add_patch(rect)

    # Bande titre
    title_h = 0.45
    title_rect = FancyBboxPatch(
        (x - w / 2, y + h / 2 - title_h), w, title_h,
        boxstyle="round,pad=0.04",
        linewidth=0, edgecolor=color,
        facecolor=color, zorder=4, clip_on=True,
    )
    ax.add_patch(title_rect)

    # Nom entité
    display_name = name.replace("_SOCIONOM", "\nSOCIOÉCONOMIQUE")
    ax.text(x, y + h / 2 - title_h / 2, display_name,
            ha="center", va="center", fontsize=7.5, fontweight="bold",
            color="white", zorder=5)

    # Attributs
    n = len(attrs)
    if n > 0:
        step = (h - title_h - 0.15) / n
        for i, attr in enumerate(attrs):
            ay = y + h / 2 - title_h - 0.1 - step * (i + 0.5)
            style = "bold" if attr.startswith("#") else "normal"
            color_attr = AMBER if attr.startswith("#") else MUTED
            ax.text(x - w / 2 + 0.12, ay, attr.replace("# ", ""),
                    ha="left", va="center", fontsize=5.8,
                    color=color_attr, fontweight=style, zorder=5)


def draw_association(ax, assoc):
    ax_x, ax_y = assoc["pos"]
    name       = assoc["name"]

    # Losange
    diamond_w, diamond_h = 1.2, 0.5
    diamond = plt.Polygon(
        [(ax_x, ax_y + diamond_h),
         (ax_x + diamond_w / 2, ax_y),
         (ax_x, ax_y - diamond_h),
         (ax_x - diamond_w / 2, ax_y)],
        closed=True,
        linewidth=1.4, edgecolor=ASSOC_BD,
        facecolor=ASSOC_BG, zorder=3,
    )
    ax.add_patch(diamond)
    ax.text(ax_x, ax_y, name, ha="center", va="center",
            fontsize=5.5, color=ACCENT, fontweight="bold", zorder=4)

    # Flèches + cardinalités
    for ent_name, side, cardinality in assoc["links"]:
        bx, by = entity_border(ent_name, side)
        ax.annotate(
            "", xy=(bx, by), xytext=(ax_x, ax_y),
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.2),
            zorder=2,
        )
        # Cardinalité positionnée près de l'entité
        mx = bx + (ax_x - bx) * 0.22
        my = by + (ax_y - by) * 0.22
        ax.text(mx, my, cardinality, ha="center", va="center",
                fontsize=5.2, color=AMBER, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.1", facecolor=BG,
                          edgecolor="none", alpha=0.85), zorder=5)


def main():
    fig_w, fig_h = 22, 17
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 21)
    ax.set_ylim(0, 16.5)
    ax.axis("off")

    # Titre
    ax.text(10.5, 16.1,
            "MCD — ElectioAnalytics · MSPR TPRE813",
            ha="center", va="center",
            fontsize=14, fontweight="bold", color=TEXT)
    ax.text(10.5, 15.7,
            "Modèle Conceptuel de Données · Région Nouvelle-Aquitaine · Élection Présidentielle 2022",
            ha="center", va="center",
            fontsize=8, color=MUTED)

    # Légende couleurs
    legend_items = [
        (ENTITY_BD, "Entités géographiques"),
        (GREEN,     "Entités électorales"),
        (AMBER,     "Résultats / Indicateurs"),
        (ROSE,      "Modèles ML / Prédictions"),
    ]
    for i, (col, lbl) in enumerate(legend_items):
        lx = 1.2 + i * 4.8
        ax.add_patch(FancyBboxPatch((lx, 15.25), 0.35, 0.22,
                                    boxstyle="round,pad=0.02",
                                    facecolor=col, edgecolor="none"))
        ax.text(lx + 0.48, 15.36, lbl, va="center",
                fontsize=6.5, color=MUTED)

    # Dessin des associations (en premier pour passer derrière)
    for assoc in ASSOCIATIONS:
        draw_association(ax, assoc)

    # Dessin des entités
    for name, info in ENTITIES.items():
        draw_entity(ax, name, info)

    plt.tight_layout(pad=0.3)
    fig.savefig(OUT_PATH, dpi=180, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"[OK] MCD généré : {OUT_PATH}")


if __name__ == "__main__":
    main()
