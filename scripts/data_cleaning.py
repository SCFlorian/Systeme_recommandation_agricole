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
    logging.info(f"\nNombre de lignes et de colonnes sans modifs : {df.shape}\n")
    # On enlève les valeurs extrêmes (les rendements négatifs non explicables)
    df_clean = df[df["Yield_tons_per_hectare"]>=0]
    return df_clean
# Affichage du nouveau fichier
df_clean = cleaning_df()
logging.info(df_clean.head())
logging.info(f"\nNombre de lignes et de colonne aprés suppression : {df_clean.shape}")

def preparation_modelisation(df_clean):
    """ Encodage des variables non numériques"""
    df = df_clean
    # Encodage des variables qualitatives avec la technique One Hot
    df_encoded = pd.get_dummies(df, columns=['Region','Soil_Type','Crop','Weather_Condition'], dtype=int)
    # True et False des variables Fertilizer_Used et Irrigation_Used en catégorie 0 et 1
    df_encoded['Fertilizer_Used'] = df_encoded['Fertilizer_Used'].astype(int)
    df_encoded['Irrigation_Used'] = df_encoded['Irrigation_Used'].astype(int)
    logging.info(f"\nNombre de lignes et de colonnes avec modifs : {df_encoded.shape}\n")
    return df_encoded

df_encoded = preparation_modelisation(df_clean)



