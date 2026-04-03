# ====================================================
# Configuration du système de recommandation agricole
# ====================================================

# Chargement des fichiers csv
csv_file_crop_yield = "data/raw/crop_yield.csv"
csv_yield_conso = "data/processed/yield_df_final.csv"
csv_file_crop_yield_clean = "data/processed/crop_yield.csv"
csv_mapping_countries = "data/processed/harmonization_data/country_standardization_mapping.csv"
csv_pesticides = "data/raw/pesticides.csv"
csv_rainfall = "data/raw/rainfall.csv"
csv_temp = "data/raw/temp.csv"
csv_yield = "data/raw/yield.csv"
csv_yield_enriched = "data/processed/yield_df_enriched.csv"
csv_yield_conso_encoded = "data/processed/yield_df_final_conso_encoded.csv"

FEATURES_PATH = "model/feature_columns.joblib"
MODEL_PATH = "model/yield_pipeline.joblib"
