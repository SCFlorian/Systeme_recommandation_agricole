# ====================================================
# Configuration du système de recommandation agricole
# ====================================================
from typing import Literal

# Chargement des fichiers csv
csv_yield_conso = "../data/processed/yield_df_final_conso.csv"
csv_yield_enriched = "../data/processed/yield_df_enriched_conso.csv"

# Région et item à avoir dans l'app
REGIONS = Literal[
    'Southern Asia', 'Southern Europe', 'Northern Africa', 'Polynesia',
    'Sub-Saharan Africa', 'Latin America and the Caribbean', 'Western Asia',
    'Australia and New Zealand', 'Western Europe', 'Eastern Europe',
    'Northern America', 'South-eastern Asia', 'Eastern Asia',
    'Northern Europe', 'Melanesia', 'Micronesia', 'Central Asia'
]

ITEMS = Literal[
    'Maize', 'Potatoes', 'Rice', 'Wheat', 'Sorghum', 'Soybean',
    'Cassava', 'Yams', 'Sweet potatoes', 'Plantains and others'
]