"""
Fix notebook cell 5c560b4a: replace hardcoded first-column parsing
with actual column name detection for département and canton.
"""
import json, sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

nb_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "MSPR_Final", "MSPR", "03_Data_Science", "notebooks",
    "Nouvelle_Aquitaine_Machine_Learning.ipynb"
)

with open(nb_path, encoding='utf-8') as f:
    nb = json.load(f)

# New source for the geographic parsing block (replaces the old "Parser colonnes" block)
NEW_GEO_PARSE = """\
# ── Détection des colonnes géographiques dans le dataset réel ─────────────────
dept_col = next(
    (c for c in df_orig.columns if "partement" in c.lower() and "libell" in c.lower()),
    next((c for c in df_orig.columns
          if "departement" in c.lower() and "code" not in c.lower()), None)
)
canton_col = next(
    (c for c in df_orig.columns if "canton" in c.lower() and "libell" in c.lower()),
    None
)
# Fallback: utilise le code département si aucune colonne libellé trouvée
if dept_col is None and "code_departement" in df_orig.columns:
    dept_col = "code_departement"

if dept_col:
    df_orig["parsed_departement"] = df_orig[dept_col].apply(clean_name)
    print(f"  Colonne département détectée : '{dept_col}'")
if canton_col:
    df_orig["parsed_canton"] = df_orig[canton_col].apply(clean_name)
    print(f"  Colonne canton détectée     : '{canton_col}'")\
"""

OLD_BLOCK_START = "# ── Parser colonnes géographiques depuis la 1re colonne"
OLD_BLOCK_END   = "df_orig[\"parsed_canton\"]      = meta_df[canton_idx[0]].apply(clean_name)"

for cell in nb['cells']:
    if '5c560b4' not in cell.get('id', ''):
        continue

    src = ''.join(cell['source'])

    start_idx = src.find(OLD_BLOCK_START)
    if start_idx == -1:
        # Try ASCII version (in case of encoding mismatch in the file)
        OLD_BLOCK_START_ASCII = "# ── Parser colonnes g"
        start_idx = src.find(OLD_BLOCK_START_ASCII)
        if start_idx == -1:
            print("ERROR: could not find old geo-parse block in cell 5c560b4a")
            sys.exit(1)

    end_idx = src.find(OLD_BLOCK_END)
    if end_idx == -1:
        print("ERROR: could not find end marker of old geo-parse block")
        sys.exit(1)

    end_idx += len(OLD_BLOCK_END)
    # Include trailing newline if present
    if end_idx < len(src) and src[end_idx] == '\n':
        end_idx += 1

    new_src = src[:start_idx] + NEW_GEO_PARSE + "\n" + src[end_idx:]
    cell['source'] = [new_src]
    print("Cell 5c560b4a patched successfully.")
    break
else:
    print("ERROR: cell 5c560b4a not found in notebook")
    sys.exit(1)

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Notebook saved.")
