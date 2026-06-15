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
from matplotlib.patches import FancyBboxPatch

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT     = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT_PATH = os.path.join(ROOT, "public", "data", "charts", "MCD_ElectioAnalytics.png")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

# ── Palette ───────────────────────────────────────────────────────────────────
BG        = "#0f1117"
ENTITY_BG = "#1a1d2e"
TEXT      = "#e2e8f0"
MUTED     = "#94a3b8"
AMBER     = "#f59e0b"

C_GEO   = "#6366f1"   # entités géographiques  — bleu/violet
C_ELEC  = "#10b981"   # entités électorales    — vert
C_DATA  = "#f59e0b"   # données / indicateurs  — ambre
C_ML    = "#f43f5e"   # ML / prédictions       — rose
C_ASSOC = "#a78bfa"   # associations           — violet clair

# ──────────────────────────────────────────────────────────────────────────────
# LAYOUT — 4 colonnes bien séparées
#
#  Col A  x=2.8   : REGION → DEPARTEMENT → CANTON → TERRITOIRE
#  Col B  x=10.0  : ELECTION → RESULTAT_ELECTORAL → INDICATEUR_SOCIONOM
#  Col C  x=17.2  : CANDIDAT → MODELE_ML → PREDICTION
#  Col D  x=24.5  : TENDANCE_ELECTORALE (seule, reliée à MODELE_ML)
# ──────────────────────────────────────────────────────────────────────────────

