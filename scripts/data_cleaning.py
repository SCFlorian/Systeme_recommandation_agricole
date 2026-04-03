# ========================================================
# Nettoyage des fichiers à partir des fichiers consolidés
# ========================================================

# Imports
import pandas as pd
import numpy as np
import sys, os
import logging
# Chemin pour accèder aux éléments du projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Imports du projet
from scripts.config import (csv_yield_conso, csv_yield_enriched, csv_file_crop_yield_clean)
# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fichier yield_df_conso

def preparation_yield_df(df):
    """L'objectif ici est de partir du fichier consolidé pour préparer le fichier à la modélisation.
    On va renommer les variables et ensuite on va procéder au feature engineering"""
    # On remplace les noms pour être plus cohérent
    logging.info(f"Nombre de lignes et de colonnes sans modifs : {df.shape}\n")
    df['item'] = df['item'].replace({
        'Rice, paddy': 'Rice',
        'Soybeans': 'Soybean',
        'Maize': 'Maize',
        'Wheat': 'Wheat',
        'Barley': 'Barley'
        })
    logging.info(df['item'].unique())
    # Ajout des nouvelles variables
    # Flag de sécheresse (Binaire) 
    df['is_drought'] = (df['rainfall_mm'] < 200).astype(bool)
    # Déséquilibre intrants/eau (Ecart log)
    df['input_imbalance'] = np.abs(np.log1p(df['pesticides_tonnes']) - np.log1p(df['rainfall_mm']))
    # Stress thermique simple 
    df['thermal_stress'] = np.abs(df['avg_temp'] - 20)
    # On fixe l'année de référence 2016 pour l'interface future.
    year_ref = 2016
    # On crée un score de maturité technologique
    # Plus l'écart est grand, plus les semences et machines sont supposées performantes.
    df['years_from_now'] = year_ref - df['year']
    df = df.drop(columns={"area","year"}).copy()
    logging.info(f"Nombre de lignes et de colonnes après nouvelles variables et suppression de 2 colonnes : {df.shape}\n")
    # On détermine quels sont nos variables catégorielles et nos variables quantitatives
    num_cols = df.select_dtypes(include='number').columns
    cat_cols = df.select_dtypes(include=['object','bool']).columns
    logging.info(num_cols)
    logging.info(cat_cols)
    # Encodage One Hot des variables catégorielles
    df = pd.get_dummies(df, columns=cat_cols, dtype=float).copy()
    logging.info(f"Nombre de lignes et de colonnes après feature engineering {df.shape}")
    # Nettoyage du nom des variables pour uniformiser
    df = df.drop(columns={"Unnamed: 0"}).copy()
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    logging.info(df.head())
    logging.info(df.columns)
    df.to_csv("data/processed/yield_df_final_conso_encoded.csv")
    return df

def preparation_yield_enriched():
    """L'objectif ici est de partir du fichier enrichi pour préparer le fichier à la modélisation.
    On va renommer les variables et ensuite on va procéder au feature engineering"""
    # On charge le fichier
    try :
        df = pd.read_csv(csv_yield_enriched, index_col=0)
    except Exception as e:
        logging.error(f"Erreur critique lors du chargement du fichier : {e}")
        raise e
    logging.info(df.columns)
    # Ajout des nouvelles variables
    # Impact de l'irrigation
    df['irrigation_impact'] = df['Irrigation_Used'].astype(int) / (df['rainfall_mm'] + 1)
    # Flag de sécheresse (Binaire) 
    df['is_drought'] = (df['rainfall_mm'] < 200).astype(bool)
    # Déséquilibre intrants/eau (Ecart log)
    df['input_imbalance'] = np.abs(np.log1p(df['pesticides_tonnes']) - np.log1p(df['rainfall_mm']))
    # Stress thermique simple 
    df['thermal_stress'] = np.abs(df['avg_temp'] - 20)
    # On fixe l'année de référence 2016 pour l'interface future.
    year_ref = 2016
    # On crée un score de maturité technologique
    # Plus l'écart est grand, plus les semences et machines sont supposées performantes.
    df['years_from_now'] = year_ref - df['year']
    df = df.drop(columns={"area","year"}).copy()
    logging.info(f"Nombre de lignes et de colonnes après nouvelles variables et suppression de 2 colonnes : {df.shape}\n")
    # On détermine quels sont nos varibales catégorielles et nos variables quantitatives
    num_cols = df.select_dtypes(include='number').columns
    cat_cols = df.select_dtypes(include=['str','bool']).columns
    logging.info(num_cols)
    logging.info(cat_cols)
    # Encodage One Hot des variables catégorielles
    df = pd.get_dummies(df, columns=cat_cols, dtype=float).copy()
    logging.info(f"Nombre de lignes et de colonnes après feature engineering {df.shape}")
    # Nettoyage du nom des variables pour uniformiser
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    logging.info(df.head())
    logging.info(df.columns)
    df.to_csv("data/processed/yield_df_enriched_encoded.csv")

    return df

