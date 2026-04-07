# ========================================================
# Nettoyage des fichiers à partir des fichiers consolidés
# ========================================================

import pandas as pd
import numpy as np
import sys, os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import (csv_yield_conso, csv_yield_enriched, csv_file_crop_yield_clean)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def preparation_yield_df(df):
    """Prépare le fichier consolidé pour la modélisation."""
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

    # Optionnel si tu veux conserver ce filtre
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

    # Le nom de fichier devrait refléter qu'il n'est plus encodé
    df.to_csv("data/processed/yield_df_final_conso_ready.csv", index=False)

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

    # Optionnel si tu veux conserver ce filtre
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

    # Le nom de fichier devrait refléter qu'il n'est plus encodé
    df.to_csv("data/processed/yield_df_enriched_ready.csv", index=False)

    return df

df = pd.read_csv("data/processed/yield_df_enriched.csv")
df = preparation_yield_enriched(df)

def preparation_crop_yield():
    """Préparation du fichier crop_yield pour modélisation."""
    try:
        df = pd.read_csv(csv_file_crop_yield_clean, index_col=0)
    except Exception as e:
        logging.error(f"Erreur critique lors du chargement du fichier : {e}")
        raise e

    logging.info(f"Nombre de lignes et de colonnes sans modifs : {df.shape}\n")

    df['irrigation_impact'] = df['Irrigation_Used'].astype(int) / (df['Rainfall_mm'] + 1)
    df['growth_intensity'] = df['Temperature_Celsius'] / (df['Days_to_Harvest'] + 1)

    df = df.drop(columns=["Unnamed: 0"], errors="ignore").copy()

    num_cols = df.select_dtypes(include=['number']).columns
    cat_cols = df.select_dtypes(include=['object', 'string', 'bool']).columns

    df = df.rename(columns={"Yield_tons_per_hectare": "yield"}).copy()
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    logging.info(num_cols)
    logging.info(cat_cols)
    logging.info(df.columns)
    logging.info(df.shape)

    df.to_csv("data/processed/crop_yield_ready.csv", index=False)

    return df


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