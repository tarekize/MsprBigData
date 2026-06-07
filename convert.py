import json
import os

def convert_py_to_ipynb(py_file, ipynb_file):
    with open(py_file, 'r', encoding='utf-8') as f:
        code = f.read()

    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [line + '\n' for line in code.split('\n')[:-1]] + [code.split('\n')[-1]]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.12.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    # Write notebook
    with open(ipynb_file, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2)

    print(f"Updated {ipynb_file}")

# Paths
prep_py = "C:/Users/tarek/Downloads/economic-pulse-analyzer/MSPR_Final/MSPR/02_Data_Engineering/run_prep.py"
prep_ipynb = "C:/Users/tarek/Downloads/economic-pulse-analyzer/MSPR_Final/MSPR/02_Data_Engineering/notebooks/Nouvelle_Aquitaine_Data_Preparation.ipynb"

ml_py = "C:/Users/tarek/Downloads/economic-pulse-analyzer/ml/notebooks/run_all.py"
ml_ipynb = "C:/Users/tarek/Downloads/economic-pulse-analyzer/ml/notebooks/Nouvelle_Aquitaine_ML.ipynb"

# Run conversion
convert_py_to_ipynb(prep_py, prep_ipynb)
convert_py_to_ipynb(ml_py, ml_ipynb)
