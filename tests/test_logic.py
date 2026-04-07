import pandas as pd
import pytest
from scripts.data_cleaning import preparation_yield_df_inference

def test_preparation_inference_columns():
    # 1. On crée une donnée factice (Mock data)
    df_test = pd.DataFrame([{
        "region": "Western Europe",
        "item": "Wheat",
        "avg_temp": 15.0,
        "rainfall_mm": 500.0,
        "pesticides_tonnes": 100.0
    }])
    
    # 2. On lance la fonction
    df_result = preparation_yield_df_inference(df_test)
    
    # 3. On vérifie que le résultat n'est pas vide et contient les bonnes colonnes
    assert not df_result.empty
    assert "thermal_stress" in df_result.columns
    assert "years_from_now" in df_result.columns