ENTITIES = {
    # ── Col A : géographie ────────────────────────────────────────────────────
    "REGION": {
        "pos": (2.8, 15.2), "w": 4.0, "h": 2.0, "color": C_GEO,
        "attrs": ["# code_region", "nom_region"],
    },
    "DEPARTEMENT": {
        "pos": (2.8, 11.6), "w": 4.0, "h": 2.4, "color": C_GEO,
        "attrs": ["# code_departement", "nom_departement", "code_region (FK)"],
    },
    "CANTON": {
        "pos": (2.8, 7.8), "w": 4.0, "h": 2.4, "color": C_GEO,
        "attrs": ["# code_canton", "nom_canton", "code_departement (FK)"],
    },
    "TERRITOIRE": {
        "pos": (2.8, 3.6), "w": 4.0, "h": 3.0, "color": C_GEO,
        "attrs": [
            "# codgeo",
            "nom_commune",
            "code_canton (FK)",
            "superficie",
            "est_zone_urbaine",
        ],
    },
    # ── Col B : électoral + indicateurs ──────────────────────────────────────
    "ELECTION": {
        "pos": (10.0, 15.2), "w": 4.2, "h": 2.4, "color": C_ELEC,
        "attrs": ["# id_election", "annee", "tour", "type_election"],
    },
    "RESULTAT_ELECTORAL": {
        "pos": (10.0, 10.2), "w": 4.4, "h": 3.8, "color": C_DATA,
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
        "pos": (10.0, 4.5), "w": 4.6, "h": 4.2, "color": C_DATA,
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
    # ── Col C : candidat + ML ─────────────────────────────────────────────────
    "CANDIDAT": {
        "pos": (17.2, 15.2), "w": 4.2, "h": 2.4, "color": C_ELEC,
        "attrs": ["# id_candidat", "nom", "prenom", "orientation_politique"],
    },
    "MODELE_ML": {
        "pos": (17.2, 9.5), "w": 4.2, "h": 3.2, "color": C_ML,
        "attrs": [
            "# id_modele",
            "nom_modele",
            "type_modele",
            "cv_accuracy  /  test_accuracy",
            "precision  /  recall  /  f1",
        ],
    },
    "PREDICTION": {
        "pos": (17.2, 4.0), "w": 4.2, "h": 3.4, "color": C_ML,
        "attrs": [
            "# id_prediction",
            "codgeo (FK)",
            "id_modele (FK)",
            "etat_eco_predit",
            "candidat_predit",
            "proba_macron  /  proba_lepen",
        ],
    },
    # ── Col D : tendances ─────────────────────────────────────────────────────
    "TENDANCE_ELECTORALE": {
        "pos": (24.5, 9.5), "w": 4.6, "h": 4.4, "color": C_ML,
        "attrs": [
            "# id_tendance",
            "id_modele (FK)",
            "annee_base",
            "annee_prevision",
            "pct_extreme_gauche",
            "pct_gauche",
            "pct_centre",
            "pct_droite  /  pct_extreme_droite",
            "confiance_modele",
        ],
    },
}

# ── Associations ──────────────────────────────────────────────────────────────
ASSOCIATIONS = [
    # Hiérarchie géographique (col A, entre entités)
    {
        "name": "CONTIENT",
        "pos": (2.8, 13.4),
        "links": [("REGION", "bottom", "1,1"), ("DEPARTEMENT", "top", "0,n")],
    },
    {
        "name": "CONTIENT",
        "pos": (2.8, 9.7),
        "links": [("DEPARTEMENT", "bottom", "1,1"), ("CANTON", "top", "0,n")],
    },
    {
        "name": "REGROUPE",
        "pos": (2.8, 5.8),
        "links": [("CANTON", "bottom", "1,1"), ("TERRITOIRE", "top", "0,n")],
    },
    # Canton → RESULTAT_ELECTORAL (col A→B)
    {
        "name": "ENREGISTRE",
        "pos": (6.6, 9.5),
        "links": [("CANTON", "right", "1,1"), ("RESULTAT_ELECTORAL", "left", "0,n")],
    },
    # Élection → RESULTAT_ELECTORAL (col B interne)
    {
        "name": "CONCERNE",
        "pos": (10.0, 13.1),
        "links": [("ELECTION", "bottom", "1,1"), ("RESULTAT_ELECTORAL", "top", "1,n")],
    },
    # Candidat → RESULTAT_ELECTORAL (col C→B)
    {
        "name": "OBTIENT",
        "pos": (13.6, 12.0),
        "links": [("CANDIDAT", "bottom", "0,n"), ("RESULTAT_ELECTORAL", "right", "1,n")],
    },
    # Territoire → INDICATEUR (col A→B)
    {
        "name": "POSSEDE",
        "pos": (6.6, 4.5),
        "links": [("TERRITOIRE", "right", "1,1"), ("INDICATEUR_SOCIONOM", "left", "0,n")],
    },
    # INDICATEUR → MODELE_ML (col B→C)
    {
        "name": "ENTRAINE",
        "pos": (13.8, 6.8),
        "links": [("INDICATEUR_SOCIONOM", "right", "1,n"), ("MODELE_ML", "left", "1,1")],
    },
    # MODELE_ML → PREDICTION (col C interne)
    {
        "name": "GENERE",
        "pos": (17.2, 6.9),
        "links": [("MODELE_ML", "bottom", "1,1"), ("PREDICTION", "top", "1,n")],
    },
    # Territoire → PREDICTION (col A→C, bas)
    {
        "name": "CONCERNE",
        "pos": (10.5, 2.5),
        "links": [("TERRITOIRE", "bottom", "1,1"), ("PREDICTION", "bottom", "0,n")],
    },
    # MODELE_ML → TENDANCE_ELECTORALE (col C→D)
    {
        "name": "PREVOIT",
        "pos": (21.0, 9.5),
        "links": [("MODELE_ML", "right", "1,1"), ("TENDANCE_ELECTORALE", "left", "0,n")],
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def entity_border(name, side):
    e = ENTITIES[name]
    x, y, w, h = e["pos"][0], e["pos"][1], e["w"], e["h"]
    if side == "top":    return (x,          y + h / 2)
    if side == "bottom": return (x,          y - h / 2)
    if side == "left":   return (x - w / 2,  y)
    if side == "right":  return (x + w / 2,  y)
    return (x, y)


def draw_entity(ax, name, info):
    x, y   = info["pos"]
    w, h   = info["w"], info["h"]
    color  = info["color"]
    attrs  = info["attrs"]
    TITLE_H = 0.48

    # Corps
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.07",
        linewidth=2.0, edgecolor=color,
        facecolor=ENTITY_BG, zorder=3,
    ))
    # Bandeau titre
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y + h / 2 - TITLE_H), w, TITLE_H,
        boxstyle="square,pad=0.0",
        linewidth=0, edgecolor="none",
        facecolor=color, zorder=4, clip_on=True,
    ))
    # Nom
    display = name.replace("_SOCIONOM", "\nSOCIOÉCONOMIQUE")
    ax.text(x, y + h / 2 - TITLE_H / 2, display,
            ha="center", va="center", fontsize=7.5, fontweight="bold",
            color="white", zorder=5)
    # Attributs
    n = len(attrs)
    if n:
        step = (h - TITLE_H - 0.12) / n
        for i, attr in enumerate(attrs):
            ay = y + h / 2 - TITLE_H - 0.08 - step * (i + 0.5)
            is_pk = attr.startswith("#")
            ax.text(x - w / 2 + 0.14, ay,
                    attr.replace("# ", ""),
                    ha="left", va="center",
                    fontsize=5.8,
                    color=AMBER if is_pk else MUTED,
                    fontweight="bold" if is_pk else "normal",
                    zorder=5)


