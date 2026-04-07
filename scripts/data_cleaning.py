# ==========================================================================
# Nettoyage des fichiers à partir des fichiers consolidés (après imputation)
# ==========================================================================

import pandas as pd
import numpy as np
import sys, os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import (csv_yield_conso, csv_yield_enriched, csv_file_crop_yield_clean)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Les 2 fonctions suivantes corrrespondent à la préparation du fichier avant encodage et séparation du split X,y
def preparation_yield_df(df):
    """Prépare le fichier consolidé non enrichi pour la modélisation."""
    logging.info(f"Nombre de lignes et de colonnes sans modifs : {df.shape}\n")

    df = df.copy()

    df['item'] = df['item'].replace({
        'Rice, paddy': 'Rice',
        'Soybeans': 'Soybean',
        'Maize': 'Maize',
        'Wheat': 'Wheat',
        'Barley': 'Barley'
    })

    logging.info(df['item'].unique())

    # On enlève les valeurs à 0
    df = df.loc[df['yield'] > 0].copy()

    df['is_drought'] = (df['rainfall_mm'] < 200).astype(bool)
    df['input_imbalance'] = np.abs(np.log1p(df['pesticides_tonnes']) - np.log1p(df['rainfall_mm']))
    df['thermal_stress'] = np.abs(df['avg_temp'] - 20)

    year_ref = 2016
    df['years_from_now'] = year_ref - df['year']

    # Nettoyage avant détection des types
    df = df.drop(columns=["area", "year", "Unnamed: 0"], errors="ignore").copy()

    logging.info(f"Nombre de lignes et de colonnes après feature engineering : {df.shape}\n")

    num_cols = df.select_dtypes(include=['number']).columns
    cat_cols = df.select_dtypes(include=['object', 'string', 'bool']).columns

    logging.info(num_cols)
    logging.info(cat_cols)

    df.columns = df.columns.str.lower().str.replace(" ", "_")
    logging.info(df.head())
    logging.info(df.columns)

    # Sauveragrde du fichier
    df.to_csv("data/processed/yield_df_final_conso.csv", index=False)

    return df

def preparation_yield_enriched(df):
    """Prépare le fichier enrichi pour la modélisation."""
    logging.info(f"Nombre de lignes et de colonnes sans modifs : {df.shape}\n")

    df = df.copy()

    df['item'] = df['item'].replace({
        'Rice, paddy': 'Rice',
        'Soybeans': 'Soybean',
        'Maize': 'Maize',
        'Wheat': 'Wheat',
        'Barley': 'Barley'
    })

    logging.info(df['item'].unique())

    # On enlève les valeurs à 0
    df = df.loc[df['yield'] > 0].copy()

    df['is_drought'] = (df['rainfall_mm'] < 200).astype(bool)
    df['input_imbalance'] = np.abs(np.log1p(df['pesticides_tonnes']) - np.log1p(df['rainfall_mm']))
    df['thermal_stress'] = np.abs(df['avg_temp'] - 20)

    year_ref = 2016
    df['years_from_now'] = year_ref - df['year']

    # Nettoyage avant détection des types
    df = df.drop(columns=["area", "year", "Unnamed: 0"], errors="ignore").copy()

    logging.info(f"Nombre de lignes et de colonnes après feature engineering : {df.shape}\n")

    num_cols = df.select_dtypes(include=['number']).columns
    cat_cols = df.select_dtypes(include=['object', 'string', 'bool']).columns

    logging.info(num_cols)
    logging.info(cat_cols)

    df.columns = df.columns.str.lower().str.replace(" ", "_")
    logging.info(df.head())
    logging.info(df.columns)

    # Sauvegarde du fichier
    df.to_csv("data/processed/yield_df_enriched_conso.csv", index=False)

    return df

# Fonction dédiée au modèle lors que l'API va refaire l'ensemble des traitement 
def preparation_yield_df_inference(input_df: pd.DataFrame) -> pd.DataFrame:
    """Prépare une ou plusieurs lignes pour la prédiction API
    avec le même feature engineering qu'à l'entraînement.
    L'encodage sera géré ensuite par le pipeline.
    """
    df = input_df.copy()

    df["item"] = df["item"].replace({
        "Rice, paddy": "Rice",
        "Soybeans": "Soybean",
        "Maize": "Maize",
        "Wheat": "Wheat",
        "Barley": "Barley"
    })
    df['is_drought'] = (df['rainfall_mm'] < 200).astype(bool)
    df['input_imbalance'] = np.abs(np.log1p(df['pesticides_tonnes']) - np.log1p(df['rainfall_mm']))
    df['thermal_stress'] = np.abs(df['avg_temp'] - 20)

    year_ref = 2016
    target_year = df['year'] if 'year' in df.columns else year_ref
    df['years_from_now'] = year_ref - target_year

    df = df.drop(columns=["area", "year", "Unnamed: 0"], errors="ignore").copy()
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    return df