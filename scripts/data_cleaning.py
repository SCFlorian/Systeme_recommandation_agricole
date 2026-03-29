# ========================================================
# Nettoyage des fichiers à partir des fichiers consolidés
# ========================================================

# Imports
import pandas as pd
import sys, os
import logging
# Chemin pour accèder aux éléments du projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Imports du projet
from scripts.config import (csv_yield_conso, csv_yield_enriched)
# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fichier yield_df_conso

def preparation_yield_df():
    """L'objectif ici est de partir du fichier consolidé pour préparer le fichier à la modélisation.
    On va renommer les variables et ensuite on va procéder au feature engineering"""
    # On charge le fichier
    try :
        df = pd.read_csv(csv_yield_conso, index_col=0)
    except Exception as e:
        logging.error(f"Erreur critique lors du chargement du fichier : {e}")
        raise e
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
    # Progrès technique
    df['tech_trend'] = df['year'] - df['year'].min()
    # Écart-type de la température par pays (mesure de l'instabilité)
    df['climate_instability'] = df.groupby('area')['avg_temp'].transform('std')
    # Le relative tech-age
    avg_pest_country = df.groupby('area')['pesticides_tonnes'].transform('mean')
    df['relative_tech_intensity'] = df['pesticides_tonnes'] / (avg_pest_country + 1)
    # Suppression de l'année et de l'area
    df = df.drop(columns={"year","area"}).copy()
    logging.info(f"Nombre de lignes et de colonnes après nouvelles variables et suppression de 2 colonnes : {df.shape}\n")
    # On détermine quels sont nos varibales catégorielles et nos variables quantitatives
    num_cols = df.select_dtypes(include='number').columns
    cat_cols = df.select_dtypes(include='str').columns
    logging.info(num_cols)
    logging.info(cat_cols)
    # Encodage One Hot des variables catégorielles
    df = pd.get_dummies(df, columns=cat_cols, dtype=float).copy()
    logging.info(f"Nombre de lignes et de colonnes après feature engineering {df.shape}")
    # Nettoyage du nom des variables pour uniformiser
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    logging.info(df.head())
    logging.info(df.columns)
    return df

# Fichier crop_yield

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
    # Progrès technique
    df['tech_trend'] = df['year'] - df['year'].min()
    # Ratio climatique - indice d'irrigation critique
    df['irrigation_impact'] = df['Irrigation_Used'].astype(int) / (df['rainfall_mm'] + 1)
    # Écart-type de la température par pays (mesure de l'instabilité)
    df['climate_instability'] = df.groupby('area')['avg_temp'].transform('std')
    # Le relative tech-age
    avg_pest_country = df.groupby('area')['pesticides_tonnes'].transform('mean')
    df['relative_tech_intensity'] = df['pesticides_tonnes'] / (avg_pest_country + 1)
    # Suppression de l'année et de l'area
    df = df.drop(columns={"year","area"}).copy()
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

    return df