# Fichier crop_yield pour modélisation

def preparation_crop_yield():
    """Si jamais on décide de s'en servir pour un modèle, on le prépare à l'encodage"""
    # On charge le fichier
    try :
        df = pd.read_csv(csv_file_crop_yield_clean, index_col=0)
    except Exception as e:
        logging.error(f"Erreur critique lors du chargement du fichier : {e}")
        raise e
    logging.info(f"Nombre de lignes et de colonnes sans modifs : {df.shape}\n")
    # Ajout de deux nouvelles variables
    # Ratio climatique - indice d'irrigation critique
    df['irrigation_impact'] = df['Irrigation_Used'].astype(int) / (df['Rainfall_mm'] + 1)
    # Intensité du cycle
    df['growth_intensity'] = df['Temperature_Celsius'] / (df['Days_to_Harvest'] + 1)
    # On détermine quels sont nos varibales catégorielles et nos variables quantitatives
    num_cols = df.select_dtypes(include='number').columns
    cat_cols = df.select_dtypes(include=['object', 'string', 'bool']).columns
    # Encodage One Hot des variables catégorielles
    df = pd.get_dummies(df, columns=cat_cols, dtype=float).copy()
    logging.info(f"Nombre de lignes et de colonnes après feature engineering {df.shape}")
    # Nettoyage du nom des variables pour uniformiser
    df = df.rename(columns={"Yield_tons_per_hectare":"yield"}).copy()
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    logging.info(num_cols)
    logging.info(cat_cols)
    logging.info(df.columns)
    logging.info(df.shape)
    df.to_csv("data/processed/crop_yield_conso.csv")

    return df

def preparation_yield_df_inference(input_df: pd.DataFrame, expected_columns: list) -> pd.DataFrame:
    """Prépare une ou plusieurs lignes pour la prédiction API, avec le même feature engineering
    et le même encodage que pendant l'entraînement.
    """
    df = input_df.copy()

    df["item"] = df["item"].replace({
        "Rice, paddy": "Rice",
        "Soybeans": "Soybean",
        "Maize": "Maize",
        "Wheat": "Wheat",
        "Barley": "Barley"
    })

    # Flag de sécheresse
    df['is_drought'] = (df['rainfall_mm'] < 200).astype(bool)
    
    # Déséquilibre intrants/eau
    df['input_imbalance'] = np.abs(np.log1p(df['pesticides_tonnes']) - np.log1p(df['rainfall_mm']))
    
    # Stress thermique
    df['thermal_stress'] = np.abs(df['avg_temp'] - 20)
    
    # Année de référence
    year_ref = 2016
    target_year = df['year'] if 'year' in df.columns else year_ref
    df['years_from_now'] = year_ref - target_year

    df = df.drop(columns=["area", "year"], errors="ignore").copy()

    cat_cols = df.select_dtypes(include=["object", "string", "bool"]).columns
    df = pd.get_dummies(df, columns=cat_cols, dtype=float).copy()

    df.columns = df.columns.str.lower().str.replace(" ", "_")

    for col in expected_columns:
        if col not in df.columns:
            df[col] = 0.0

    df = df[expected_columns].copy()

    return df
