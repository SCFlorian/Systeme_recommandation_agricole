# ======================================
# NETTOYAGE DU FICHIER "crop_yield.csv"
# ======================================

# Imports
import pandas as pd
import sys, os
import logging
# Chemin pour accèder aux éléments du projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Imports du projet
from scripts.config import csv_file_model
# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fonction de nettoyage du fichier principal
def cleaning_df():
    """On prépare notre dataframe principal pour la modélisation"""
    df = pd.read_csv(csv_file_model)
    # On enlève les valeurs extrêmes (les rendements négatifs non explicables)
    df_clean = df[df["Yield_tons_per_hectare"]>=0]
    return df_clean
# Affichage du nouveau fichier
df = cleaning_df()
logging.info(df.head())
logging.info(f"\nNombre de lignes et de colonnes : {df.shape}")

def preparation_modelisation():
    """ Encodage des variables non numériques"""
    