def draw_association(ax, assoc):
    ax_x, ax_y = assoc["pos"]
    name       = assoc["name"]
    dw, dh     = 1.3, 0.52

    # Losange
    diamond = plt.Polygon(
        [(ax_x,           ax_y + dh),
         (ax_x + dw / 2,  ax_y),
         (ax_x,           ax_y - dh),
         (ax_x - dw / 2,  ax_y)],
        closed=True,
        linewidth=1.5, edgecolor=C_ASSOC,
        facecolor="#2d1f3d", zorder=6,
    )
    ax.add_patch(diamond)
    ax.text(ax_x, ax_y, name,
            ha="center", va="center",
            fontsize=5.5, color=C_ASSOC, fontweight="bold", zorder=7)

    # Traits + cardinalités
    for ent_name, side, card in assoc["links"]:
        bx, by = entity_border(ent_name, side)
        ax.plot([ax_x, bx], [ax_y, by], color=MUTED, lw=1.1, zorder=2)
        # Cardinalité à 20 % du chemin vers l'entité
        cx = bx + (ax_x - bx) * 0.20
        cy = by + (ax_y - by) * 0.20
        ax.text(cx, cy, card,
                ha="center", va="center",
                fontsize=5.4, color=AMBER, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.08", facecolor=BG,
                          edgecolor="none", alpha=0.9),
                zorder=8)


def main():
    FIG_W, FIG_H = 30, 18
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 28)
    ax.set_ylim(0, 17.5)
    ax.axis("off")

    # ── Titre principal ───────────────────────────────────────────────────────
    ax.text(14.0, 17.1,
            "MCD — ElectioAnalytics · MSPR TPRE813",
            ha="center", va="center",
            fontsize=15, fontweight="bold", color=TEXT)
    ax.text(14.0, 16.65,
            "Modèle Conceptuel de Données · Région Nouvelle-Aquitaine · Élection Présidentielle 2022",
            ha="center", va="center",
            fontsize=8.5, color=MUTED)

    # ── Légende ───────────────────────────────────────────────────────────────
    legend = [
        (C_GEO,  "Entités géographiques"),
        (C_ELEC, "Entités électorales"),
        (C_DATA, "Résultats / Indicateurs"),
        (C_ML,   "Modèles ML / Prédictions"),
    ]
    for i, (col, lbl) in enumerate(legend):
        lx = 2.5 + i * 6.0
        ax.add_patch(FancyBboxPatch((lx, 16.1), 0.38, 0.25,
                                    boxstyle="round,pad=0.02",
                                    facecolor=col, edgecolor="none", zorder=3))
        ax.text(lx + 0.55, 16.22, lbl,
                va="center", fontsize=7.0, color=MUTED)

    # ── En-têtes colonnes ─────────────────────────────────────────────────────
    for cx, label in [
        (2.8,  "Géographie"),
        (10.0, "Electoral / Indicateurs"),
        (17.2, "Candidat / ML"),
        (24.5, "Prévisions"),
    ]:
        ax.text(cx, 16.6, label,
                ha="center", va="center",
                fontsize=7.5, color=MUTED,
                style="italic")
        ax.plot([cx - 2.0, cx + 2.0], [16.45, 16.45],
                color=MUTED, lw=0.5, alpha=0.3)

    # ── Séparateurs verticaux légers ──────────────────────────────────────────
    for sx in [6.4, 13.6, 20.8]:
        ax.plot([sx, sx], [0.5, 16.3],
                color=MUTED, lw=0.4, alpha=0.15, linestyle="--")

    # ── Dessin (associations d'abord, entités par-dessus) ─────────────────────
    for assoc in ASSOCIATIONS:
        draw_association(ax, assoc)
    for name, info in ENTITIES.items():
        draw_entity(ax, name, info)

    plt.tight_layout(pad=0.2)
    fig.savefig(OUT_PATH, dpi=180, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"[OK] MCD généré : {OUT_PATH}")


if __name__ == "__main__":
    main()
