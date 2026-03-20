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


import pandas as pd
import numpy as np
import logging
import sys, os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# 1. CONFIGURATION DU LOGGING
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Chemin pour accéder aux éléments du projet (selon ta structure)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scripts.config import csv_file_model
except ImportError:
    # Si tu lances le script en dehors de ton architecture habituelle
    csv_file_model = "crop_yield.csv" 

# 2. TES FONCTIONS DE NETTOYAGE
def cleaning_df():
    """Nettoyage des données"""
    df = pd.read_csv(csv_file_model)
    df_clean = df[df["Yield_tons_per_hectare"] >= 0]
    return df_clean

def preparation_modelisation(df_clean):
    """Encodage des variables"""
    df_encoded = pd.get_dummies(df_clean, columns=['Region','Soil_Type','Crop','Weather_Condition'], dtype=int)
    df_encoded['Fertilizer_Used'] = df_encoded['Fertilizer_Used'].astype(int)
    df_encoded['Irrigation_Used'] = df_encoded['Irrigation_Used'].astype(int)
    return df_encoded

# 3. FONCTION D'ENTRAÎNEMENT GLOBAL
def entrainement_global(df_encoded):
    # Séparation X et y
    X = df_encoded.drop(columns=['Yield_tons_per_hectare'])
    y = df_encoded['Yield_tons_per_hectare']

    # Split Train/Test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Standardisation
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Liste des modèles
    modeles = {
        "Régression Linéaire": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    }

    logging.info("\n" + "="*60)
    logging.info(f"{'MODÈLE':<25} | {'R² TEST':<10} | {'MAE':<10}")
    logging.info("-" * 60)

    for nom, model in modeles.items():
        # Entraînement
        model.fit(X_train_scaled, y_train)
        # Prédictions
        y_pred = model.predict(X_test_scaled)
        # Métriques
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        logging.info(f"{nom:<25} | {r2:<10.4f} | {mae:<10.2f} t/ha")

    # Diagnostic Overfitting sur le meilleur (souvent XGBoost ou RF)
    cv_scores = cross_val_score(modeles["XGBoost"], X_train_scaled, y_train, cv=5)
    logging.info("-" * 60)
    logging.info(f"Stabilité XGBoost (Cross-Val) : {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    logging.info("="*60 + "\n")

    return modeles, scaler

# 4. LE BOUTON "START" (Indispensable pour que ça tourne)
if __name__ == "__main__":
    logging.info("Lancement du pipeline d'entraînement...")
    
    # Étape 1 : Nettoyage
    data_propre = cleaning_df()
    
    # Étape 2 : Encodage
    data_prete = preparation_modelisation(data_propre)
    
    # Étape 3 : Comparaison des modèles
    modeles_entraines, mon_scaler = entrainement_global(data_prete)