import json

with open("notebooks/Nouvelle_Aquitaine_Data_Preparation.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

with open("run_prep.py", "w", encoding="utf-8") as f:
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            # Comment out ipython magic commands
            source = "\n".join([line if not line.strip().startswith("!") else f"# {line}" for line in source.split("\n")])
            f.write(source + "\n\n")
