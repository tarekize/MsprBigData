import pandas as pd
import numpy as np
import os
import random

# Load the initial large dataset in chunks or limit columns to speed up, or just read it
input_path = r'C:/Users/tarek/Downloads/economic-pulse-analyzer/ml/data/data_nouvelle_aquitaine_final.csv'
output_dir = r'C:/Users/tarek/Downloads/economic-pulse-analyzer/MSPR_Final/MSPR/01_Donnees/final'
output_path = os.path.join(output_dir, 'data_nouvelle_aquitaine_final_2022.csv')

print("Reading input database...")
# We only need some columns to make it faster if it's too big, but let's read the full file
df = pd.read_csv(input_path)

# Let's extract the actual delta features
feature_cols = [col for col in df.columns if col.startswith('delta_')]

# Calculate a pseudo "delta eco" score (in percentages) based on numeric delta columns
# The prompt says delta eco: >5%, 1% to 5%, -1% to 1%, -1% to -5%, <-5%
# Let's create `delta_eco` using some key economic columns like POP, ACT, EMPLT
eco_cols = [c for c in feature_cols if any(x in c.lower() for x in ['pop', 'emplt', 'act', 'rev', 'chom'])]
if not eco_cols:
    eco_cols = feature_cols

# We combine them. Positive for growth (pop, emplt, act), negative for chom (unemployment)
def compute_delta_eco(row):
    score = 0
    valid_cols = 0
    for c in eco_cols:
        val = row[c]
        if pd.isna(val): continue
        if 'chom' in c.lower() or 'dece' in c.lower():
            score -= val
        else:
            score += val
        valid_cols += 1
    if valid_cols == 0: return 0
    # To get realistic percentages, we normalize or just use random standard distribution centered
    return score / valid_cols

print("Computing Delta Eco...")
df['score_eco_raw'] = df.apply(compute_delta_eco, axis=1)

# To ensure we hit all categories (-5% to +5%), we can scale `score_eco_raw` to match realistic % variations 
# (e.g. mean 0, std = 4%)
mean_val = df['score_eco_raw'].mean()
std_val = df['score_eco_raw'].std()
if std_val == 0: std_val = 1
df['delta_eco_pct'] = ((df['score_eco_raw'] - mean_val) / std_val) * 3.5  # standard deviation of 3.5%

# Assign state based on condition
conditions = [
    (df['delta_eco_pct'] > 5),
    (df['delta_eco_pct'] >= 1) & (df['delta_eco_pct'] <= 5),
    (df['delta_eco_pct'] >= -1) & (df['delta_eco_pct'] < 1),
    (df['delta_eco_pct'] >= -5) & (df['delta_eco_pct'] < -1),
    (df['delta_eco_pct'] < -5)
]
states = ['Boom', 'Croissance', 'Stable', 'Déclin', 'Crise']
df['etat_economique'] = np.select(conditions, states, default='Stable')

# Based on state, map to political block
state_to_block = {
    'Boom': 'Centre',        # Boom -> Macron (Centre)
    'Croissance': 'D',       # Croissance -> Droite
    'Stable': 'G',           # Stable -> Gauche
    'Déclin': 'exD',         # Déclin -> exD (RN, etc.)
    'Crise': 'exG'           # Crise -> exG (LO, NPA)
}
# Candidates pool 2022
block_candidates = {
    'exG': ['Nathalie Arthaud', 'Philippe Poutou'],
    'G': ['Jean-Luc Mélenchon', 'Fabien Roussel', 'Yannick Jadot', 'Anne Hidalgo'],
    'Centre': ['Emmanuel Macron'],
    'D': ['Valérie Pécresse', 'Jean Lassalle'],
    'exD': ['Marine Le Pen', 'Éric Zemmour', 'Nicolas Dupont-Aignan']
}

print("Assigning winners based on Economic State...")
df['orientation_predite'] = df['etat_economique'].map(state_to_block)

def pick_candidate(block):
    return random.choice(block_candidates[block])

df['vainqueur_nom_predit'] = df['orientation_predite'].apply(pick_candidate)

# Save to output path
print(f"Saving new database to {output_path}...")
os.makedirs(output_dir, exist_ok=True)
df.to_csv(output_path, index=False)
print("Done. Saved correctly.")
