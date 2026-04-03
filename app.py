# ===========
# SCRIPT API
# ===========

# Librairies nécessaires
import os
import logging
import joblib
import pandas as pd
import uvicorn

from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
# Imports du projet
from scripts.config import (FEATURES_PATH,MODEL_PATH)
from scripts.data_cleaning import preparation_yield_df_inference

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Chargement de l'API
app = FastAPI(title="Agritech Answers")

# On récupère le modèle de ML 
pipeline = joblib.load(MODEL_PATH)
# Colonnes attendues par le modèle
expected_columns = joblib.load(FEATURES_PATH)


# Logging du projet
logging.info("Modèle, colonnes attendues et dataset de référence chargés avec succès.")

# Vérification Pydantic
class InputPrediction(BaseModel):
    region: str
    item: str
    avg_temp: float
    rainfall_mm: float
    pesticides_tonnes: float

class InputRecommendation(BaseModel):
    region: str
    avg_temp: float
    rainfall_mm: float
    pesticides_tonnes: float

# Alerte si erreur d'endpoint sélectionné
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error_code": 404,
            "message": "Cette route n'existe pas.",
            "detail": f"L'URL '{request.url.path}' est inconnue.",
            "suggestion": "Essayez plutôt /predict ou /health"
        }
    )

# Endpoint pour vérifier le bon fonctionnement
@app.get("/health")
def health_check():
    return {"status": "OK", "message": "API opérationnelle"}

# Endpoint pour la fonction de prédiction
@app.post("/predict")
def predict_api(data: InputPrediction):
    try:
        # Données sélectionnées par l'utilisateur
        donnees_saisies = pd.DataFrame([data.model_dump()])
        # Prétraitement des données et encodage
        donnees_preparees = preparation_yield_df_inference(
            input_df=donnees_saisies,
            expected_columns=expected_columns
        )

        logging.info(f"Colonnes finales envoyées au modèle : {list(donnees_preparees.columns)}")
        # Prédiction sur les informations de l'utilisateur
        prediction = pipeline.predict(donnees_preparees)[0]

        return {
            "prediction": float(prediction),
            "unit": "yield"
        }

    except Exception as e:
        logging.exception("Erreur pendant la prédiction")
        return JSONResponse(
            status_code=500,
            content={
                "error_code": 500,
                "message": "Erreur lors de la prédiction",
                "detail": str(e)
            }
        )
    
CROPS = ["Wheat", "Rice", "Maize", "Soybean", "Potatoes",
         "Sweet Potatoes", "Sorghum", "Cassava", "Yams", "Plantains and others"]

# Endpoint pour la fonction de recommendation
@app.post("/recommend")
def recommend_api(data: InputRecommendation):
    try:
        results = []

        for crop in CROPS:
            donnees_saisies = pd.DataFrame([{
                "region": data.region,
                "item": crop,
                "avg_temp": data.avg_temp,
                "rainfall_mm": data.rainfall_mm,
                "pesticides_tonnes": data.pesticides_tonnes
            }])
            # Données sélectionnées par l'utilisateur
            donnees_preparees = preparation_yield_df_inference(
                input_df=donnees_saisies,
                expected_columns=expected_columns
            )
            # Prétraitement des données et encodage
            prediction = pipeline.predict(donnees_preparees)[0]
            # Liste classement par type de culture
            results.append({
                "crop": crop,
                "predicted_yield": float(prediction)
            })

        results = sorted(results, key=lambda x: x["predicted_yield"], reverse=True)

        return {
            "best_crop": results[0]["crop"],
            "ranking": results
        }

    except Exception as e:
        logging.exception("Erreur pendant la recommandation")
        return JSONResponse(
            status_code=500,
            content={
                "error_code": 500,
                "message": "Erreur lors de la recommandation",
                "detail": str(e)
            }
        )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7860)