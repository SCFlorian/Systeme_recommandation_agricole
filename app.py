import logging
import joblib
import pandas as pd
import uvicorn
import os
from huggingface_hub import hf_hub_download
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# On importe ta fonction de nettoyage
from scripts.data_cleaning import preparation_yield_df_inference

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title="Agritech Answers")

# ==========================================
# CHARGEMENT DYNAMIQUE DU MODÈLE
# ==========================================
def load_remote_pipeline():
    # Remplace par ton repo de modèle créé précédemment
    REPO_ID = "FLORIANSC/yield-prediction-model" 
    FILENAME = "randomforest_best_pipeline.joblib"
    
    # On vérifie si on est en local (pour tes tests) ou sur le Space
    if os.path.exists(FILENAME):
        logging.info("Chargement du modèle local.")
        return joblib.load(FILENAME)
    else:
        logging.info("Modèle local non trouvé. Téléchargement depuis le Hub...")
        token = os.getenv("HF_TOKEN")
        model_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME, token=token)
        return joblib.load(model_path)

# Chargement du pipeline au démarrage
try:
    pipeline = load_remote_pipeline()
    logging.info("Pipeline chargé avec succès.")
except Exception as e:
    logging.error(f"Erreur critique de chargement du modèle : {e}")
    pipeline = None

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


@app.get("/health")
def health_check():
    return {"status": "OK", "message": "API opérationnelle"}


@app.post("/predict")
def predict_api(data: InputPrediction):
    try:
        donnees_saisies = pd.DataFrame([data.model_dump()])

        # Feature engineering uniquement, sans encodage manuel
        donnees_preparees = preparation_yield_df_inference(input_df=donnees_saisies)

        logging.info(f"Colonnes envoyées au pipeline : {list(donnees_preparees.columns)}")

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


CROPS = [
    "Wheat", "Rice", "Maize", "Soybean", "Potatoes",
    "Sweet Potatoes", "Sorghum", "Cassava", "Yams", "Plantains and others"
]


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

            # Feature engineering uniquement
            donnees_preparees = preparation_yield_df_inference(input_df=donnees_saisies)

            prediction = pipeline.predict(donnees_preparees)[0]

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